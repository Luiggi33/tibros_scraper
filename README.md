# tibros scraper

tibros scraper is a Python-based tool designed to scrape and parse exam results from the IHK platform (https://apps.ihk-berlin.de). It uses Selenium for browser automation and BeautifulSoup for HTML parsing.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/tibros-scraper.git
   cd tibros-scraper
   ```

2. Install dependencies using Poetry:
   ```bash
   poetry install
   ```

3. Set up your environment variables:
   ```bash
   export IHK_AZUBINUMBER="your_username"
   export IHK_AZUBIPASSWORD="your_password"
   ```

## Usage

Run the scraper using the following command:
```bash
poetry run tibros_scraper
```

This script will automatically log you in, fetch your exam results and display them inside the console. Further automation is soon to follow

### Example Output
```
=== EXAM RESULTS ===
Einrichten eines IT-gestützten Arbeitsplatzes: 85 - 2.0
Konzeption und Administration von IT-Systemen: 92 - 1.0
```

## Testing

Run the tests using Pytest:
```bash
poetry run pytest -v
```

## Docker Support

You can also build and run the scraper using Docker:

1. Build the Docker image:
   ```bash
   docker build -t tibros-scraper .
   ```

2. Run the container:
   ```bash
   docker run -e IHK_AZUBINUMBER="your_username" -e IHK_AZUBIPASSWORD="your_password" tibros-scraper
   ```

## License

This project is licensed under the GNU GPLv3.