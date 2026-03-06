#!/bin/bash
# Crop a region from an image using sips
# Usage: crop-image.sh <input> <output> <x> <y> <width> <height>
#
# Note: sips uses a confusing syntax where -c takes HEIGHT WIDTH (reversed!)
# and --cropOffset takes X Y (normal order)

INPUT="$1"
OUTPUT="$2"
X="$3"
Y="$4"
WIDTH="$5"
HEIGHT="$6"

if [ $# -lt 6 ]; then
    echo "Usage: crop-image.sh <input> <output> <x> <y> <width> <height>"
    echo ""
    echo "Crops a region starting at (x,y) with given width and height."
    echo "Coordinates use top-left as origin (0,0)."
    echo ""
    echo "Example: crop-image.sh screen.png toolbar.png 1600 0 400 100"
    exit 1
fi

if [ ! -f "$INPUT" ]; then
    echo "Error: Input file '$INPUT' not found"
    exit 1
fi

# Get original dimensions
ORIG_WIDTH=$(sips -g pixelWidth "$INPUT" | tail -1 | awk '{print $2}')
ORIG_HEIGHT=$(sips -g pixelHeight "$INPUT" | tail -1 | awk '{print $2}')

# Validate crop region
if [ $((X + WIDTH)) -gt "$ORIG_WIDTH" ] || [ $((Y + HEIGHT)) -gt "$ORIG_HEIGHT" ]; then
    echo "Warning: Crop region extends beyond image bounds"
    echo "Image: ${ORIG_WIDTH}x${ORIG_HEIGHT}, Crop: ${X},${Y} + ${WIDTH}x${HEIGHT}"
fi

# Copy input to output first (sips modifies in place)
cp "$INPUT" "$OUTPUT"

# sips -c HEIGHT WIDTH crops to that size (centered by default)
# --cropOffset X Y sets where the crop starts (from top-left)
# Note: -c takes HEIGHT then WIDTH (counterintuitive!)
sips --cropOffset "$X" "$Y" -c "$HEIGHT" "$WIDTH" "$OUTPUT" > /dev/null 2>&1

echo "Cropped: ${WIDTH}x${HEIGHT} from (${X},${Y}) -> $OUTPUT"
