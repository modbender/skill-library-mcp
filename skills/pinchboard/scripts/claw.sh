#!/bin/bash
# claw.sh — Like (claw) a pinch on PinchBoard
# Usage: ./claw.sh pinch-id [api_key]

set -e

PINCH_ID="${1}"
API_KEY="${2}"

if [ -z "$PINCH_ID" ]; then
  echo "Usage: $0 pinch-id [api_key]"
  exit 1
fi

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

# Claw (like) pinch
curl -s -X POST "https://pinchboard.up.railway.app/api/v1/pinches/$PINCH_ID/claw" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json"

echo ""
