#!/usr/bin/env bash
#
# gd-api.sh - Base helper for GoDaddy API calls
#
set -euo pipefail

: "${GODADDY_API_BASE_URL:?Set GODADDY_API_BASE_URL}"
: "${GODADDY_API_KEY:?Set GODADDY_API_KEY}"
: "${GODADDY_API_SECRET:?Set GODADDY_API_SECRET}"

gd_api() {
  local method="$1" path="$2" body="${3:-}"
  
  if [[ -n "$body" ]]; then
    curl -sS -X "$method" "${GODADDY_API_BASE_URL}${path}" \
      -H "Authorization: sso-key ${GODADDY_API_KEY}:${GODADDY_API_SECRET}" \
      -H "Accept: application/json" \
      -H "Content-Type: application/json" \
      --data "$body"
  else
    curl -sS -X "$method" "${GODADDY_API_BASE_URL}${path}" \
      -H "Authorization: sso-key ${GODADDY_API_KEY}:${GODADDY_API_SECRET}" \
      -H "Accept: application/json"
  fi
}

# Export for use by other scripts
export -f gd_api
