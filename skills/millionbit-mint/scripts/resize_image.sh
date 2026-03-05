#!/usr/bin/env bash
# resize_image.sh - Resize an image to exact plot dimensions
#
# Usage: ./resize_image.sh <input_image> <width> <height> [output_image]
#
# Width and height must be multiples of 16. If output is omitted,
# writes to <input_basename>_<W>x<H>.png in the same directory.
#
# Output: JSON with output path and dimensions

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/config.sh"

if [ "$#" -lt 3 ]; then
    echo "Usage: $0 <input_image> <width> <height> [output_image]" >&2
    exit 1
fi

INPUT="$1"
WIDTH="$2"
HEIGHT="$3"

# Generate output path if not provided
if [ "$#" -ge 4 ]; then
    OUTPUT="$4"
else
    BASENAME=$(basename "$INPUT" | sed 's/\.[^.]*$//')
    DIRNAME=$(dirname "$INPUT")
    OUTPUT="${DIRNAME}/${BASENAME}_${WIDTH}x${HEIGHT}.png"
fi

# Validate input exists
if [ ! -f "$INPUT" ]; then
    echo "Error: Input file not found: $INPUT" >&2
    exit 1
fi

# Validate dimensions
if (( WIDTH % GRID_UNIT != 0 )); then
    echo "Error: Width ($WIDTH) must be a multiple of $GRID_UNIT" >&2
    exit 1
fi
if (( HEIGHT % GRID_UNIT != 0 )); then
    echo "Error: Height ($HEIGHT) must be a multiple of $GRID_UNIT" >&2
    exit 1
fi

# Use Node.js sharp helper for resizing
node "$HELPERS_DIR/resize.js" "$INPUT" "$WIDTH" "$HEIGHT" "$OUTPUT"
