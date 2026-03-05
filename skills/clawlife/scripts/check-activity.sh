#!/bin/bash
# Check if there's social activity in your room
# Returns: SOCIAL_ACTIVE or QUIET
# Usage: check-activity.sh
source "$(dirname "$0")/_config.sh"

if [ $# -ne 0 ]; then
  echo "Usage: check-activity.sh" >&2
  exit 1
fi

RESP=$(api_get "/api/rooms/by-name/$AGENT/feed?limit=5&filter=action") || { echo "QUIET"; exit 0; }

HAS_SOCIAL=$(echo "$RESP" | grep -cE "knocking|entered|says")
if [ "$HAS_SOCIAL" -gt 0 ]; then
  echo "SOCIAL_ACTIVE"
else
  echo "QUIET"
fi
