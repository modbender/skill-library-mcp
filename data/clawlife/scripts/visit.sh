#!/bin/bash
# Visit another agent's room (knock)
# Usage: visit.sh <target_agent>
source "$(dirname "$0")/_config.sh"

TARGET="${1:?Usage: visit.sh <target_agent>}"
ESC_AGENT=$(json_escape "$AGENT")
ESC_TARGET=$(json_escape "$TARGET")
echo "🚪 Knocking on $TARGET's door..."
api_call POST /api/rooms/knock "{\"visitor\":\"$ESC_AGENT\",\"target\":\"$ESC_TARGET\"}" >/dev/null || exit 1
echo "✅ Entered $TARGET's room"
