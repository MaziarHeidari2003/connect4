FROM python:3.12-slim AS base

WORKDIR /app

RUN apt-get update && apt-get install -y \
    curl build-essential libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

ENV POETRY_VERSION=1.8.3
RUN curl -sSL https://install.python-poetry.org | python3 - --version $POETRY_VERSION
ENV PATH="/root/.local/bin:$PATH"

RUN poetry config virtualenvs.create false

COPY pyproject.toml poetry.lock ./

RUN poetry install --no-root --no-interaction --no-ansi

COPY . .

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]

CMD ["poetry", "run", "python", "-m", "app.main"]
