import os
import time
import logging

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

from bs4 import BeautifulSoup

logging.basicConfig(level=logging.WARNING,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def parse_exam_results(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')

    results_table = soup.find('div', class_='noc_table')

    if not results_table:
        logging.warning("No exam results found!")
        return []

    exam_results = []

    rows = results_table.find_all('div', class_='row reihe')

    for row in rows:
        if row.find('b'):
            continue

        columns = row.find_all('div', class_=['col-xs-8', 'col-xs-2'])

        if len(columns) >= 3:
            label_col = columns[0]
            result_col = columns[1]
            note_col = columns[2]

            label = label_col.get_text(strip=True)
            points = result_col.get_text(strip=True)
            mark = note_col.get_text(strip=True)

            if label and not label_col.find('b'):
                print(f"{label} | Points: {points} | Mark: {mark}")
                exam_results.append({
                    'label': label,
                    'points': points,
                    'mark': mark
                })

    return exam_results

def get_exam_results():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (X11; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0")

    username = os.environ.get('IHK_AZUBINUMBER')
    password = os.environ.get('IHK_AZUBIPASSWORD')

    if not username or not password:
        logging.warning("No IHK username and IHK password found!")
        return []

    driver = None
    try:
        logging.info("Initializing Chrome driver")
        driver = webdriver.Chrome(options=chrome_options)

        logging.info("Navigating to login page")
        driver.get("https://apps.ihk-berlin.de/tibrosBB/BB_auszubildende.jsp")

        logging.info("Logging in")
        username_field = WebDriverWait(driver, 10).until(
            ec.presence_of_element_located((By.NAME, "login"))
        )
        password_field = driver.find_element(By.NAME, "pass")

        username_field.send_keys(username)
        password_field.send_keys(password)

        login_button = driver.find_element(By.XPATH, "//button[@name='anmelden']")
        login_button.click()

        time.sleep(2)

        logging.info("Navigating to results")

        exam_link = WebDriverWait(driver, 10).until(
            ec.presence_of_element_located((By.XPATH, "//a[contains(@href, 'azubiPruef.jsp')]"))
        )
        exam_link.click()

        results_link = WebDriverWait(driver, 10).until(
            ec.presence_of_element_located((By.XPATH, "//a[contains(@href, 'azubiErgebnisse.jsp')]"))
        )
        results_link.click()

        time.sleep(2)

        logging.info("Parsing results")
        html_content = driver.page_source
        exam_results = parse_exam_results(html_content)

        logging.info("Logging out")
        logout_link = driver.find_element(By.XPATH, "//a[contains(@href, 'logout.jsp')]")
        logout_link.click()

        return exam_results

    except Exception as e:
        logging.error(f"Error: {e}")
        return []
    finally:
        if driver:
            logging.info("Closing browser")
            driver.quit()


def main():
    try:
        logging.info("Starting script")
        results = get_exam_results()
        if results:
            logging.info(f"Successfully retrieved {len(results)} exam results")
            print("\n=== EXAM RESULTS ===")
            for result in results:
                print(f"{result['label']}: {result['points']} - {result['mark']}")
        else:
            logging.warning("No results found or an error occurred")
    except Exception as e:
        logging.error(f"Script failed: {e}")


if __name__ == "__main__":
    main()