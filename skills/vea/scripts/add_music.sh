#!/bin/bash
# Add background music to a video using Soundstripe
# Usage: ./add_music.sh <input_video> <output_video> [track_id]

set -e

INPUT_VIDEO="${1:?Usage: $0 <input_video> <output_video> [track_id]}"
OUTPUT_VIDEO="${2:?Usage: $0 <input_video> <output_video> [track_id]}"
TRACK_ID="${3:-18022}"  # Default: "Get Hype" (high energy hip-hop)

VEA_DIR="${VEA_DIR:-$HOME/vea}"
CONFIG="$VEA_DIR/config.json"

# Get API key
SOUNDSTRIPE_KEY=$(jq -r '.api_keys.SOUNDSTRIPE_KEY' "$CONFIG")
if [ -z "$SOUNDSTRIPE_KEY" ] || [ "$SOUNDSTRIPE_KEY" = "null" ]; then
    echo "Error: SOUNDSTRIPE_KEY not found in $CONFIG"
    exit 1
fi

# Get track download URL
echo "Fetching track $TRACK_ID from Soundstripe..."
TRACK_INFO=$(curl -s "https://api.soundstripe.com/v1/songs/$TRACK_ID" \
    -H "accept: application/json" \
    -H "Authorization: Token $SOUNDSTRIPE_KEY")

MUSIC_URL=$(echo "$TRACK_INFO" | jq -r '.included[0].attributes.versions.mp3')
TRACK_TITLE=$(echo "$TRACK_INFO" | jq -r '.data.attributes.title')

if [ -z "$MUSIC_URL" ] || [ "$MUSIC_URL" = "null" ]; then
    echo "Error: Could not get download URL for track $TRACK_ID"
    exit 1
fi

echo "Downloading: $TRACK_TITLE"

# Download music to temp file
MUSIC_FILE=$(mktemp --suffix=.mp3)
curl -sL "$MUSIC_URL" -o "$MUSIC_FILE"

# Get video duration for fade timing
DURATION=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$INPUT_VIDEO")
FADE_START=$(echo "$DURATION - 4" | bc)

echo "Mixing music with video (volume=18%, fade out at ${FADE_START}s)..."

# Mix audio
ffmpeg -y \
    -i "$INPUT_VIDEO" \
    -i "$MUSIC_FILE" \
    -filter_complex "[1:a]volume=0.18,afade=t=out:st=$FADE_START:d=4[music];[0:a][music]amix=inputs=2:duration=first:dropout_transition=2[aout]" \
    -map 0:v \
    -map "[aout]" \
    -c:v copy \
    -c:a aac -b:a 192k \
    -shortest \
    "$OUTPUT_VIDEO"

# Cleanup
rm -f "$MUSIC_FILE"

echo "Done: $OUTPUT_VIDEO"
echo "Music: $TRACK_TITLE (Soundstripe ID: $TRACK_ID)"
