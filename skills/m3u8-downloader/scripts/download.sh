#!/bin/bash
# M3U8 Video Downloader
# Usage: ./download.sh <m3u8_url> [output_name]

set -e

M3U8_URL="$1"
OUTPUT_NAME="${2:-video_$(date +%Y%m%d_%H%M%S)}"
WORK_DIR="$HOME/Downloads/m3u8_${OUTPUT_NAME}"
OUTPUT_FILE="$HOME/Downloads/${OUTPUT_NAME}.mp4"

if [ -z "$M3U8_URL" ]; then
    echo "Usage: $0 <m3u8_url> [output_name]"
    exit 1
fi

# Check dependencies
command -v aria2c >/dev/null 2>&1 || { echo "aria2c required. Install: brew install aria2"; exit 1; }
command -v ffmpeg >/dev/null 2>&1 || { echo "ffmpeg required. Install: brew install ffmpeg"; exit 1; }

echo "🎬 M3U8 Downloader"
echo "URL: $M3U8_URL"
echo "Output: $OUTPUT_FILE"
echo ""

mkdir -p "$WORK_DIR"
cd "$WORK_DIR"

# Step 1: Fetch master playlist
echo "📋 Fetching playlist..."
MASTER=$(curl -sL "$M3U8_URL")
BASE_URL=$(dirname "$M3U8_URL")

# Check if it's a master playlist pointing to another m3u8
NESTED=$(echo "$MASTER" | grep -E "\.m3u8$" | head -1)
if [ -n "$NESTED" ]; then
    if [[ "$NESTED" == /* ]]; then
        # Absolute path
        PROTOCOL=$(echo "$M3U8_URL" | grep -oE "^https?://[^/]+")
        PLAYLIST_URL="${PROTOCOL}${NESTED}"
    elif [[ "$NESTED" == http* ]]; then
        PLAYLIST_URL="$NESTED"
    else
        PLAYLIST_URL="${BASE_URL}/${NESTED}"
    fi
    echo "Found nested playlist: $PLAYLIST_URL"
    PLAYLIST=$(curl -sL "$PLAYLIST_URL")
    BASE_URL=$(dirname "$PLAYLIST_URL")
else
    PLAYLIST="$MASTER"
    PLAYLIST_URL="$M3U8_URL"
fi

echo "$PLAYLIST" > playlist.m3u8

# Step 2: Get encryption key if present
KEY_LINE=$(echo "$PLAYLIST" | grep "EXT-X-KEY" | head -1)
if [ -n "$KEY_LINE" ]; then
    KEY_URI=$(echo "$KEY_LINE" | grep -oE 'URI="[^"]+"' | sed 's/URI="//;s/"$//')
    if [ -n "$KEY_URI" ]; then
        if [[ "$KEY_URI" == http* ]]; then
            KEY_URL="$KEY_URI"
        else
            KEY_URL="${BASE_URL}/${KEY_URI}"
        fi
        echo "🔑 Downloading encryption key from: $KEY_URL"
        curl -sL "$KEY_URL" -o enc.key
    fi
fi

# Step 3: Extract segment URLs
echo "📦 Extracting segment URLs..."
echo "$PLAYLIST" | grep -E "^https?://" > urls.txt || true

# If segments are relative paths
if [ ! -s urls.txt ]; then
    echo "$PLAYLIST" | grep -E "\.ts$" | while read -r line; do
        if [[ "$line" == /* ]]; then
            PROTOCOL=$(echo "$PLAYLIST_URL" | grep -oE "^https?://[^/]+")
            echo "${PROTOCOL}${line}"
        elif [[ "$line" == http* ]]; then
            echo "$line"
        else
            echo "${BASE_URL}/${line}"
        fi
    done > urls.txt
fi

TOTAL=$(wc -l < urls.txt | tr -d ' ')
echo "Found $TOTAL segments"

# Step 4: Parallel download
echo "⬇️  Downloading segments (16 threads)..."
aria2c -i urls.txt -j 16 -x 16 -s 16 --file-allocation=none --auto-file-renaming=false -c true --console-log-level=warn

# Step 5: Verify downloads
DOWNLOADED=$(ls *.ts 2>/dev/null | wc -l | tr -d ' ')
echo "Downloaded: $DOWNLOADED / $TOTAL segments"

if [ "$DOWNLOADED" -lt "$TOTAL" ]; then
    echo "⚠️  Warning: Some segments missing. Retrying..."
    aria2c -i urls.txt -j 16 -x 16 -s 16 --file-allocation=none --auto-file-renaming=false -c true --console-log-level=warn
fi

# Step 6: Merge with ffmpeg
echo "🔧 Merging segments..."

# Create local m3u8 pointing to downloaded files
if [ -f enc.key ]; then
    # Encrypted - need to create local playlist with key reference
    sed "s|URI=\"[^\"]*\"|URI=\"enc.key\"|g" playlist.m3u8 > local_playlist.m3u8
    # Replace remote URLs with local filenames
    for ts in *.ts; do
        sed -i '' "s|.*/${ts}|${ts}|g" local_playlist.m3u8 2>/dev/null || \
        sed -i "s|.*/${ts}|${ts}|g" local_playlist.m3u8
    done
    ffmpeg -y -allowed_extensions ALL -i local_playlist.m3u8 -c copy -bsf:a aac_adtstoasc "$OUTPUT_FILE"
else
    # No encryption - simple concat
    ls -v *.ts | sed "s/^/file '/" | sed "s/$/'/" > filelist.txt
    ffmpeg -y -f concat -safe 0 -i filelist.txt -c copy -bsf:a aac_adtstoasc "$OUTPUT_FILE"
fi

# Cleanup
echo "🧹 Cleaning up..."
rm -rf "$WORK_DIR"

echo ""
echo "✅ Done! Video saved to: $OUTPUT_FILE"
ls -lh "$OUTPUT_FILE"
