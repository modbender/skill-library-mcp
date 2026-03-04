#!/bin/bash
# Click at display coordinates (from screenshot viewer)
# Usage: click-at-display.sh <display_x> <display_y> [--double] [--right]
#
# This script converts display coordinates (what you see in image viewer)
# to cliclick logical coordinates using the calibrated scale factor.

CALIBRATION_FILE="$HOME/.clawdbot/mac-control-calibration.json"

# Default scale factor if not calibrated
DEFAULT_SCALE=2.5

# Parse args
DISPLAY_X=$1
DISPLAY_Y=$2
CLICK_TYPE="c"  # single click

shift 2
while [[ $# -gt 0 ]]; do
    case $1 in
        --double) CLICK_TYPE="dc" ;;
        --right) CLICK_TYPE="rc" ;;
        *) ;;
    esac
    shift
done

if [[ -z "$DISPLAY_X" || -z "$DISPLAY_Y" ]]; then
    echo "Usage: click-at-display.sh <display_x> <display_y> [--double] [--right]" >&2
    echo "" >&2
    echo "Coordinates should be from the displayed image (e.g., 2000x1125 display of 3840x2160 screenshot)" >&2
    exit 1
fi

# Get scale factor from calibration or use default
if [[ -f "$CALIBRATION_FILE" ]]; then
    SCALE=$(cat "$CALIBRATION_FILE" | grep scaleFactor | sed 's/.*: *\([0-9.]*\).*/\1/')
else
    SCALE=$DEFAULT_SCALE
    echo "⚠️  No calibration found, using default scale: $SCALE" >&2
    echo "   Run: bash scripts/calibrate.sh" >&2
fi

# The displayed image is typically 2000x1125 showing a 3840x2160 screenshot
# Display ratio: 3840/2000 = 1.92
DISPLAY_RATIO=1.92

# Convert display coords to original screenshot coords
ORIG_X=$(echo "$DISPLAY_X * $DISPLAY_RATIO" | bc)
ORIG_Y=$(echo "$DISPLAY_Y * $DISPLAY_RATIO" | bc)

# Convert screenshot coords to cliclick coords
# cliclick = original / (screenshot_scale)
# But we found that cliclick_coords = display_coords * SCALE directly works better
CLICLICK_X=$(echo "$DISPLAY_X * $SCALE" | bc | cut -d. -f1)
CLICLICK_Y=$(echo "$DISPLAY_Y * $SCALE" | bc | cut -d. -f1)

echo "Display: ($DISPLAY_X, $DISPLAY_Y) → cliclick: ($CLICLICK_X, $CLICLICK_Y)" >&2

# Perform click
/opt/homebrew/bin/cliclick "$CLICK_TYPE:$CLICLICK_X,$CLICLICK_Y"

echo "Clicked at ($CLICLICK_X, $CLICLICK_Y)"
