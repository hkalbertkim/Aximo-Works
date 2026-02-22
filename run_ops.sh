#!/usr/bin/env bash
set -euo pipefail

# Load env
export $(grep -v '^#' .env | xargs)

DRY_RUN="${DRY_RUN:-0}"

echo "=== AXIMO OPS RUN ==="

# 1) Optional intake from file if provided
# Usage: ./run_ops.sh intake.txt
if [[ "${1:-}" != "" && -f "$1" ]]; then
  echo "--- Intake from $1 ---"
  if [[ "$DRY_RUN" == "1" ]]; then
    echo "DRY_RUN: python3 linear_cli.py intake --state backlog < $1"
  else
    python3 linear_cli.py intake --state backlog < "$1"
  fi
fi

# 2) Post daily brief (existing behavior)
echo "--- Posting daily brief ---"
if [[ "$DRY_RUN" == "1" ]]; then
  echo "DRY_RUN: python3 post_daily_brief.py"
else
  python3 post_daily_brief.py
fi

# 3) Email report
export EOD_STATUS_NOTE="EOD: daily brief generated; email send attempted; commit/push pending"
echo "--- Sending EOD email report ---"
python3 scripts/eod_send_report_email.py

# 4) Linear update
echo "--- Posting EOD Linear update ---"
python3 scripts/eod_linear_update.py

# 5) Commit + push
echo "--- EOD commit + push ---"
bash scripts/eod_commit_push.sh

echo "=== DONE ==="
