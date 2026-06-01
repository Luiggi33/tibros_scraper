FROM python:3.12-slim-bookworm AS runtime

ENV PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_VERSION=2.1.3 \
    POETRY_HOME="/opt/poetry"

RUN apt-get update \
    && apt-get install --no-install-recommends -y \
        build-essential

RUN python -m venv ${POETRY_HOME}
RUN ${POETRY_HOME}/bin/pip install -U pip setuptools
RUN ${POETRY_HOME}/bin/pip install "poetry==${POETRY_VERSION}"


FROM python:3.12-bookworm AS production-image

ENV SE_AVOID_STATS=true

# Selenium
## Install Chrome and chromedriver (ensure required tools present)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        chromium \
        chromium-driver \
        ca-certificates \
        wget \
        unzip \
        fonts-liberation \
        libnss3 \
        libatk1.0-0 \
        libatk-bridge2.0-0 \
        libx11-xcb1 \
        libxcb1 \
        libxcomposite1 \
        libxcursor1 \
        libxdamage1 \
        libxrandr2 \
        libgbm1 \
        libasound2 \
        libpangocairo-1.0-0 \
        libgtk-3-0 \
        libxss1 \
    && rm -rf /var/lib/apt/lists/*

## Chromedriver is not preinstalled; Selenium Manager will fetch the correct driver at runtime

WORKDIR /app

ENV CHROME_BINARY_LOCATION=/usr/bin/chromium \
    CHROMEDRIVER_PATH=/usr/bin/chromedriver

# Install package and dependencies via pip directly from pyproject
COPY pyproject.toml poetry.lock ./
COPY README.md ./
COPY src ./src
RUN python -m pip install --no-cache-dir .

ENTRYPOINT ["python", "-m", "tibros_scraper.main"]