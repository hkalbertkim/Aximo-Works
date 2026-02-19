#!/usr/bin/env bash
set -euo pipefail

TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT

SERVICE_TOKEN_PRESENT="NO"
if [[ -n "${CF_ACCESS_CLIENT_ID:-}" && -n "${CF_ACCESS_CLIENT_SECRET:-}" ]]; then
  SERVICE_TOKEN_PRESENT="YES"
fi

echo "Service token present: ${SERVICE_TOKEN_PRESENT}"
echo

LAST_CODE=""

sanitize_headers() {
  sed 's/\r$//' "$1" | head -n 12
}

run_check() {
  local name="$1"
  local method="$2"
  local url="$3"
  local auth_mode="$4"     # public|service
  local body_payload="$5"   # "" for none
  local show_snippet="$6"   # yes|no

  local slug
  slug="$(echo "$name" | tr -cs 'A-Za-z0-9' '_')"
  local hdr_file="$TMP_DIR/${slug}.headers"
  local body_file="$TMP_DIR/${slug}.body"

  local -a cmd
  cmd=(curl -sS -D "$hdr_file" -o "$body_file" -X "$method" "$url")

  if [[ "$auth_mode" == "service" ]]; then
    cmd+=( -H "CF-Access-Client-Id: ${CF_ACCESS_CLIENT_ID}" )
    cmd+=( -H "CF-Access-Client-Secret: ${CF_ACCESS_CLIENT_SECRET}" )
  fi

  if [[ -n "$body_payload" ]]; then
    cmd+=( -H "Content-Type: application/json" )
    cmd+=( --data "$body_payload" )
  fi

  "${cmd[@]}"

  local line code
  line="$(head -n 1 "$hdr_file" | tr -d '\r')"
  code="$(awk 'NR==1 {print $2}' "$hdr_file")"
  LAST_CODE="$code"

  echo "=== ${name} ==="
  echo "url: ${url}"
  echo "status: ${line}"
  echo "headers (first 12):"
  sanitize_headers "$hdr_file"

  if [[ "$show_snippet" == "yes" ]]; then
    local snippet
    snippet="$(tr '\n' ' ' < "$body_file" | cut -c1-120)"
    echo "body[0:120]: ${snippet}"
  fi

  echo
}

mark_pass_fail() {
  local label="$1"
  local pass="$2"
  if [[ "$pass" == "yes" ]]; then
    echo "${label}: PASS"
  else
    echo "${label}: FAIL"
  fi
}

# A) Public checks
run_check "A1 public GET /" "GET" "https://meeting.aximo.works/" "public" "" "no"; A1_CODE="$LAST_CODE"
run_check "A2 public GET /kanban" "GET" "https://meeting.aximo.works/kanban" "public" "" "no"; A2_CODE="$LAST_CODE"
run_check "A3 public GET /meeting" "GET" "https://meeting.aximo.works/meeting" "public" "" "no"; A3_CODE="$LAST_CODE"
run_check "A4 public GET /api/proxy/health" "GET" "https://meeting.aximo.works/api/proxy/health" "public" "" "no"; A4_CODE="$LAST_CODE"
run_check "A5 public GET /api/proxy/tasks" "GET" "https://meeting.aximo.works/api/proxy/tasks" "public" "" "no"; A5_CODE="$LAST_CODE"
run_check "A6 public POST /api/proxy/tasks" "POST" "https://meeting.aximo.works/api/proxy/tasks" "public" '{"text":"public smoke post","type":"internal_generate"}' "no"; A6_CODE="$LAST_CODE"

A1_OK="no"; [[ "$A1_CODE" == "200" || "$A1_CODE" == "302" ]] && A1_OK="yes"
A2_OK="no"; [[ "$A2_CODE" == "200" || "$A2_CODE" == "302" ]] && A2_OK="yes"
A3_OK="no"; [[ "$A3_CODE" == "200" || "$A3_CODE" == "302" ]] && A3_OK="yes"
A4_OK="no"; [[ "$A4_CODE" != "200" ]] && A4_OK="yes"
A5_OK="no"; [[ "$A5_CODE" != "200" ]] && A5_OK="yes"
A6_OK="no"; [[ "$A6_CODE" != "200" ]] && A6_OK="yes"

# B) Service-token checks (optional)
B1_OK="skip"; B2_OK="skip"; B3_OK="skip"
if [[ "$SERVICE_TOKEN_PRESENT" == "YES" ]]; then
  run_check "B1 token GET /api/proxy/health" "GET" "https://meeting.aximo.works/api/proxy/health" "service" "" "no"; B1_CODE="$LAST_CODE"
  run_check "B2 token GET /api/proxy/tasks" "GET" "https://meeting.aximo.works/api/proxy/tasks" "service" "" "yes"; B2_CODE="$LAST_CODE"
  run_check "B3 token POST /api/proxy/tasks" "POST" "https://meeting.aximo.works/api/proxy/tasks" "service" '{"text":"token smoke post","type":"internal_generate"}' "yes"; B3_CODE="$LAST_CODE"

  B1_OK="no"; [[ "$B1_CODE" == "200" ]] && B1_OK="yes"
  B2_OK="no"; [[ "$B2_CODE" == "200" ]] && B2_OK="yes"
  B3_OK="no"; [[ "$B3_CODE" == "200" ]] && B3_OK="yes"
else
  echo "Skipping B checks: missing CF_ACCESS_CLIENT_ID/CF_ACCESS_CLIENT_SECRET"
  echo
fi

# C) Local sanity
run_check "C1 local GET /api/proxy/health" "GET" "http://127.0.0.1:3000/api/proxy/health" "public" "" "no"; C1_CODE="$LAST_CODE"
run_check "C2 local GET /api/proxy/tasks" "GET" "http://127.0.0.1:3000/api/proxy/tasks" "public" "" "yes"; C2_CODE="$LAST_CODE"

C1_OK="no"; [[ "$C1_CODE" == "200" ]] && C1_OK="yes"
C2_OK="no"; [[ "$C2_CODE" == "200" ]] && C2_OK="yes"

echo "=== Checklist Summary ==="
mark_pass_fail "A1 public /" "$A1_OK"
mark_pass_fail "A2 public /kanban" "$A2_OK"
mark_pass_fail "A3 public /meeting" "$A3_OK"
mark_pass_fail "A4 public /api/proxy/health not 200" "$A4_OK"
mark_pass_fail "A5 public /api/proxy/tasks not 200" "$A5_OK"
mark_pass_fail "A6 public POST /api/proxy/tasks not 200" "$A6_OK"

if [[ "$B1_OK" == "skip" ]]; then
  echo "B1 token /api/proxy/health: SKIP"
  echo "B2 token /api/proxy/tasks: SKIP"
  echo "B3 token POST /api/proxy/tasks: SKIP"
else
  mark_pass_fail "B1 token /api/proxy/health" "$B1_OK"
  mark_pass_fail "B2 token /api/proxy/tasks" "$B2_OK"
  mark_pass_fail "B3 token POST /api/proxy/tasks" "$B3_OK"
fi

mark_pass_fail "C1 local /api/proxy/health" "$C1_OK"
mark_pass_fail "C2 local /api/proxy/tasks" "$C2_OK"

SAFE_TO_SHARE="NO"
if [[ "$A1_OK" == "yes" && "$A2_OK" == "yes" && "$A3_OK" == "yes" && "$A4_OK" == "yes" && "$A5_OK" == "yes" && "$A6_OK" == "yes" ]]; then
  SAFE_TO_SHARE="YES"
fi

echo "SAFE_TO_SHARE=${SAFE_TO_SHARE}"
