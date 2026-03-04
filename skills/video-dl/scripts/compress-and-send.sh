#!/bin/bash
# Compress video for Telegram and notify when done
# Usage: compress-and-send.sh <input_file> <chat_id>

INPUT="$1"
CHAT_ID="$2"
MAX_SIZE_MB=15  # Leave margin under 16MB limit

if [ -z "$INPUT" ] || [ -z "$CHAT_ID" ]; then
    echo "Usage: compress-and-send.sh <input_file> <chat_id>"
    exit 1
fi

# Get duration for time estimate
DURATION=$(ffprobe -v quiet -show_entries format=duration -of csv=p=0 "$INPUT" 2>/dev/null | cut -d. -f1)
ESTIMATE=$((DURATION / 4))  # ~4x realtime with ultrafast

OUTPUT="${INPUT%.*}-telegram.mp4"

echo "Compressing: $INPUT"
echo "Estimated time: ~${ESTIMATE}s"

# Compress with aggressive settings for Telegram
ffmpeg -i "$INPUT" \
    -c:v libx264 -preset ultrafast -crf 38 \
    -vf "scale=480:-2" \
    -c:a aac -b:a 32k \
    -y "$OUTPUT" 2>/dev/null

if [ $? -eq 0 ]; then
    SIZE=$(stat -f%z "$OUTPUT" 2>/dev/null || stat -c%s "$OUTPUT" 2>/dev/null)
    SIZE_MB=$((SIZE / 1024 / 1024))
    
    if [ $SIZE_MB -le $MAX_SIZE_MB ]; then
        echo "SUCCESS:$OUTPUT"
    else
        echo "ERROR:File still too large (${SIZE_MB}MB)"
    fi
else
    echo "ERROR:Compression failed"
fi
