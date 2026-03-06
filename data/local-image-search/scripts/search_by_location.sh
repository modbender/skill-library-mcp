#!/bin/bash
# Search images by GPS location
# Usage: search_by_location.sh [directory]

DIR="${1:-$HOME}"

echo "Images with GPS coordinates in: $DIR"
echo ""

mdfind -onlyin "$DIR" "kMDItemContentTypeTree == 'public.image' && kMDItemGPSStatus == 'GPS'"
