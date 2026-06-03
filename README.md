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
   # Optional: override the user mention that gets pinged on grade changes.
   export DISCORD_USER_ID="123123123123123123"
   # Optional: persist the last seen grade hash somewhere stable. Keep it inside the data folder.
   export TIBROS_SCRAPER_STATE_PATH="/data/tibros-grades.json"
   ```

## Usage

Run the scraper using the following command:
```bash
poetry run tibros_scraper
```
This script will automatically log you in, fetch your exam results, compare them with the last saved snapshot, and send a Discord message that mentions the configured user when the grades change.
When a change is detected, it updates the embed and also sends a separate ping message.

Or run directly without Poetry:
```bash
python -m tibros_scraper.main
```

I personally use it with a cron job like this, to produce logs aswell as flock to prevent overlap:
```bash
*/30 * * * * flock -n /tmp/tibros_scraper.lock /tibros_scraper/run_scraper.sh >> /var/log/tibros_scraper.log 2>&1
```

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
   export DISCORD_USER_ID="367690502432227329"
   ```

   If you want change detection to survive container restarts, mount a volume and point `TIBROS_SCRAPER_STATE_PATH` at a file inside it.

2. Start both containers:
   ```bash
   docker compose up --build
   ```

   The scraper container connects to the Selenium container through `SELENIUM_REMOTE_URL=http://selenium:4444`.

If you run the scraper image against a Selenium service of your own, set `SELENIUM_REMOTE_URL` to that service's address. Outside Docker, if `SELENIUM_REMOTE_URL` is not set, the scraper falls back to a local Chrome driver.

## License

This project is licensed under the GNU GPLv3.