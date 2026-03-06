#!/bin/bash
# Find element position interactively
# Takes screenshot, crops around mouse position, helps identify precise coordinates
#
# Usage: find-element.sh [--move x,y] [--crop x,y,w,h]

TMP_DIR="/tmp/mac-find-element-$$"
mkdir -p "$TMP_DIR"

# Get current mouse position
MOUSE_POS=$(/opt/homebrew/bin/cliclick p)
MOUSE_X=$(echo $MOUSE_POS | cut -d, -f1)
MOUSE_Y=$(echo $MOUSE_POS | cut -d, -f2)

echo "Current mouse position (cliclick): $MOUSE_X, $MOUSE_Y"

# Parse args
MOVE_TO=""
CROP_REGION=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --move)
            MOVE_TO=$2
            shift 2
            ;;
        --crop)
            CROP_REGION=$2
            shift 2
            ;;
        *)
            shift
            ;;
    esac
done

# Move mouse if requested
if [[ -n "$MOVE_TO" ]]; then
    /opt/homebrew/bin/cliclick m:$MOVE_TO
    MOUSE_POS=$MOVE_TO
    MOUSE_X=$(echo $MOUSE_POS | cut -d, -f1)
    MOUSE_Y=$(echo $MOUSE_POS | cut -d, -f2)
    echo "Moved to: $MOUSE_X, $MOUSE_Y"
fi

# Take screenshot with cursor
/usr/sbin/screencapture -C -x "$TMP_DIR/full.png"
echo "Screenshot saved: $TMP_DIR/full.png"

# Get dimensions
WIDTH=$(sips -g pixelWidth "$TMP_DIR/full.png" | tail -1 | awk '{print $2}')
HEIGHT=$(sips -g pixelHeight "$TMP_DIR/full.png" | tail -1 | awk '{print $2}')
echo "Screenshot dimensions: ${WIDTH}x${HEIGHT}"

# Crop around mouse if no specific region
if [[ -z "$CROP_REGION" ]]; then
    # Scale factor from cliclick to screenshot coords
    SCALE_FACTOR=2  # Standard assumption: screenshot = 2x cliclick
    
    # Calculate crop region centered on mouse
    CROP_SIZE=400
    CROP_X=$((MOUSE_X * SCALE_FACTOR - CROP_SIZE / 2))
    CROP_Y=$((MOUSE_Y * SCALE_FACTOR - CROP_SIZE / 2))
    
    # Ensure within bounds
    [[ $CROP_X -lt 0 ]] && CROP_X=0
    [[ $CROP_Y -lt 0 ]] && CROP_Y=0
    
    CROP_REGION="$CROP_X,$CROP_Y,$CROP_SIZE,$CROP_SIZE"
fi

# Parse crop region
IFS=',' read -r CX CY CW CH <<< "$CROP_REGION"

echo "Cropping region: x=$CX, y=$CY, w=$CW, h=$CH"

# Use sips to crop
# sips crops from top-left, we need to calculate properly
sips -c $CH $CW --cropOffset $CY $CX "$TMP_DIR/full.png" --out "$TMP_DIR/cropped.png" 2>/dev/null

echo "Cropped image: $TMP_DIR/cropped.png"
echo ""
echo "To view: open $TMP_DIR/cropped.png"
echo "Full screenshot: $TMP_DIR/full.png"

# Output paths for scripting
echo "FULL=$TMP_DIR/full.png"
echo "CROPPED=$TMP_DIR/cropped.png"
