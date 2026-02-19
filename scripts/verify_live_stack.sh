#!/usr/bin/env bash
set -euo pipefail

BASE_URL="https://meeting.aximo.works/api/proxy"

if [[ -z "${CF_ACCESS_CLIENT_ID:-}" || -z "${CF_ACCESS_CLIENT_SECRET:-}" ]]; then
  echo "Missing required env vars. Export: CF_ACCESS_CLIENT_ID and CF_ACCESS_CLIENT_SECRET"
  exit 1
fi

TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT

print_result() {
  local name="$1"
  local endpoint="$2"
  local hdr_file="$3"
  local body_file="$4"

  echo "=== ${name} ==="
  echo "endpoint: ${endpoint}"
  echo "status: $(head -n 1 "$hdr_file" | tr -d '\r')"
  echo "headers (first 12):"
  sed 's/\r$//' "$hdr_file" | head -n 12

  if [[ "$name" == "POST /tasks" ]]; then
    local snippet
    snippet="$(tr -d '\n' < "$body_file" | cut -c1-200)"
    echo "body snippet: ${snippet}"
  fi

  echo
}

run_check() {
  local name="$1"
  local method="$2"
  local endpoint="$3"
  local body="${4:-}"

  local hdr_file="$TMP_DIR/${name//[^a-zA-Z0-9]/_}.headers"
  local body_file="$TMP_DIR/${name//[^a-zA-Z0-9]/_}.body"

  if [[ "$method" == "GET" ]]; then
    curl -sS -D "$hdr_file" -o "$body_file" \
      -H "CF-Access-Client-Id: ${CF_ACCESS_CLIENT_ID}" \
      -H "CF-Access-Client-Secret: ${CF_ACCESS_CLIENT_SECRET}" \
      "$endpoint"
  else
    curl -sS -D "$hdr_file" -o "$body_file" \
      -H "CF-Access-Client-Id: ${CF_ACCESS_CLIENT_ID}" \
      -H "CF-Access-Client-Secret: ${CF_ACCESS_CLIENT_SECRET}" \
      -H "Content-Type: application/json" \
      -X "$method" \
      --data "$body" \
      "$endpoint"
  fi

  print_result "$name" "$endpoint" "$hdr_file" "$body_file"
}

run_check "GET /health" "GET" "${BASE_URL}/health"
run_check "GET /tasks" "GET" "${BASE_URL}/tasks"
run_check "POST /tasks" "POST" "${BASE_URL}/tasks" '{"text":"POST smoke test from verify script","type":"internal_generate"}'
