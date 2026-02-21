#!/usr/bin/env bash
set -euo pipefail

URL="https://meeting.aximo.works/api/proxy/tasks"

# Optional local env for Cloudflare Access service token.
if [[ -f ".env.cf_access" ]]; then
  set -a
  # shellcheck disable=SC1091
  source ".env.cf_access"
  set +a
fi

tmp_headers="$(mktemp)"
tmp_body="$(mktemp)"
trap 'rm -f "$tmp_headers" "$tmp_body"' EXIT

curl_args=(-sS -D "$tmp_headers" -o "$tmp_body")
if [[ -n "${CF_ACCESS_CLIENT_ID:-}" && -n "${CF_ACCESS_CLIENT_SECRET:-}" ]]; then
  curl_args+=(
    -H "CF-Access-Client-Id: ${CF_ACCESS_CLIENT_ID}"
    -H "CF-Access-Client-Secret: ${CF_ACCESS_CLIENT_SECRET}"
  )
fi
curl "${curl_args[@]}" "$URL"

status_code="$(awk 'NR==1 {print $2}' "$tmp_headers")"
body_preview="$(head -c 200 "$tmp_body" | tr '\r\n' ' ' | tr -s ' ')"

echo "status=${status_code:-unknown}"
echo "body_preview=${body_preview}"

if [[ "${status_code:-}" != "200" ]]; then
  exit 1
fi
