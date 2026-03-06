#!/bin/bash
# webp-compress.sh - Compress images to webp format for web upload

if [ $# -lt 2 ]; then
    echo "Usage: $0 <input-file> <output-file>"
    echo "Example: $0 photo.png photo.webp"
    exit 1
fi

INPUT="$1"
OUTPUT="$2"

if [ ! -f "$INPUT" ]; then
    echo "Error: Input file '$INPUT' not found"
    exit 1
fi

# Convert to webp (ImageMagick)
convert "$INPUT" "$OUTPUT"

# Show compression results
INPUT_SIZE=$(du -h "$INPUT" | cut -f1)
OUTPUT_SIZE=$(du -h "$OUTPUT" | cut -f1)

echo "Compressed: $INPUT ($INPUT_SIZE) -> $OUTPUT ($OUTPUT_SIZE)"
