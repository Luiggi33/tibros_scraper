# tibros scraper

tibros scraper is a Python-based tool designed to scrape and parse exam results from the IHK platform (https://apps.ihk-berlin.de). It uses Selenium for browser automation and BeautifulSoup for HTML parsing.

## Installation

1. Clone the repository:
   ```bash
   git clone git@github.com:Luiggi33/tibros_scraper.git
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
   export DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/.../..."
   # Optional: set this after the first successful send to edit the same message later.
   export DISCORD_WEBHOOK_MESSAGE_ID="123456789012345678"
   ```

## Usage

Run the scraper using the following command:
```bash
poetry run tibros_scraper
```
This script will automatically log you in, fetch your exam results, and send them to a Discord webhook as a single embed. If `DISCORD_WEBHOOK_MESSAGE_ID` is set, the existing message will be edited instead of creating a new one.

Or run directly without Poetry:
```bash
python -m tibros_scraper.main
```

The Discord message uses the exam label as the field name and combines points and mark in the field value.

## Testing

Run the tests using Pytest:
```bash
poetry run pytest -v
```

## Docker Support

The recommended container setup runs the scraper and a Selenium Chrome container together.

1. Set the required environment variables:
   ```bash
   export IHK_AZUBINUMBER="your_username"
   export IHK_AZUBIPASSWORD="your_password"
   export DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/.../..."
   export DISCORD_WEBHOOK_MESSAGE_ID="123456789012345678"
   ```

2. Start both containers:
   ```bash
   docker compose up --build
   ```

   The scraper container connects to the Selenium container through `SELENIUM_REMOTE_URL=http://selenium:4444`.

If you run the scraper image against a Selenium service of your own, set `SELENIUM_REMOTE_URL` to that service's address. Outside Docker, if `SELENIUM_REMOTE_URL` is not set, the scraper falls back to a local Chrome driver.

## License

This project is licensed under the GNU GPLv3.