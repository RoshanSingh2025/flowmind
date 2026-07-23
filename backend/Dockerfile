# syntax=docker/dockerfile:1

FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_HOME="/opt/poetry" \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    PATH="/opt/poetry/bin:$PATH"

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl build-essential libpq-dev \
    && curl -sSL https://install.python-poetry.org | python3 - \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY pyproject.toml ./

# ---------------------------------------------------------------------------
# development target — installs dev deps, mounts source via docker-compose
# ---------------------------------------------------------------------------
FROM base AS development
RUN poetry install --no-root --no-interaction
COPY . .
EXPOSE 8000
CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# ---------------------------------------------------------------------------
# production target — deps only, no dev tools, non-root user
# ---------------------------------------------------------------------------
FROM base AS production
RUN poetry install --no-root --no-interaction --only main \
    && addgroup --system flowmind && adduser --system --ingroup flowmind flowmind
COPY . .
RUN chown -R flowmind:flowmind /app
USER flowmind
EXPOSE 8000
CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
