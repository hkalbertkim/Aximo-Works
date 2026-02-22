#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if git diff --quiet --ignore-submodules -- && git diff --cached --quiet --ignore-submodules --; then
  echo "no changes"
  exit 0
fi

git add -A

MSG="${EOD_COMMIT_MSG:-chore: eod updates}"
if git commit -m "$MSG"; then
  echo "Committed with message: $MSG"
else
  echo "no changes"
  exit 0
fi

if [[ "${DRY_RUN:-0}" == "1" ]]; then
  echo "DRY_RUN: git push origin master"
  exit 0
fi

git push origin master
