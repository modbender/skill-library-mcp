#!/bin/bash
# List items in a Find My tab
# Usage: fm-list.sh [people|devices|items]
# Note: Find My's accessibility tree doesn't expose item names reliably.
#       This script captures a screenshot for visual inspection.

set -euo pipefail

TAB="${1:-items}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUTPUT_DIR="${FM_OUTPUT_DIR:-/tmp}"

# Set bridge socket path - expand $HOME if present in value
PEEKABOO_BRIDGE_SOCKET="${PEEKABOO_BRIDGE_SOCKET:-\$HOME/Library/Application Support/OpenClaw/bridge.sock}"
PEEKABOO_BRIDGE_SOCKET="${PEEKABOO_BRIDGE_SOCKET//\$HOME/$HOME}"
export PEEKABOO_BRIDGE_SOCKET

# Switch to the requested tab
"$SCRIPT_DIR/fm-tab.sh" "$TAB" >/dev/null 2>&1
sleep 0.3

# Capture screenshot
timestamp=$(date +%s)
output_path="$OUTPUT_DIR/findmy-${TAB}-list-${timestamp}.png"
"$SCRIPT_DIR/fm-screenshot.sh" "$output_path" >/dev/null

echo "Screenshot saved: $output_path"
echo ""
echo "Note: Find My's sidebar items aren't exposed via accessibility APIs."
echo "View the screenshot to see available ${TAB}."
echo ""
echo "Sidebar layout (approximate Y positions from window top):"
echo "  - First item:  y ≈ 120"
echo "  - Second item: y ≈ 174"
echo "  - Third item:  y ≈ 228"
echo "  - (spacing: ~54px per item)"
echo ""
echo "Use fm-click.sh 150 <y> to select an item."
