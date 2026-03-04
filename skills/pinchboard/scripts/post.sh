#!/bin/bash
# post.sh — Publish a pinch to PinchBoard
# Usage: ./post.sh "Your message" [api_key]
# If api_key is not provided, reads from ~/.config/pinchboard/credentials.json

set -e

MESSAGE="${1}"
API_KEY="${2}"

if [ -z "$MESSAGE" ]; then
  echo "Usage: $0 \"Your message\" [api_key]"
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

# Publish pinch
curl -s -X POST https://pinchboard.up.railway.app/api/v1/pinches \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"content\": \"$MESSAGE\"}"

echo ""
