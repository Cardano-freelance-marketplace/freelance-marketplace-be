#!/bin/bash

# Install system dependencies
echo "Installing system dependencies..."
sudo apt update
sudo apt install -y jpegoptim

# Check if Poetry is installed
if ! command -v poetry &> /dev/null; then
    echo "Poetry is not installed. Please install it first: https://python-poetry.org/docs/#installation"
    exit 1
fi

# Activate Poetry environment and start the FastAPI application
echo "Starting FastAPI application in development mode..."
poetry run uvicorn freelance_marketplace.main:app --reload --host 0.0.0.0 --port 8000 --log-level debug
