#!/bin/bash
# Convert any image to compressed .webp format
# Usage: bash convert-image.sh <input> [output] [quality]
# Quality: 0-100 (default: 80)

INPUT="${1:?Usage: convert-image.sh <input> [output] [quality]}"
QUALITY="${3:-80}"

# Derive output name if not provided
if [ -z "$2" ]; then
  OUTPUT="${INPUT%.*}.webp"
else
  OUTPUT="$2"
fi

# Get original file size
ORIG_SIZE=$(stat -f%z "$INPUT" 2>/dev/null || stat -c%s "$INPUT" 2>/dev/null)

# Convert to webp
cwebp -q "$QUALITY" "$INPUT" -o "$OUTPUT" 2>/dev/null

if [ -f "$OUTPUT" ]; then
  NEW_SIZE=$(stat -f%z "$OUTPUT" 2>/dev/null || stat -c%s "$OUTPUT" 2>/dev/null)
  SAVINGS=$(( (ORIG_SIZE - NEW_SIZE) * 100 / ORIG_SIZE ))
  echo "Converted: $INPUT -> $OUTPUT"
  echo "Original: $(numfmt --to=iec $ORIG_SIZE) -> Compressed: $(numfmt --to=iec $NEW_SIZE) (${SAVINGS}% smaller)"
else
  echo "ERROR: Conversion failed" >&2
  exit 1
fi
