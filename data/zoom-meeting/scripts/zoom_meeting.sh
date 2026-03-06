#!/bin/bash
# Create a Zoom meeting
# Usage: zoom_meeting.sh <topic> <start_time> [duration_minutes] [timezone]
# Example: zoom_meeting.sh "Team Meeting" "2026-03-01T11:50:00" 60 "Asia/Aqtobe"

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=zoom_auth.sh
source "${SCRIPT_DIR}/zoom_auth.sh"

TOPIC="${1:?Usage: zoom_meeting.sh <topic> <start_time> [duration] [timezone]}"
START_TIME="${2:?Missing start_time (format: YYYY-MM-DDTHH:MM:SS)}"
DURATION="${3:-60}"
TIMEZONE="${4:-Asia/Aqtobe}"

CREDS_FILE="${ZOOM_CREDENTIALS:-$HOME/.openclaw/credentials/zoom.json}"

# --- Validate start_time format ---
if ! [[ "$START_TIME" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}$ ]]; then
  echo "ERROR: start_time must be in format YYYY-MM-DDTHH:MM:SS (e.g. 2026-03-01T11:50:00)" >&2
  exit 1
fi

# --- Get access token ---
ZOOM_TOKEN=$(zoom_get_token "$CREDS_FILE")

# --- Build JSON payload safely ---
PAYLOAD=$(jq -n \
  --arg topic "$TOPIC" \
  --arg start_time "$START_TIME" \
  --argjson duration "$DURATION" \
  --arg timezone "$TIMEZONE" \
  '{
    topic: $topic,
    type: 2,
    start_time: $start_time,
    duration: $duration,
    timezone: $timezone,
    settings: {
      host_video: true,
      participant_video: true,
      join_before_host: true,
      waiting_room: false
    }
  }')

# --- Create Zoom Meeting ---
ZOOM_RESPONSE=$(curl -s -X POST "https://api.zoom.us/v2/users/me/meetings" \
  -H "Authorization: Bearer $ZOOM_TOKEN" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD")

JOIN_URL=$(echo "$ZOOM_RESPONSE" | jq -r '.join_url')

if [ -z "$JOIN_URL" ] || [ "$JOIN_URL" = "null" ]; then
  echo "ERROR: Failed to create Zoom meeting" >&2
  echo "$ZOOM_RESPONSE" >&2
  exit 1
fi

echo "$ZOOM_RESPONSE" | jq '{join_url, id, password}'
