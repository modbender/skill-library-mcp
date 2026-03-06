#!/bin/bash
# Open info panel for currently selected item and capture screenshot
# Usage: fm-info.sh [output_path]
# Run after selecting an item with fm-select-item.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUTPUT_DIR="${FM_OUTPUT_DIR:-/tmp}"
OUTPUT_PATH="${1:-$OUTPUT_DIR/findmy-info-$(date +%s).png}"

# Set bridge socket path - expand $HOME if present in value
PEEKABOO_BRIDGE_SOCKET="${PEEKABOO_BRIDGE_SOCKET:-\$HOME/Library/Application Support/OpenClaw/bridge.sock}"
PEEKABOO_BRIDGE_SOCKET="${PEEKABOO_BRIDGE_SOCKET//\$HOME/$HOME}"
export PEEKABOO_BRIDGE_SOCKET

# Get window info
window_info=$("$SCRIPT_DIR/fm-window.sh")
window_id=$(echo "$window_info" | jq -r '.window_id')

# Try to find the info button using peekaboo see
result=$(peekaboo see --window-id "$window_id" --json 2>/dev/null)

# Look for info button (various possible labels)
info_btn=$(echo "$result" | jq -r '
  [.data.ui_elements // .ui_elements // [] | .[] |
   select(.is_actionable == true) |
   select(.description != null) |
   select(.description | test("info|detail|more"; "i"))] |
  first // empty')

if [ -n "$info_btn" ] && [ "$info_btn" != "null" ]; then
    info_id=$(echo "$info_btn" | jq -r '.id')
    echo "Found info button, clicking..." >&2
    peekaboo click --on "$info_id" --window-id "$window_id" >/dev/null 2>&1
    sleep 0.5
else
    echo "Note: Could not find info button via accessibility." >&2
    echo "If item was just selected, the info panel may already be visible," >&2
    echo "or you may need to click the (i) button manually on the map popup." >&2
fi

# Capture screenshot
"$SCRIPT_DIR/fm-screenshot.sh" "$OUTPUT_PATH" >/dev/null

echo "Screenshot: $OUTPUT_PATH"
echo ""
echo "Info panel actions (if visible):"
echo "  - Play Sound: Click on the play button"
echo "  - Directions: Opens Maps with directions"
echo "  - Lost Mode: Enable to share contact info"
