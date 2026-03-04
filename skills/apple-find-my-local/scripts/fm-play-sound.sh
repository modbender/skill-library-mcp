#!/bin/bash
# Play sound on a Find My item (AirTag)
# Usage: fm-play-sound.sh <position>
# Position: 1 = first item in Items tab, 2 = second, etc.
# Note: This is a best-effort automation - requires info panel to be open

set -euo pipefail

POSITION="${1:?Usage: fm-play-sound.sh <position>}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Set bridge socket path - expand $HOME if present in value
PEEKABOO_BRIDGE_SOCKET="${PEEKABOO_BRIDGE_SOCKET:-\$HOME/Library/Application Support/OpenClaw/bridge.sock}"
PEEKABOO_BRIDGE_SOCKET="${PEEKABOO_BRIDGE_SOCKET//\$HOME/$HOME}"
export PEEKABOO_BRIDGE_SOCKET

echo "Attempting to play sound on item #$POSITION..." >&2

# Step 1: Select the item
"$SCRIPT_DIR/fm-select-item.sh" "$POSITION" items >/dev/null 2>&1
sleep 0.5

# Step 2: Get window info for coordinate calculation
window_info=$("$SCRIPT_DIR/fm-window.sh")
window_id=$(echo "$window_info" | jq -r '.window_id')

# Step 3: Try to find Play Sound button in UI
result=$(peekaboo see --window-id "$window_id" --json 2>/dev/null)

play_btn=$(echo "$result" | jq -r '
  [.data.ui_elements // .ui_elements // [] | .[] |
   select(.is_actionable == true) |
   select(.label != null or .description != null) |
   select((.label // .description // "") | test("play|sound"; "i"))] |
  first // empty')

if [ -n "$play_btn" ] && [ "$play_btn" != "null" ]; then
    play_id=$(echo "$play_btn" | jq -r '.id')
    echo "Found Play Sound button, clicking..." >&2
    peekaboo click --on "$play_id" --window-id "$window_id" 2>&1
    echo "Sound should now be playing!"
else
    echo ""
    echo "Could not automatically find 'Play Sound' button." >&2
    echo ""
    echo "Manual steps:" >&2
    echo "1. If not visible, click the (i) info button on the map popup" >&2
    echo "2. Then click 'Play Sound' in the info panel" >&2
    echo ""
    echo "Taking screenshot for reference..." >&2
    "$SCRIPT_DIR/fm-screenshot.sh" "/tmp/findmy-playsound.png" >/dev/null
    echo "Screenshot: /tmp/findmy-playsound.png"
fi
