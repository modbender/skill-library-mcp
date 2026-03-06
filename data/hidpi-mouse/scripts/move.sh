#!/bin/bash
# HiDPI-aware mouse move (no click)
# Usage: move.sh [--raw] <x> <y>

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DISPLAY="${DISPLAY:-:1}"
export DISPLAY
export XAUTHORITY="${XAUTHORITY:-$HOME/.Xauthority}"

RAW_MODE=false
[[ "$1" == "--raw" ]] && { RAW_MODE=true; shift; }

if [[ $# -lt 2 ]]; then
    echo "Usage: move.sh [--raw] <x> <y>"
    exit 1
fi

X="$1"
Y="$2"

if [[ "$RAW_MODE" != "true" ]]; then
    SCALE="${HIDPI_SCALE:-$("$SCRIPT_DIR/detect-scale.sh")}"
    X=$(echo "$X * $SCALE" | bc | cut -d'.' -f1)
    Y=$(echo "$Y * $SCALE" | bc | cut -d'.' -f1)
fi

xdotool mousemove "$X" "$Y"
echo "Moved to ($X, $Y)"
