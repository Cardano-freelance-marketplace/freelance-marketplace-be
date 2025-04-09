FROM python:3.12-alpine3.19 as builder

# Set environment variables for Poetry
ENV POETRY_VERSION=2.0.1
ENV POETRY_HOME="/opt/poetry"
ENV PATH="$POETRY_HOME/bin:$PATH"

# Timeout in seconds
ENV PIP_DEFAULT_TIMEOUT=10000
ENV POETRY_HTTP_TIMEOUT=10000

# Install Poetry and other dependencies
RUN apk update && apk add curl openssh-client git && \
    curl -sSL https://install.python-poetry.org | python3 - && \
    $POETRY_HOME/bin/poetry config virtualenvs.create false

# Install prerequisites
RUN apk add --no-cache \
  curl \
  git \
  build-base \
  libffi-dev \
  python3-dev \
  py3-pip \
  py3-setuptools \
  py3-wheel \
  musl-dev \
  openssl-dev \
  postgresql-dev \
  libpq

# Clean up unnecessary files
RUN rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy pyproject.toml and poetry.lock
COPY pyproject.toml ./
COPY poetry.lock ./

RUN poetry install --no-root

COPY . .

EXPOSE 8000


# Start the app
CMD ["poetry", "run", "uvicorn", "freelance_marketplace.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000", "--log-level", "debug"]