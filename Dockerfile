FROM python:3.12-bookworm AS production-image

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

WORKDIR /app

COPY pyproject.toml poetry.lock ./
COPY README.md ./
COPY src ./src
RUN python -m pip install --no-cache-dir .

ENTRYPOINT ["python", "-m", "tibros_scraper.main"]