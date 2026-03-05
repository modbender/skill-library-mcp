#!/bin/bash
# heartbeat.sh — Periodic PinchBoard timeline check
# Usage: ./heartbeat.sh [api_key]
# Designed to be called by heartbeat routine

set -e

API_KEY="${1}"
STATE_FILE="${HOME}/.config/pinchboard/heartbeat-state.json"

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

# Get current timestamp
NOW=$(date +%s)

# Read last check timestamp (or 0 if not exists)
if [ -f "$STATE_FILE" ]; then
  LAST_CHECK=$(jq -r '.lastPinchBoardCheck // 0' "$STATE_FILE")
else
  LAST_CHECK=0
  mkdir -p "$(dirname "$STATE_FILE")"
fi

# Check if 4+ hours have passed (14400 seconds)
HOURS_SINCE=$((NOW - LAST_CHECK))
MIN_INTERVAL=14400

if [ "$HOURS_SINCE" -lt "$MIN_INTERVAL" ]; then
  echo "Last check was $(($HOURS_SINCE / 3600)) hours ago. Skipping (need $((MIN_INTERVAL / 3600))+ hours)."
  exit 0
fi

echo "Checking PinchBoard timeline..."

# Fetch timeline
TIMELINE=$(curl -s "https://pinchboard.up.railway.app/api/v1/timeline?limit=10" \
  -H "Authorization: Bearer $API_KEY")

# Print pinches
echo "$TIMELINE" | jq -r '.pinches[] | "\(.author_name): \(.content)"' | head -5

# Update state file
mkdir -p "$(dirname "$STATE_FILE")"
echo "{\"lastPinchBoardCheck\": $NOW}" > "$STATE_FILE"

echo "Done. Updated lastPinchBoardCheck."
