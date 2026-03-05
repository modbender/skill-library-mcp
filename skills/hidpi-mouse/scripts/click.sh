#!/bin/bash
# HiDPI-aware mouse click
# Usage: click.sh [--raw|--double|--right] <x> <y>

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DISPLAY="${DISPLAY:-:1}"
export DISPLAY
export XAUTHORITY="${XAUTHORITY:-$HOME/.Xauthority}"

# Parse options
RAW_MODE=false
CLICK_TYPE="1"  # 1=left, 2=middle, 3=right
REPEAT=1

while [[ $# -gt 0 ]]; do
    case "$1" in
        --raw)
            RAW_MODE=true
            shift
            ;;
        --double)
            REPEAT=2
            shift
            ;;
        --right)
            CLICK_TYPE=3
            shift
            ;;
        --middle)
            CLICK_TYPE=2
            shift
            ;;
        *)
            break
            ;;
    esac
done

if [[ $# -lt 2 ]]; then
    echo "Usage: click.sh [--raw|--double|--right|--middle] <x> <y>"
    exit 1
fi

X="$1"
Y="$2"

# Apply scaling unless raw mode
if [[ "$RAW_MODE" != "true" ]]; then
    SCALE="${HIDPI_SCALE:-$("$SCRIPT_DIR/detect-scale.sh")}"
    X=$(echo "$X * $SCALE" | bc | cut -d'.' -f1)
    Y=$(echo "$Y * $SCALE" | bc | cut -d'.' -f1)
fi

# Move and click
xdotool mousemove "$X" "$Y"
sleep 0.1

for ((i=0; i<REPEAT; i++)); do
    xdotool click "$CLICK_TYPE"
    [[ $REPEAT -gt 1 ]] && sleep 0.1
done

echo "Clicked at ($X, $Y) [button=$CLICK_TYPE, repeat=$REPEAT]"
