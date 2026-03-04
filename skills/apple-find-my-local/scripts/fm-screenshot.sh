#!/bin/bash
# Capture Find My window screenshot
# Usage: fm-screenshot.sh [output_path]

set -euo pipefail

OUTPUT_PATH="${1:-/tmp/findmy.png}"

# Set bridge socket path - expand $HOME if present in value
PEEKABOO_BRIDGE_SOCKET="${PEEKABOO_BRIDGE_SOCKET:-\$HOME/Library/Application Support/OpenClaw/bridge.sock}"
PEEKABOO_BRIDGE_SOCKET="${PEEKABOO_BRIDGE_SOCKET//\$HOME/$HOME}"
export PEEKABOO_BRIDGE_SOCKET

# Get window ID (--app flag hangs, so we use --window-id)
window_id=$(peekaboo window list --app "Find My" --json 2>/dev/null | jq -r '(.data.windows[0].window_id // .windows[0].window_id) // empty')

if [ -z "$window_id" ]; then
    echo "Error: Find My window not found. Is the app open?" >&2
    exit 1
fi

# Capture using window ID
peekaboo image --window-id "$window_id" --path "$OUTPUT_PATH" 2>&1

echo "$OUTPUT_PATH"
