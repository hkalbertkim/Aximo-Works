#!/usr/bin/env bash
set -euo pipefail

# Load env
export $(grep -v '^#' .env | xargs)

echo "=== AXIMO OPS RUN ==="

# 1) Optional intake from file if provided
# Usage: ./run_ops.sh intake.txt
if [[ "${1:-}" != "" && -f "$1" ]]; then
  echo "--- Intake from $1 ---"
  python linear_cli.py intake --state backlog < "$1"
fi

# 2) Post daily brief
echo "--- Posting daily brief ---"
python post_daily_brief.py

echo "=== DONE ==="
