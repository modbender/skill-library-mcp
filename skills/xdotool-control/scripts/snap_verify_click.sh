#!/bin/bash
# snap_verify_click.sh — Screenshot, verify state, then click
# Usage: snap_verify_click.sh <window_name> <snap_label> <x> <y>
#
# Takes a screenshot before and after clicking so you can verify the action worked.

WINDOW_NAME="${1:-Google Chrome}"
LABEL="${2:-action}"
CLICK_X="${3:-960}"
CLICK_Y="${4:-56}"

BEFORE="/tmp/xdotool_${LABEL}_before.png"
AFTER="/tmp/xdotool_${LABEL}_after.png"

WIN=$(xdotool search --name "$WINDOW_NAME" 2>/dev/null | head -1)
if [ -z "$WIN" ]; then
  echo "ERROR: Window '$WINDOW_NAME' not found" >&2
  exit 1
fi

xdotool windowactivate --sync "$WIN"
sleep 0.3

# Before snapshot
scrot "$BEFORE" 2>/dev/null
echo "Before: $BEFORE"

# Click
xdotool mousemove "$CLICK_X" "$CLICK_Y" click 1
sleep 0.5

# After snapshot
scrot "$AFTER" 2>/dev/null
echo "After:  $AFTER"
echo "Read both files to verify the click had the intended effect."
