#!/bin/bash
# =============================================================================
# optimize_image.sh
# Resizes and optimizes images for Open Graph (1200x630) using ImageMagick.
# =============================================================================

set -euo pipefail

# Default dimensions for Open Graph (Facebook, LinkedIn, Twitter)
DEFAULT_WIDTH=1200
DEFAULT_HEIGHT=630
DEFAULT_QUALITY=85

# Parse arguments
INPUT="${1:-}"
OUTPUT="${2:-}"

# Display usage if arguments are missing
if [ -z "$INPUT" ] || [ -z "$OUTPUT" ]; then
    echo "Usage: $0 <input_image> <output_image>" >&2
    echo "Example: $0 /tmp/cover.jpg /tmp/cover_optimized.jpg" >&2
    exit 1
fi

# Check if input file exists
if [ ! -f "$INPUT" ]; then
    echo "ERROR: Input image not found: $INPUT" >&2
    exit 1
fi

# Check if ImageMagick convert command is available
if ! command -v convert &> /dev/null; then
    echo "ERROR: ImageMagick 'convert' command not found" >&2
    echo "Install with: apt install imagemagick (Debian/Ubuntu)" >&2
    echo "           or: brew install imagemagick (macOS)" >&2
    exit 1
fi

# Get input file size for logging
INPUT_SIZE=$(du -h "$INPUT" | cut -f1)

echo "Processing image: $INPUT ($INPUT_SIZE)"
echo "Output: $OUTPUT"

# Resize, crop to exact dimensions, and optimize
# -resize 1200x630^: Resize maintaining aspect, larger dimension at least 1200
# -gravity Center: Center the image for cropping
# -extent 1200x630: Crop to exact dimensions
# -quality 85: JPEG quality 85% (good balance)
# -strip: Remove EXIF metadata
convert "$INPUT" \
    -resize "${DEFAULT_WIDTH}x${DEFAULT_HEIGHT}^" \
    -gravity Center \
    -extent "${DEFAULT_WIDTH}x${DEFAULT_HEIGHT}" \
    -quality "$DEFAULT_QUALITY" \
    -strip \
    "$OUTPUT"

# Verify output was created
if [ ! -f "$OUTPUT" ]; then
    echo "ERROR: Output image was not created" >&2
    exit 1
fi

# Get output file size for comparison
OUTPUT_SIZE=$(du -h "$OUTPUT" | cut -f1)

echo "Optimization complete:"
echo "  Input:  $INPUT_SIZE"
echo "  Output: $OUTPUT_SIZE"
echo "  Dimensions: ${DEFAULT_WIDTH}x${DEFAULT_HEIGHT}"
echo "  Quality: ${DEFAULT_QUALITY}%"

exit 0
