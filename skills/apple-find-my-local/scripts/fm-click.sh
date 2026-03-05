#!/bin/bash
# Click at relative coordinates within Find My window
# Usage: fm-click.sh <rel_x> <rel_y>

set -euo pipefail

REL_X="${1:?Usage: fm-click.sh <rel_x> <rel_y>}"
REL_Y="${2:?Usage: fm-click.sh <rel_x> <rel_y>}"

# Validate inputs are positive integers (prevent arithmetic injection)
if ! [[ "$REL_X" =~ ^[0-9]+$ ]] || ! [[ "$REL_Y" =~ ^[0-9]+$ ]]; then
    echo "Error: Coordinates must be positive integers" >&2
    exit 1
fi

# Set bridge socket path - expand $HOME if present in value
PEEKABOO_BRIDGE_SOCKET="${PEEKABOO_BRIDGE_SOCKET:-\$HOME/Library/Application Support/OpenClaw/bridge.sock}"
PEEKABOO_BRIDGE_SOCKET="${PEEKABOO_BRIDGE_SOCKET//\$HOME/$HOME}"
export PEEKABOO_BRIDGE_SOCKET

# Get window bounds
bounds=$(peekaboo window list --app "Find My" --json 2>/dev/null | jq -r '(.data.windows[0].bounds // .windows[0].bounds) // empty')

if [ -z "$bounds" ]; then
    echo "Error: Find My window not found. Is the app open?" >&2
    exit 1
fi

win_x=$(echo "$bounds" | jq -r '.x')
win_y=$(echo "$bounds" | jq -r '.y')

# Calculate absolute coordinates
abs_x=$((win_x + REL_X))
abs_y=$((win_y + REL_Y))

# Ensure Find My is focused and click
peekaboo app switch --to "Find My" >/dev/null 2>&1
sleep 0.1
peekaboo click --coords "${abs_x},${abs_y}" 2>&1
