#!/bin/bash
# Locate an item/person/device in Find My by position
# Usage: fm-locate.sh <position> [people|devices|items]
# Position: 1 = first item, 2 = second, etc.
# Returns: Screenshot showing the selected item's location

set -euo pipefail

POSITION="${1:?Usage: fm-locate.sh <position> [people|devices|items]}"
TAB="${2:-items}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUTPUT_DIR="${FM_OUTPUT_DIR:-/tmp}"

# Set bridge socket path - expand $HOME if present in value
PEEKABOO_BRIDGE_SOCKET="${PEEKABOO_BRIDGE_SOCKET:-\$HOME/Library/Application Support/OpenClaw/bridge.sock}"
PEEKABOO_BRIDGE_SOCKET="${PEEKABOO_BRIDGE_SOCKET//\$HOME/$HOME}"
export PEEKABOO_BRIDGE_SOCKET

# Select the item
"$SCRIPT_DIR/fm-select-item.sh" "$POSITION" "$TAB" >/dev/null 2>&1
sleep 0.5

# Capture screenshot showing the location
timestamp=$(date +%s)
output_path="$OUTPUT_DIR/findmy-${TAB}-${POSITION}-${timestamp}.png"
"$SCRIPT_DIR/fm-screenshot.sh" "$output_path" >/dev/null

echo "Screenshot: $output_path"
echo ""
echo "The map should now show item #$POSITION from the $TAB tab."
echo "View the screenshot to see the location and address."
echo ""
echo "To see full info panel, run: fm-info.sh"
