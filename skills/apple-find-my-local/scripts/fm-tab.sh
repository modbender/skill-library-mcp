#!/bin/bash
# Switch Find My to a specific tab
# Usage: fm-tab.sh <people|devices|items>

set -euo pipefail

TAB="${1:-items}"

# Set bridge socket path - expand $HOME if present in value
PEEKABOO_BRIDGE_SOCKET="${PEEKABOO_BRIDGE_SOCKET:-\$HOME/Library/Application Support/OpenClaw/bridge.sock}"
PEEKABOO_BRIDGE_SOCKET="${PEEKABOO_BRIDGE_SOCKET//\$HOME/$HOME}"
export PEEKABOO_BRIDGE_SOCKET

# Tab X coordinates (relative to window)
case "$TAB" in
    people)  TAB_X=63 ;;
    devices) TAB_X=154 ;;
    items)   TAB_X=243 ;;
    *)
        echo "Error: Unknown tab '$TAB'. Use: people, devices, items" >&2
        exit 1
        ;;
esac

TAB_Y=68  # Tab bar Y coordinate

# Get window bounds
bounds=$(peekaboo window list --app "Find My" --json 2>/dev/null | jq -r '(.data.windows[0].bounds // .windows[0].bounds) // empty')

if [ -z "$bounds" ]; then
    echo "Error: Find My window not found. Is the app open?" >&2
    exit 1
fi

win_x=$(echo "$bounds" | jq -r '.x')
win_y=$(echo "$bounds" | jq -r '.y')

# Calculate absolute coordinates
abs_x=$((win_x + TAB_X))
abs_y=$((win_y + TAB_Y))

# Switch to Find My and click
peekaboo app switch --to "Find My" >/dev/null 2>&1
sleep 0.2
peekaboo click --coords "${abs_x},${abs_y}" 2>&1

echo "Switched to $TAB tab"
