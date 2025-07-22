# pull official base image
FROM python:3.12-slim-bookworm
RUN groupadd -r app && useradd --no-log-init -r -g app app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV VENV_PATH="/app/.venv"
ENV PATH="$VENV_PATH/bin:$PATH"

# install system dependencies
RUN apt-get update \
  && apt-get -y --no-install-recommends install curl gcc postgresql-client libpq-dev \
  && apt-get clean

# install python dependencies
RUN pip install --upgrade pip poetry
# set working directory
WORKDIR /app
COPY ./poetry.lock ./pyproject.toml ./
ENV POETRY_HTTP_BASIC_WEPOSITIVE_AWS_USERNAME=aws
RUN mkdir .venv
RUN --mount=type=secret,id=pypi-token,env=POETRY_HTTP_BASIC_WEPOSITIVE_AWS_PASSWORD poetry install --only main --no-root
COPY . .
RUN --mount=type=secret,id=pypi-token,env=POETRY_HTTP_BASIC_WEPOSITIVE_AWS_PASSWORD poetry install

USER app
CMD ["./.venv/bin/serve","prod"]
