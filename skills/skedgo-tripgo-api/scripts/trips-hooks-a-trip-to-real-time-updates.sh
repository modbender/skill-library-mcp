#!/bin/bash
# Hook a Trip to Real-Time Updates
# POST /trip/hook/{id}

set -euo pipefail

# Configuration
TRIPGO_API_KEY="${TRIPGO_API_KEY:-your-api-key-here}"
BASE_URL="${TRIPGO_BASE_URL:-https://api.tripgo.com/v1}"
TRIPGO_WEBHOOK_ALLOWLIST="${TRIPGO_WEBHOOK_ALLOWLIST:-}"
TRIPGO_ALLOW_UNSAFE_WEBHOOK="${TRIPGO_ALLOW_UNSAFE_WEBHOOK:-false}"

urlencode() {
  jq -nr --arg v "$1" '$v|@uri'
}

trim() {
  local s="$1"
  s="${s#${s%%[![:space:]]*}}"
  s="${s%${s##*[![:space:]]}}"
  printf '%s' "$s"
}

extract_https_host() {
  jq -nr --arg u "$1" '$u|capture("^https://(?<host>[^/:?#]+)").host' 2>/dev/null || true
}

host_allowed() {
  local host="$1"
  local allow_csv="$2"
  local entry
  IFS=',' read -r -a items <<<"$allow_csv"
  for entry in "${items[@]}"; do
    entry="$(trim "$entry")"
    [[ -z "$entry" ]] && continue
    if [[ "$host" == "$entry" || "$host" == *".$entry" ]]; then
      return 0
    fi
  done
  return 1
}

# Check if required parameters are provided
if [[ $# -lt 2 ]]; then
    echo "Usage: $0 <hook-url-id> <webhook-url> [headers-json]"
    echo "Example: $0 abc123def456 https://example.com/callback '{\"x-auth\":\"token\"}'"
    echo ""
    echo "Security defaults:"
    echo "  - webhook URL must be https://"
    echo "  - domain must match TRIPGO_WEBHOOK_ALLOWLIST unless TRIPGO_ALLOW_UNSAFE_WEBHOOK=true"
    echo ""
    echo "Note: Use the hookURL from the original trip response"
    exit 1
fi

TRIP_ID="$1"
WEBHOOK_URL="$2"
HEADERS='{}'
if [[ $# -ge 3 ]]; then
  HEADERS="$3"
fi

if ! jq -e . >/dev/null 2>&1 <<<"$HEADERS"; then
  echo "Error: headers-json must be valid JSON"
  exit 1
fi

if [[ ! "$WEBHOOK_URL" =~ ^https:// ]]; then
  echo "Error: webhook-url must use https://"
  exit 1
fi

WEBHOOK_HOST="$(extract_https_host "$WEBHOOK_URL")"
if [[ -z "$WEBHOOK_HOST" ]]; then
  echo "Error: unable to parse webhook host from URL"
  exit 1
fi

if [[ "$TRIPGO_ALLOW_UNSAFE_WEBHOOK" != "true" ]]; then
  if [[ -z "$TRIPGO_WEBHOOK_ALLOWLIST" ]]; then
    echo "Error: TRIPGO_WEBHOOK_ALLOWLIST is required unless TRIPGO_ALLOW_UNSAFE_WEBHOOK=true"
    echo "Example: export TRIPGO_WEBHOOK_ALLOWLIST='example.com,webhooks.example.org'"
    exit 1
  fi

  if ! host_allowed "$WEBHOOK_HOST" "$TRIPGO_WEBHOOK_ALLOWLIST"; then
    echo "Error: webhook host '$WEBHOOK_HOST' is not in TRIPGO_WEBHOOK_ALLOWLIST"
    exit 1
  fi
fi

BODY=$(jq -n \
  --arg url "$WEBHOOK_URL" \
  --argjson headers "$HEADERS" \
  '{url: $url, headers: $headers}')

TRIP_ID_ENC="$(urlencode "$TRIP_ID")"

# Make the request
curl -s -X POST "${BASE_URL}/trip/hook/${TRIP_ID_ENC}" \
    -H "X-TripGo-Key: ${TRIPGO_API_KEY}" \
    -H "Content-Type: application/json" \
    -H "Accept: application/json" \
    -d "$BODY" | jq '.'
