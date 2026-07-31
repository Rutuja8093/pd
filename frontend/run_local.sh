#!/usr/bin/env bash
# Starts the React frontend for local development.
set -e
cd "$(dirname "$0")"

if command -v yarn >/dev/null 2>&1; then
  yarn install
  yarn start
else
  npm install
  npm start
fi
