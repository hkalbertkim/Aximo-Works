#!/usr/bin/env bash
set -euo pipefail

# Load .env into env vars (safe for local dev; do NOT commit .env)
if [[ -f ".env" ]]; then
  export $(grep -v '^#' .env | xargs)
fi

# Default state = backlog (override by: STATE=todo ./intake_from_clipboard.sh)
STATE="${STATE:-backlog}"

# macOS clipboard -> stdin intake
pbpaste | python linear_cli.py intake --state "$STATE"
