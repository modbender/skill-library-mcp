#!/usr/bin/env bash
#
# BitSkins API helper script
# Usage: bash bitskins-api.sh <METHOD> <PATH> [JSON_BODY]
#
# Environment variables:
#   BITSKINS_API_KEY - Required. Your BitSkins API key.
#
# Examples:
#   bash bitskins-api.sh GET /account/profile/me
#   bash bitskins-api.sh POST /account/profile/balance
#   bash bitskins-api.sh POST /market/search/730 '{"limit":10,"offset":0,"where":{}}'

set -euo pipefail

BASE_URL="https://api.bitskins.com"

if [ -z "${BITSKINS_API_KEY:-}" ]; then
  echo "Error: BITSKINS_API_KEY environment variable is not set." >&2
  echo "Set it with: export BITSKINS_API_KEY=your_api_key_here" >&2
  exit 1
fi

METHOD="${1:?Usage: bitskins-api.sh <METHOD> <PATH> [JSON_BODY]}"
PATH_ARG="${2:?Usage: bitskins-api.sh <METHOD> <PATH> [JSON_BODY]}"
BODY="${3:-}"

METHOD_UPPER=$(echo "$METHOD" | tr '[:lower:]' '[:upper:]')

CURL_ARGS=(
  -s
  -X "$METHOD_UPPER"
  -H "x-apikey: $BITSKINS_API_KEY"
  -H "Content-Type: application/json"
  -H "Accept: application/json"
  -w "\n%{http_code}"
  "${BASE_URL}${PATH_ARG}"
)

if [ -n "$BODY" ] && [ "$METHOD_UPPER" != "GET" ]; then
  CURL_ARGS+=(-d "$BODY")
fi

RESPONSE=$(curl "${CURL_ARGS[@]}")

HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY_RESPONSE=$(echo "$RESPONSE" | sed '$d')

if [ "$HTTP_CODE" -ge 400 ] 2>/dev/null; then
  echo "HTTP $HTTP_CODE Error:" >&2
  echo "$BODY_RESPONSE" | jq . 2>/dev/null || echo "$BODY_RESPONSE" >&2
  exit 1
fi

echo "$BODY_RESPONSE" | jq . 2>/dev/null || echo "$BODY_RESPONSE"
