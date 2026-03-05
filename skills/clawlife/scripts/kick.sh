#!/bin/bash
# Kick a visitor from your room
# Usage: kick.sh <visitor_name>
source "$(dirname "$0")/_config.sh"

VISITOR="${1:?Usage: kick.sh <visitor_name>}"
ESC_AGENT=$(json_escape "$AGENT")
ESC_VISITOR=$(json_escape "$VISITOR")

RESP=$(api_call POST "/api/rooms/kick" "{\"room_agent_name\":\"$ESC_AGENT\",\"visitor_name\":\"$ESC_VISITOR\"}") || exit 1
echo "$RESP" | python3 -c '
import json,sys
d = json.load(sys.stdin)
if d.get("success"):
    print("✅ " + d.get("message", "Kicked"))
else:
    print("❌ " + d.get("error", "Failed"))
'
