#!/bin/bash
# Select an item by position in Find My sidebar
# Usage: fm-select-item.sh <position> [people|devices|items]
# Position: 1 = first item, 2 = second, etc.

set -euo pipefail

POSITION="${1:?Usage: fm-select-item.sh <position> [people|devices|items]}"
TAB="${2:-items}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Set bridge socket path - expand $HOME if present in value
PEEKABOO_BRIDGE_SOCKET="${PEEKABOO_BRIDGE_SOCKET:-\$HOME/Library/Application Support/OpenClaw/bridge.sock}"
PEEKABOO_BRIDGE_SOCKET="${PEEKABOO_BRIDGE_SOCKET//\$HOME/$HOME}"
export PEEKABOO_BRIDGE_SOCKET

# Validate position is a number
if ! [[ "$POSITION" =~ ^[0-9]+$ ]]; then
    echo "Error: Position must be a number (1, 2, 3, ...)" >&2
    exit 1
fi

# Switch to the requested tab
"$SCRIPT_DIR/fm-tab.sh" "$TAB" >/dev/null 2>&1
sleep 0.3

# Calculate Y coordinate based on position
# Sidebar items start around y=120, with ~54px spacing
SIDEBAR_X=150
FIRST_ITEM_Y=120
ITEM_SPACING=54

rel_y=$((FIRST_ITEM_Y + (POSITION - 1) * ITEM_SPACING))

# Click on the item
"$SCRIPT_DIR/fm-click.sh" "$SIDEBAR_X" "$rel_y"

echo "Selected item #$POSITION in $TAB tab"
