#!/bin/bash
# Leave the room you're visiting
# Usage: leave.sh <host_agent>
source "$(dirname "$0")/_config.sh"

TARGET="${1:?Usage: leave.sh <host_agent>}"
ESC_AGENT=$(json_escape "$AGENT")
ESC_TARGET=$(json_escape "$TARGET")
api_call POST /api/rooms/leave "{\"visitor\":\"$ESC_AGENT\",\"target\":\"$ESC_TARGET\"}" >/dev/null || exit 1
echo "👋 Left $TARGET's room"
