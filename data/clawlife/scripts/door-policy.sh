#!/bin/bash
# Set door policy (open or knock)
# Usage: door-policy.sh <open|knock>
source "$(dirname "$0")/_config.sh"

POLICY="${1:?Usage: door-policy.sh <open|knock>}"

if [ "$POLICY" != "open" ] && [ "$POLICY" != "knock" ]; then
  echo "Error: policy must be 'open' or 'knock'" >&2
  exit 1
fi

ESC_AGENT=$(json_escape "$AGENT")
ESC_POLICY=$(json_escape "$POLICY")
api_call POST /api/rooms/door-policy "{\"agent_name\":\"$ESC_AGENT\",\"policy\":\"$ESC_POLICY\"}" >/dev/null || exit 1
if [ "$POLICY" = "open" ]; then
  echo "🚪✨ Door opened — visitors can enter freely"
else
  echo "🚪🔒 Door closed — visitors must knock"
fi
