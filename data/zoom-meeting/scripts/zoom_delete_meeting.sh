#!/bin/bash
# Delete a Zoom meeting by Meeting ID
# Usage: zoom_delete_meeting.sh <meeting_id>
# Example: zoom_delete_meeting.sh 123456789

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=zoom_auth.sh
source "${SCRIPT_DIR}/zoom_auth.sh"

MEETING_ID="${1:?Usage: zoom_delete_meeting.sh <meeting_id>}"

CREDS_FILE="${ZOOM_CREDENTIALS:-$HOME/.openclaw/credentials/zoom.json}"

# --- Get access token ---
ZOOM_TOKEN=$(zoom_get_token "$CREDS_FILE")

# --- Delete the meeting ---
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" -X DELETE \
  "https://api.zoom.us/v2/meetings/${MEETING_ID}" \
  -H "Authorization: Bearer $ZOOM_TOKEN")

if [ "$HTTP_STATUS" = "204" ]; then
  echo "{\"status\": \"deleted\", \"meeting_id\": \"${MEETING_ID}\"}"
elif [ "$HTTP_STATUS" = "404" ]; then
  echo "ERROR: Meeting ${MEETING_ID} not found" >&2
  exit 1
else
  echo "ERROR: Failed to delete meeting (HTTP ${HTTP_STATUS})" >&2
  exit 1
fi
