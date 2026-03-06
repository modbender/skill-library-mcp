#!/bin/bash

# YouTube Transcript Extractor
# Extracts and cleans transcript from YouTube video URL

set -e

if [ $# -eq 0 ]; then
    echo "Usage: $0 <youtube-url> [output-file]"
    echo "Example: $0 'https://www.youtube.com/watch?v=dQw4w9WgXcQ' transcript.txt"
    exit 1
fi

VIDEO_URL="$1"
OUTPUT_FILE="${2:-transcript.txt}"

# Check if yt-dlp exists
if ! command -v yt-dlp &> /dev/null; then
    # Try to find it in home directory
    if [ -f "$HOME/yt-dlp" ]; then
        YT_DLP="$HOME/yt-dlp"
    else
        echo "Error: yt-dlp not found. Installing to ~/yt-dlp..."
        curl -L https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp -o "$HOME/yt-dlp"
        chmod +x "$HOME/yt-dlp"
        YT_DLP="$HOME/yt-dlp"
    fi
else
    YT_DLP="yt-dlp"
fi

echo "Extracting transcript from: $VIDEO_URL"

# Extract transcript as VTT subtitle file
$YT_DLP --write-auto-sub --write-sub --sub-lang en --skip-download --sub-format vtt "$VIDEO_URL" -o "temp_transcript" --quiet 2>/dev/null || {
    echo "Warning: Some warnings occurred during extraction, but continuing..."
}

# Check if transcript was extracted
if [ ! -f "temp_transcript.en.vtt" ]; then
    echo "Error: Failed to extract transcript. Video may not have captions available."
    exit 1
fi

echo "Cleaning transcript..."

# Clean up the VTT format to extract just the text
grep -v "^[0-9]" temp_transcript.en.vtt | \
grep -v "^WEBVTT" | \
grep -v "^Kind:" | \
grep -v "^Language:" | \
grep -v "^\s*$" | \
grep -v "align:start" | \
sed 's/<[^>]*>//g' | \
tr '\n' ' ' | \
sed 's/  */ /g' | \
sed 's/^ *//g' | \
sed 's/ *$//g' > "$OUTPUT_FILE"

# Clean up temporary file
rm -f temp_transcript.en.vtt

echo "Transcript saved to: $OUTPUT_FILE"
echo "Character count: $(wc -c < "$OUTPUT_FILE")"

# Show first few lines as preview
echo -e "\nPreview:"
head -c 200 "$OUTPUT_FILE"
echo -e "...\n"