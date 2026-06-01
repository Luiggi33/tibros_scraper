import json
import logging
import os
import hashlib
import time
from pathlib import Path
from datetime import datetime, timezone
from urllib.parse import urlencode, urlsplit, urlunsplit
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

IHK_RESULTS_URL = "https://apps.ihk-berlin.de/tibrosBB/BB_auszubildende.jsp"
DISCORD_EMBED_COLOR = 5793266


def current_timestamp():
    return datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z')


def build_exam_field_value(result):
    return f"Points: {result['points']}\nMark: {result['mark']}"


def build_discord_payload(exam_results, timestamp=None, content=None, allowed_mentions=None):
    embed_fields = [
        {
            'name': result['label'],
            'value': build_exam_field_value(result),
            'inline': True,
        }
        for result in exam_results
    ]

    payload = {
        'embeds': [
            {
                'title': 'IHK Berlin | Prüfungsnoten',
                'url': IHK_RESULTS_URL,
                'color': DISCORD_EMBED_COLOR,
                'timestamp': timestamp or current_timestamp(),
                'fields': embed_fields,
            }
        ]
    }

    if content:
        payload['content'] = content

    if allowed_mentions:
        payload['allowed_mentions'] = allowed_mentions

    return payload


def build_discord_ping_payload(discord_user_id, message=None):
    ping_message = message or 'Grades changed on IHK Berlin.'

    return {
        'content': f'<@{discord_user_id}> {ping_message}',
        'allowed_mentions': {
            'users': [discord_user_id],
        },
    }


def normalize_exam_results(exam_results):
    return [
        {
            'label': result['label'],
            'points': result['points'],
            'mark': result['mark'],
        }
        for result in sorted(exam_results, key=lambda result: (result['label'], result['points'], result['mark']))
    ]


def hash_exam_results(exam_results):
    normalized_results = normalize_exam_results(exam_results)
    encoded_results = json.dumps(normalized_results, ensure_ascii=False, separators=(',', ':')).encode('utf-8')
    return hashlib.sha256(encoded_results).hexdigest()


def load_grade_hash(snapshot_path):
    try:
        with open(snapshot_path, 'r', encoding='utf-8') as snapshot_file:
            snapshot = snapshot_file.read().strip()

        if snapshot:
            return snapshot

    except FileNotFoundError:
        return None
    except (OSError, json.JSONDecodeError) as error:
        logging.warning('Could not read grade snapshot from %s: %s', snapshot_path, error)

    return None


def save_grade_hash(snapshot_path, exam_results):
    snapshot_file = Path(snapshot_path)
    snapshot_file.parent.mkdir(parents=True, exist_ok=True)
    snapshot_file.write_text(hash_exam_results(exam_results), encoding='utf-8')


def grades_changed(previous_results, current_results):
    return previous_results != hash_exam_results(current_results)


def webhook_delivery_succeeded(response):
    return bool(response['payload'].get('id') or response['body_text'])


def build_webhook_request_url(webhook_url, message_id=None):
    parsed_url = urlsplit(webhook_url.rstrip('/'))
    query_params = {'wait': 'true'}

    if parsed_url.query:
        query_params.update(dict(item.split('=', 1) for item in parsed_url.query.split('&') if '=' in item))

    path = parsed_url.path.rstrip('/')

    if message_id:
        path = f"{path}/messages/{message_id}"

    return urlunsplit((parsed_url.scheme, parsed_url.netloc, path, urlencode(query_params), ''))


def build_chrome_options():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (X11; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0")

    chrome_binary_location = os.environ.get('CHROME_BINARY_LOCATION')
    if chrome_binary_location:
        chrome_options.binary_location = chrome_binary_location

    return chrome_options


def create_webdriver():
    chrome_options = build_chrome_options()
    remote_url = os.environ.get('SELENIUM_REMOTE_URL')

    if remote_url:
        logging.info('Using remote Selenium WebDriver at %s', remote_url)
        return webdriver.Remote(command_executor=remote_url, options=chrome_options)

    chromedriver_path = os.environ.get('CHROMEDRIVER_PATH')
    chrome_service = Service(chromedriver_path) if chromedriver_path else None

    if chrome_service:
        return webdriver.Chrome(service=chrome_service, options=chrome_options)

    return webdriver.Chrome(options=chrome_options)


def send_discord_webhook(webhook_url, payload, message_id=None):
    target_url = build_webhook_request_url(webhook_url, message_id)
    method = 'POST'

    if message_id:
        method = 'PATCH'

    request = Request(
        target_url,
        data=json.dumps(payload).encode('utf-8'),
        headers={
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) tibros_scraper/0.1',
        },
        method=method,
    )

    try:
        with urlopen(request, timeout=30) as response:
            response_body = response.read().decode('utf-8')
            return {
                'status_code': response.getcode(),
                'payload': json.loads(response_body) if response_body else {},
                'body_text': response_body,
            }
    except HTTPError as error:
        error_body = error.read().decode('utf-8', errors='replace')
        logging.error('Discord webhook request failed with status %s: %s', error.code, error_body)
    except URLError as error:
        logging.error('Discord webhook request failed: %s', error)

    return {'status_code': None, 'payload': {}, 'body_text': ''}


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
                logging.debug(f"{label} | Points: {points} | Mark: {mark}")
                exam_results.append({
                    'label': label,
                    'points': points,
                    'mark': mark
                })

    return exam_results


def get_exam_results():
    username = os.environ.get('IHK_AZUBINUMBER')
    password = os.environ.get('IHK_AZUBIPASSWORD')

    if not username or not password:
        logging.warning("No IHK username and IHK password found!")
        return []

    driver = None
    try:
        logging.info("Initializing Chrome driver")
        driver = create_webdriver()

        logging.info("Navigating to login page")
        driver.get(IHK_RESULTS_URL)

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

            grade_hash_path = os.environ.get('TIBROS_SCRAPER_STATE_PATH')
            previous_results = load_grade_hash(grade_hash_path)

            if previous_results is not None and not grades_changed(previous_results, results):
                logging.info('No grade changes detected; skipping Discord notification')
                return

            webhook_url = os.environ.get('DISCORD_WEBHOOK_URL')
            discord_user_id = os.environ.get('DISCORD_USER_ID')

            if webhook_url:
                embed_payload = build_discord_payload(results)
                embed_response = send_discord_webhook(webhook_url, embed_payload, os.environ.get('DISCORD_WEBHOOK_MESSAGE_ID'))
                ping_response = {'payload': {}, 'body_text': ''}

                if discord_user_id:
                    ping_payload = build_discord_ping_payload(discord_user_id)
                    ping_response = send_discord_webhook(webhook_url, ping_payload)

                if not webhook_delivery_succeeded(embed_response) and (discord_user_id and not webhook_delivery_succeeded(ping_response)):
                    logging.warning('Discord webhook delivery failed')
                else:
                    if webhook_delivery_succeeded(embed_response):
                        logging.info('Discord embed updated successfully')
                    else:
                        logging.warning('Discord embed update failed')

                    if webhook_delivery_succeeded(ping_response):
                        logging.info('Discord ping sent successfully')
                    else:
                        logging.warning('Discord ping delivery failed')

                save_grade_hash(grade_hash_path, results)
            else:
                logging.warning('DISCORD_WEBHOOK_URL is not set; skipping Discord delivery')
        else:
            logging.warning("No results found or an error occurred")
    except Exception as e:
        logging.error(f"Script failed: {e}")

if __name__ == "__main__":
    main()