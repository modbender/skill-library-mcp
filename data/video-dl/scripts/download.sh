#!/bin/bash
# Video downloader using yt-dlp
# Usage: download.sh "URL" [OPTIONS]

set -e

URL="$1"
shift || true

if [ -z "$URL" ]; then
    echo "Error: No URL provided"
    echo "Usage: download.sh URL [--audio-only] [--720p] [--1080p] [--output DIR] [--filename NAME]"
    exit 1
fi

# Defaults
OUTPUT_DIR="$HOME/Downloads/videos"
FORMAT="bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best"
AUDIO_ONLY=false
CUSTOM_FILENAME=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --audio-only)
            AUDIO_ONLY=true
            shift
            ;;
        --720p)
            FORMAT="bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=720]+bestaudio/best[height<=720]"
            shift
            ;;
        --1080p)
            FORMAT="bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=1080]+bestaudio/best[height<=1080]"
            shift
            ;;
        --output)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        --filename)
            CUSTOM_FILENAME="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Build output template
if [ -n "$CUSTOM_FILENAME" ]; then
    OUTPUT_TEMPLATE="$OUTPUT_DIR/$CUSTOM_FILENAME.%(ext)s"
else
    OUTPUT_TEMPLATE="$OUTPUT_DIR/%(title).100s-%(id)s.%(ext)s"
fi

# Use user-installed yt-dlp if available (more up to date)
YTDLP="yt-dlp"
if [ -x "$HOME/.local/bin/yt-dlp" ]; then
    YTDLP="$HOME/.local/bin/yt-dlp"
fi

# Build command
CMD=($YTDLP --no-playlist --merge-output-format mp4)

if [ "$AUDIO_ONLY" = true ]; then
    CMD+=(--extract-audio --audio-format mp3 --audio-quality 0)
else
    CMD+=(--format "$FORMAT")
fi

CMD+=(--output "$OUTPUT_TEMPLATE")
CMD+=("$URL")

# Run download
echo "Downloading: $URL"
echo "Output: $OUTPUT_DIR"
echo ""

"${CMD[@]}" 2>&1

# Find the downloaded file (most recent in output dir)
DOWNLOADED=$(ls -t "$OUTPUT_DIR" 2>/dev/null | head -1)
if [ -n "$DOWNLOADED" ]; then
    FULL_PATH="$OUTPUT_DIR/$DOWNLOADED"
    echo ""
    echo "✓ Downloaded: $FULL_PATH"
    echo "MEDIA:$FULL_PATH"
fi
