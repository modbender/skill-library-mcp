#!/bin/bash
# Copy search results to destination folder
# Usage: cat results.txt | copy_results.sh <destination_folder>

DEST="$1"

if [ -z "$DEST" ]; then
    echo "Usage: cat search_results.txt | $0 <destination_folder>"
    exit 1
fi

mkdir -p "$DEST"

while IFS= read -r file; do
    if [ -f "$file" ]; then
        cp "$file" "$DEST/"
        echo "Copied: $(basename "$file")"
    fi
done

echo ""
echo "Files copied to: $DEST"
