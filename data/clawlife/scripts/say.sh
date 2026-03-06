#!/bin/bash
# Say something in a room (must be in the room — home or visiting)
# Usage: say.sh <room_owner> <message>
# Max 150 characters.
source "$(dirname "$0")/_config.sh"

ROOM="${1:?Usage: say.sh <room_owner> <message>}"
MSG="${2:?Usage: say.sh <room_owner> <message>}"
SENDER_ESC=$(json_escape "$AGENT")
MSG_ESC=$(json_escape "$MSG")
BODY="{\"sender\":\"$SENDER_ESC\",\"message\":\"$MSG_ESC\"}"
api_call POST "/api/rooms/by-name/$ROOM/feed" "$BODY" >/dev/null || exit 1
echo "💬 Said: $MSG"
