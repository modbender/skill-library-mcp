#!/bin/bash
# Export PDF from a note (convenience wrapper for attachment extraction)
# Usage: notes-export-pdf.sh <note-name> [folder]
# Outputs just the path to the extracted PDF for easy piping

source "$(dirname "$0")/_resolve_folder.sh"

NAME="${1:-}"
FOLDER="${2:-}"
OUTPUT_DIR="/tmp/notes-export/"

if [ -z "$NAME" ]; then
    echo "Usage: notes-export-pdf.sh <note-name> [folder]"
    exit 1
fi

# Run attachment extraction silently
"$(dirname "$0")/notes-attachment.sh" "$NAME" "$FOLDER" "$OUTPUT_DIR" > /dev/null 2>&1

if [ $? -ne 0 ]; then
    exit 1
fi

# Find the PDF file in output directory
PDF_FILE=$(ls -t "$OUTPUT_DIR"/*.pdf 2>/dev/null | head -1)

if [ -n "$PDF_FILE" ]; then
    echo "$PDF_FILE"
else
    echo "Error: No PDF found for note '$NAME'" >&2
    exit 1
fi
