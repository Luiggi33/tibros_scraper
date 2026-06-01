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

You can also build and run the scraper using Docker:

1. Build the Docker image:
   ```bash
   docker build -t tibros-scraper .
   ```

2. Run the container:
   ```bash
   docker run \
     -e IHK_AZUBINUMBER="your_username" \
     -e IHK_AZUBIPASSWORD="your_password" \
     -e DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/.../..." \
     -e DISCORD_WEBHOOK_MESSAGE_ID="123456789012345678" \
     tibros-scraper
   ```

   The `DISCORD_WEBHOOK_MESSAGE_ID` variable is optional; omit it if you want the webhook to create a new message each run.

## License

This project is licensed under the GNU GPLv3.