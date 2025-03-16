# Use an official Python runtime as a base image
FROM python:3.10-slim-buster

RUN apt-get update && \
    apt-get install -y --no-install-recommends curl  build-essential libpq-dev   && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN curl -sSL https://install.python-poetry.org | python3 -

ENV PATH="${PATH}:/root/.local/bin"

WORKDIR /geolocation_catalogue

COPY pyproject.toml poetry.lock .

RUN poetry config virtualenvs.create false
RUN poetry install --without=dev --no-root

COPY geolocation_catalogue geolocation_catalogue
COPY alembic alembic
COPY alembic.ini . 

COPY start.sh .
RUN chmod +x start.sh

EXPOSE 8000

CMD ["sh", "./start.sh"]