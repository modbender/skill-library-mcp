#!/bin/bash
# Astrology API helper script
# Usage: astro-api.sh <METHOD> <endpoint> [json-body]
#
# Examples:
#   astro-api.sh GET /api/v3/data/now
#   astro-api.sh POST /api/v3/charts/natal '{"subject":{...}}'
#   astro-api.sh GET /api/v3/glossary/house-systems
#
# Environment:
#   ASTROLOGY_API_KEY - Required. Bearer token for authentication.
#   ASTROLOGY_API_URL - Optional. Base URL (default: https://api.astrology-api.io)

set -euo pipefail

BASE_URL="${ASTROLOGY_API_URL:-https://api.astrology-api.io}"

if [ -z "${ASTROLOGY_API_KEY:-}" ]; then
  echo "Error: ASTROLOGY_API_KEY environment variable is not set." >&2
  echo "Set it with: export ASTROLOGY_API_KEY=\"your_token_here\"" >&2
  exit 1
fi

if [ $# -lt 2 ]; then
  echo "Usage: astro-api.sh <METHOD> <endpoint> [json-body]" >&2
  echo "  METHOD: GET or POST" >&2
  echo "  endpoint: API path (e.g., /api/v3/charts/natal)" >&2
  echo "  json-body: JSON request body (required for POST)" >&2
  exit 1
fi

METHOD="$1"
ENDPOINT="$2"
BODY="${3:-}"

if [ "$METHOD" = "GET" ]; then
  curl -s -X GET "${BASE_URL}${ENDPOINT}" \
    -H "Authorization: Bearer ${ASTROLOGY_API_KEY}" \
    -H "Accept: application/json"
elif [ "$METHOD" = "POST" ]; then
  if [ -z "$BODY" ]; then
    echo "Error: POST requests require a JSON body as the third argument." >&2
    exit 1
  fi
  curl -s -X POST "${BASE_URL}${ENDPOINT}" \
    -H "Authorization: Bearer ${ASTROLOGY_API_KEY}" \
    -H "Content-Type: application/json" \
    -H "Accept: application/json" \
    -d "$BODY"
else
  echo "Error: Unsupported method '$METHOD'. Use GET or POST." >&2
  exit 1
fi
