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

I personally use it in combination with the provided `docker-compose.yaml` aswell as the `run_scraper.sh` file that's ran on a cron schedule. This allows me to be up-to-date if the IHK finally provided me with my results.

I use docker to keep the selenium running in its own space, aswell as only making it available to the scraper. In addition I use flock to protect against overlapping runs.

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

I would recommend that you use the provided `docker-compose.yaml` file with the example `tibros.env`.\
To make running it even easier, you can use the `run_scraper.sh`, as it keeps the Selenium Chrome container running and only removes the scraper after it has done its job.

1. Fill the `tibros.env` file with your credentials, Discord Webhook url and  Discord userid

2. Allow execution of the `run_scraper.sh` file:
   ```bash
   sudo chmod +x run_scraper.sh
   ```

3. Run the `run_scraper.sh` file:
   ```bash
   ./run_scraper.sh
   ```

4. If this is your first run, add the Discord message id to the `tibros.env` to keep that message up to date and prevent unnecessary resends.


## License

This project is licensed under the GNU GPLv3.