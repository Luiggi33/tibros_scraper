#!/bin/bash
set -euo pipefail

cd /tibros_scraper || exit 1

if ! docker compose ps --status running selenium | grep -q '^selenium'; then
  echo "selenium is not running, starting"
  docker compose up -d selenium
fi

docker compose run --rm scraper