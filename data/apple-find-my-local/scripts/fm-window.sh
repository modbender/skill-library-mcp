#!/bin/bash
# Get Find My window info (id, bounds)
# Returns JSON with window_id, x, y, width, height

set -euo pipefail

# Set bridge socket path - expand $HOME if present in value
PEEKABOO_BRIDGE_SOCKET="${PEEKABOO_BRIDGE_SOCKET:-\$HOME/Library/Application Support/OpenClaw/bridge.sock}"
PEEKABOO_BRIDGE_SOCKET="${PEEKABOO_BRIDGE_SOCKET//\$HOME/$HOME}"
export PEEKABOO_BRIDGE_SOCKET

# Get window list for Find My
result=$(peekaboo window list --app "Find My" --json 2>/dev/null)

# Extract first window's info (handle both .data.windows and .windows paths)
window_id=$(echo "$result" | jq -r '(.data.windows[0].window_id // .windows[0].window_id) // empty')
bounds=$(echo "$result" | jq -r '(.data.windows[0].bounds // .windows[0].bounds) // empty')

if [ -z "$window_id" ] || [ "$window_id" = "null" ]; then
    echo "Error: Find My window not found. Is the app open?" >&2
    exit 1
fi

# Output combined JSON
echo "$bounds" | jq --argjson wid "$window_id" '. + {window_id: $wid}'
