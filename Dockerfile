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

# Selenium

RUN curl -sS -o - https://dl-ssl.google.com/linux/linux_signing_key.pub | gpg --dearmor | tee /etc/apt/trusted.gpg.d/chrome.gpg \
    && bash -c "echo 'deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main' >> /etc/apt/sources.list.d/google-chrome.list" \
    && apt -y update \
    && apt -y install google-chrome-stable=136.0.7103.92-1 # for now this is pinned, i plan on making this better later :p

RUN wget https://storage.googleapis.com/chrome-for-testing-public/136.0.7103.92/linux64/chromedriver-linux64.zip \
    && unzip -j chromedriver-linux64.zip chromedriver-linux64/chromedriver -d /usr/local/bin/

# Poetry

ENV PATH="/opt/poetry/bin:$PATH" \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

COPY --from=runtime /opt/poetry /opt/poetry/

WORKDIR /app

COPY pyproject.toml poetry.lock ./
RUN touch README.md

RUN poetry install && rm -rf $POETRY_CACHE_DIR

COPY src/tibros_scraper ./tibros_scraper

ENTRYPOINT ["poetry", "run", "python", "-m", "tibros_scraper.main"]