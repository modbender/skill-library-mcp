#!/usr/bin/env bash
set -euo pipefail

# shelv-poll-status.sh — Poll a shelf until it reaches a terminal status
# Usage:
#   shelv-poll-status.sh <shelf-public-id>
#
# Environment:
#   SHELV_API_KEY   (required) API key from shelv.dev

SHELV_API_KEY="${SHELV_API_KEY:-}"
API_URL="https://api.shelv.dev"

SHELF_ID=""
INTERVAL=5
MAX_ATTEMPTS=120

usage() {
  cat >&2 <<'EOF'
Usage: shelv-poll-status.sh <shelf-public-id>

Polls GET /v1/shelves/{id} every 5 seconds until the shelf reaches a
terminal status (ready, review, or failed).

Exit codes:
  0   Shelf reached "ready" or "review"
  1   Shelf reached "failed" or polling timed out

Environment:
  SHELV_API_KEY   Required. Your Shelv API key.
EOF
  exit 1
}

# Parse arguments
while [ $# -gt 0 ]; do
  case "$1" in
    --help|-h)
      usage
      ;;
    -*)
      echo "Error: Unknown flag: $1" >&2
      usage
      ;;
    *)
      if [ -z "$SHELF_ID" ]; then
        SHELF_ID="$1"
      else
        echo "Error: Unexpected argument: $1" >&2
        usage
      fi
      shift
      ;;
  esac
done

if [ -z "$SHELF_ID" ]; then
  echo "Error: shelf-public-id is required" >&2
  usage
fi

if [ -z "$SHELV_API_KEY" ]; then
  echo "Error: SHELV_API_KEY environment variable is required" >&2
  echo "Get your API key at https://shelv.dev -> Settings -> API Keys" >&2
  exit 1
fi

for cmd in curl jq; do
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "Error: $cmd is required but not found" >&2
    exit 1
  fi
done

ATTEMPT=0

while true; do
  ATTEMPT=$((ATTEMPT + 1))

  if [ "$ATTEMPT" -gt "$MAX_ATTEMPTS" ]; then
    echo "Error: Timed out after $MAX_ATTEMPTS attempts ($((MAX_ATTEMPTS * INTERVAL))s)" >&2
    exit 1
  fi

  RESPONSE=$(curl -sS -w "\n%{http_code}" \
    -H "Authorization: Bearer $SHELV_API_KEY" \
    -- "$API_URL/v1/shelves/$SHELF_ID")

  HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
  BODY=$(echo "$RESPONSE" | sed '$d')

  if [ "$HTTP_CODE" != "200" ]; then
    echo "Error: API returned HTTP $HTTP_CODE" >&2
    echo "$BODY" >&2
    exit 1
  fi

  STATUS=$(echo "$BODY" | jq -r '.status')
  NAME=$(echo "$BODY" | jq -r '.name // empty')

  case "$STATUS" in
    ready)
      echo "Status: ready"
      echo "Shelf \"$NAME\" is ready."
      exit 0
      ;;
    review)
      echo "Status: review"
      echo "Shelf \"$NAME\" is in review mode. Approve or regenerate to continue."
      exit 0
      ;;
    failed)
      ERROR_MSG=$(echo "$BODY" | jq -r '.errorMessage // "Unknown error"')
      FAILED_STEP=$(echo "$BODY" | jq -r '.failedAtStep // "unknown"')
      echo "Status: failed" >&2
      echo "Shelf \"$NAME\" failed at step: $FAILED_STEP" >&2
      echo "Error: $ERROR_MSG" >&2
      exit 1
      ;;
    *)
      echo "Status: $STATUS (attempt $ATTEMPT/$MAX_ATTEMPTS)" >&2
      sleep "$INTERVAL"
      ;;
  esac
done
