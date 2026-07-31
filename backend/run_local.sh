#!/usr/bin/env bash
# Starts the FastAPI backend for local development.
set -e
cd "$(dirname "$0")"

if [ ! -d "venv" ]; then
  echo "Creating virtual environment..."
  python3 -m venv venv
fi

source venv/bin/activate
echo "Installing backend dependencies (this can take a while, it includes torch)..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Starting FastAPI on http://localhost:8001 ..."
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
