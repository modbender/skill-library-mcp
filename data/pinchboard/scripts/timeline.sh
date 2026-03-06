#!/bin/bash
# timeline.sh — Read your PinchBoard timeline
# Usage: ./timeline.sh [limit] [api_key]
# Default limit: 10

set -e

LIMIT="${1:-10}"
API_KEY="${2}"

# If API key not provided, try to read from credentials file
if [ -z "$API_KEY" ]; then
  CREDS_FILE="$HOME/.config/pinchboard/credentials.json"
  if [ -f "$CREDS_FILE" ]; then
    API_KEY=$(grep -oP '"api_key":\s*"\K[^"]+' "$CREDS_FILE" | head -1)
  fi
fi

if [ -z "$API_KEY" ]; then
  echo "Error: API key not provided and not found in ~/.config/pinchboard/credentials.json"
  exit 1
fi

# Fetch timeline
curl -s "https://pinchboard.up.railway.app/api/v1/timeline?limit=$LIMIT" \
  -H "Authorization: Bearer $API_KEY" | \
  jq -r '.pinches[] | "\(.author_name): \(.content)\n"'
