#!/bin/bash
# Fetch YouTube transcript using direct API call

VIDEO_URL="$1"
LANG="${2:-en}"

if [ -z "$VIDEO_URL" ]; then
  echo "Usage: yt-transcript.sh <youtube-url-or-id> [language]" >&2
  exit 1
fi

# Extract video ID
if [[ "$VIDEO_URL" =~ (v=|youtu\.be/)([a-zA-Z0-9_-]{11}) ]]; then
  VIDEO_ID="${BASH_REMATCH[2]}"
else
  VIDEO_ID="$VIDEO_URL"
fi

# Fetch video page and extract caption track URL
PAGE=$(curl -s "https://www.youtube.com/watch?v=$VIDEO_ID")

# Extract caption track URL from the page
CAPTION_URL=$(echo "$PAGE" | grep -oP '"captionTracks":\[{"baseUrl":"[^"]+' | head -1 | sed 's/.*baseUrl":"//;s/\\u0026/\&/g')

if [ -z "$CAPTION_URL" ]; then
  echo "No captions found for video: $VIDEO_ID" >&2
  exit 1
fi

# Fetch the transcript XML
TRANSCRIPT=$(curl -s "$CAPTION_URL")

# Parse XML and output with timestamps
echo "$TRANSCRIPT" | grep -oP '<text start="[^"]*" dur="[^"]*">[^<]*</text>' | while read -r line; do
  START=$(echo "$line" | grep -oP 'start="[^"]*"' | grep -oP '[0-9.]+')
  TEXT=$(echo "$line" | sed 's/<[^>]*>//g' | sed 's/&amp;/\&/g;s/&lt;/</g;s/&gt;/>/g;s/&#39;/'"'"'/g;s/&quot;/"/g')
  
  MINS=$(echo "$START" | awk '{printf "%d", $1/60}')
  SECS=$(echo "$START" | awk '{printf "%02d", int($1)%60}')
  
  echo "[$MINS:$SECS] $TEXT"
done
