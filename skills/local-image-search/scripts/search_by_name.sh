#!/bin/bash
# Search images by filename pattern
# Usage: search_by_name.sh <pattern> [directory]

PATTERN="$1"
DIR="${2:-$HOME}"

if [ -z "$PATTERN" ]; then
    echo "Usage: $0 <pattern> [directory]"
    echo "Example: $0 'screenshot' ~/Desktop"
    exit 1
fi

# Check if fd is available
if command -v fd &> /dev/null; then
    fd -e jpg -e jpeg -e png -e heic -e webp -e gif -e tiff -e raw "$PATTERN" "$DIR"
else
    # Fallback to find + grep
    find "$DIR" -type f \( -iname "*.jpg" -o -iname "*.jpeg" -o -iname "*.png" -o -iname "*.heic" -o -iname "*.webp" -o -iname "*.gif" -o -iname "*.tiff" -o -iname "*.raw" \) 2>/dev/null | grep -i "$PATTERN"
fi
