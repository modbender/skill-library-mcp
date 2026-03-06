#!/bin/bash
# HiDPI-aware mouse drag
# Usage: drag.sh [--raw] <from_x> <from_y> <to_x> <to_y>

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DISPLAY="${DISPLAY:-:1}"
export DISPLAY
export XAUTHORITY="${XAUTHORITY:-$HOME/.Xauthority}"

RAW_MODE=false
[[ "$1" == "--raw" ]] && { RAW_MODE=true; shift; }

if [[ $# -lt 4 ]]; then
    echo "Usage: drag.sh [--raw] <from_x> <from_y> <to_x> <to_y>"
    exit 1
fi

FROM_X="$1"
FROM_Y="$2"
TO_X="$3"
TO_Y="$4"

if [[ "$RAW_MODE" != "true" ]]; then
    SCALE="${HIDPI_SCALE:-$("$SCRIPT_DIR/detect-scale.sh")}"
    FROM_X=$(echo "$FROM_X * $SCALE" | bc | cut -d'.' -f1)
    FROM_Y=$(echo "$FROM_Y * $SCALE" | bc | cut -d'.' -f1)
    TO_X=$(echo "$TO_X * $SCALE" | bc | cut -d'.' -f1)
    TO_Y=$(echo "$TO_Y * $SCALE" | bc | cut -d'.' -f1)
fi

# Perform drag
xdotool mousemove "$FROM_X" "$FROM_Y"
sleep 0.1
xdotool mousedown 1
sleep 0.1
xdotool mousemove --sync "$TO_X" "$TO_Y"
sleep 0.1
xdotool mouseup 1

echo "Dragged from ($FROM_X, $FROM_Y) to ($TO_X, $TO_Y)"
