#!/bin/bash
# Move agent to position in room (via heartbeat)
# Usage: move.sh <x> <y>
source "$(dirname "$0")/_config.sh"

X="${1:?Usage: move.sh <x> <y>}"
Y="${2:?Usage: move.sh <x> <y>}"

if ! [[ "$X" =~ ^-?[0-9]+$ ]] || ! [[ "$Y" =~ ^-?[0-9]+$ ]]; then
  echo "❌ x and y must be integers" >&2
  exit 1
fi

ESC_AGENT=$(json_escape "$AGENT")
api_call POST /api/agents/heartbeat "{\"name\":\"$ESC_AGENT\",\"pos_x\":$X,\"pos_y\":$Y}" >/dev/null || exit 1
echo "🚶 Moved to ($X,$Y)"
