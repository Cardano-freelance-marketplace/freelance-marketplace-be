#!/bin/bash

# Check if Poetry is installed
if ! command -v poetry &> /dev/null; then
    echo "Poetry is not installed. Please install it first: https://python-poetry.org/docs/#installation"
    exit 1
fi

# Activate Poetry environment and start the FastAPI application
echo "Starting FastAPI application in development mode..."
poetry run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000 --log-level debug
