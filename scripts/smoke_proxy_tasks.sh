#!/usr/bin/env bash
set -euo pipefail

URL="https://meeting.aximo.works/api/proxy/tasks"

tmp_headers="$(mktemp)"
tmp_body="$(mktemp)"
trap 'rm -f "$tmp_headers" "$tmp_body"' EXIT

curl -sS -D "$tmp_headers" -o "$tmp_body" "$URL"

status_code="$(awk 'NR==1 {print $2}' "$tmp_headers")"
body_preview="$(head -c 200 "$tmp_body" | tr '\n' ' ')"

echo "status=${status_code:-unknown}"
echo "body_preview=${body_preview}"

if [[ "${status_code:-}" != "200" ]]; then
  exit 1
fi
