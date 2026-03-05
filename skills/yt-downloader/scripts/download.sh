#!/bin/bash
# YouTube Downloader Script
# Usage: ./download.sh "YOUTUBE_URL" ["optional-label"]

set -e

URL="$1"
LABEL="${2:-video}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT_DIR="$HOME/.openclaw/workspace/assets/videos"
REGISTRY="$HOME/.openclaw/workspace/assets/registry.json"

# Create output directory if needed
mkdir -p "$OUTPUT_DIR"

# Extract video ID
if [[ "$URL" == *"youtu.be/"* ]]; then
    VIDEO_ID=$(echo "$URL" | sed 's/.*youtu\.be\///' | sed 's/\?.*//')
elif [[ "$URL" == *"youtube.com/watch"* ]]; then
    VIDEO_ID=$(echo "$URL" | sed 's/.*v=//' | sed 's/&.*//')
elif [[ "$URL" == *"youtube.com/shorts/"* ]]; then
    VIDEO_ID=$(echo "$URL" | sed 's/.*shorts\///' | sed 's/\?.*//')
else
    echo "ERROR: Invalid YouTube URL"
    exit 1
fi

# Sanitize label (remove special chars, replace spaces with underscores)
SAFE_LABEL=$(echo "$LABEL" | tr ' ' '_' | tr -cd '[:alnum:]_-')

# Output filename
FILENAME="${SAFE_LABEL}_${VIDEO_ID}_${TIMESTAMP}.mp4"
OUTPUT_PATH="$OUTPUT_DIR/$FILENAME"

echo "Downloading: $URL"
echo "Video ID: $VIDEO_ID"
echo "Label: $LABEL"
echo "Output: $OUTPUT_PATH"

# Download with yt-dlp at best quality
# -f: best video+audio merged, prefer mp4
# --merge-output-format: ensure mp4 output
yt-dlp \
    -f "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best" \
    --merge-output-format mp4 \
    -o "$OUTPUT_PATH" \
    --no-playlist \
    --no-warnings \
    "$URL"

# Check if download succeeded
if [ ! -f "$OUTPUT_PATH" ]; then
    echo "ERROR: Download failed"
    exit 1
fi

# Get file size
FILESIZE=$(du -h "$OUTPUT_PATH" | cut -f1)

# Initialize registry if needed
if [ ! -f "$REGISTRY" ]; then
    echo '{"assets":[]}' > "$REGISTRY"
fi

# Add to registry using jq if available, otherwise append manually
if command -v jq &> /dev/null; then
    TEMP_FILE=$(mktemp)
    jq --arg type "video" \
       --arg source "youtube" \
       --arg videoId "$VIDEO_ID" \
       --arg label "$LABEL" \
       --arg filename "$FILENAME" \
       --arg path "$OUTPUT_PATH" \
       --arg url "$URL" \
       --arg downloadedAt "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
       --arg filesize "$FILESIZE" \
       '.assets += [{type: $type, source: $source, videoId: $videoId, label: $label, filename: $filename, path: $path, url: $url, downloadedAt: $downloadedAt, filesize: $filesize}]' \
       "$REGISTRY" > "$TEMP_FILE" && mv "$TEMP_FILE" "$REGISTRY"
else
    # Fallback: just note the download
    echo "Registry update requires jq. Asset saved but not registered."
fi

echo ""
echo "=== DOWNLOAD COMPLETE ==="
echo "File: $FILENAME"
echo "Path: $OUTPUT_PATH"
echo "Size: $FILESIZE"
echo "========================="
