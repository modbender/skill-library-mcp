#!/bin/bash
# List all images in a directory
# Usage: list_all.sh [directory]

DIR="${1:-$HOME}"

echo "Finding all images in: $DIR"
echo ""

# Try mdfind first, fallback to find
if command -v mdfind &> /dev/null; then
    RESULT=$(mdfind -onlyin "$DIR" "kMDItemContentTypeTree == 'public.image'" 2>/dev/null)
    if [ -n "$RESULT" ]; then
        echo "$RESULT"
        exit 0
    fi
fi

# Fallback to find
find "$DIR" -type f \( -iname "*.jpg" -o -iname "*.jpeg" -o -iname "*.png" -o -iname "*.heic" -o -iname "*.webp" -o -iname "*.gif" -o -iname "*.tiff" -o -iname "*.raw" \) 2>/dev/null
