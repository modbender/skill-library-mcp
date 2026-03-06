#!/usr/bin/env bash
# normalize-filenames.sh — Rename downloaded MP3s to clean "Artist - Title.mp3" format
#
# Usage: normalize-filenames.sh <directory> <tracklist.json>
#
# tracklist.json should be a JSON array of objects:
#   [{"artist": "Artist Name", "title": "Track Title"}, ...]
#
# The script fuzzy-matches each mp3 in the directory to a tracklist entry
# by searching for keywords from the artist/title in the filename.
# Unmatched files are left untouched.

set -euo pipefail

DIR="${1:?Usage: normalize-filenames.sh <directory> <tracklist.json>}"
TRACKLIST="${2:?Usage: normalize-filenames.sh <directory> <tracklist.json>}"

if [[ ! -d "$DIR" ]]; then
  echo "Error: directory '$DIR' not found" >&2
  exit 1
fi

if [[ ! -f "$TRACKLIST" ]]; then
  echo "Error: tracklist '$TRACKLIST' not found" >&2
  exit 1
fi

# Read tracklist entries
COUNT=$(jq length "$TRACKLIST")
RENAMED=0
SKIPPED=0

for i in $(seq 0 $((COUNT - 1))); do
  ARTIST=$(jq -r ".[$i].artist" "$TRACKLIST")
  TITLE=$(jq -r ".[$i].title" "$TRACKLIST")
  
  # Skip ID tracks
  if [[ "$ARTIST" == "ID" && "$TITLE" == "ID" ]]; then
    continue
  fi
  
  TARGET="${ARTIST} - ${TITLE}.mp3"
  
  # If target already exists, skip
  if [[ -f "$DIR/$TARGET" ]]; then
    ((SKIPPED++))
    continue
  fi
  
  # Extract keywords for fuzzy matching (longest word from artist + title)
  # Use the first artist name and key title words
  ARTIST_KEY=$(echo "$ARTIST" | awk -F'[,&]' '{print $1}' | xargs | tr '[:upper:]' '[:lower:]')
  TITLE_KEY=$(echo "$TITLE" | sed 's/([^)]*)//g' | xargs | tr '[:upper:]' '[:lower:]')
  
  MATCH=""
  for f in "$DIR"/*.mp3; do
    [[ ! -f "$f" ]] && continue
    BASENAME=$(basename "$f")
    [[ "$BASENAME" == *"Full Mix"* ]] && continue
    
    LOWER=$(echo "$BASENAME" | tr '[:upper:]' '[:lower:]')
    
    # Check if filename contains key parts of both artist and title
    if echo "$LOWER" | grep -qi "$ARTIST_KEY" && echo "$LOWER" | grep -qi "$TITLE_KEY"; then
      MATCH="$f"
      break
    fi
  done
  
  if [[ -n "$MATCH" ]]; then
    mv "$MATCH" "$DIR/$TARGET"
    echo "✅ $(basename "$MATCH") → $TARGET"
    ((RENAMED++))
  fi
done

echo ""
echo "Done: $RENAMED renamed, $SKIPPED already clean, $((COUNT - RENAMED - SKIPPED)) unmatched"
