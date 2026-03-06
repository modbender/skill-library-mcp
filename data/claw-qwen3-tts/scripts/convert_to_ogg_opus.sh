#!/usr/bin/env bash
# convert_to_ogg_opus.sh — Convert any audio file to OGG/Opus format
# Required for Telegram & WhatsApp PTT voice messages
set -euo pipefail

if [ $# -lt 2 ]; then
    echo "Usage: $0 <input_file> <output_file.ogg>"
    echo ""
    echo "Converts any audio file to OGG/Opus format suitable for"
    echo "Telegram and WhatsApp voice messages (PTT)."
    exit 1
fi

INPUT="$1"
OUTPUT="$2"
BITRATE="${3:-64k}"

if [ ! -f "$INPUT" ]; then
    echo "[ERROR] Input file not found: $INPUT"
    exit 1
fi

if ! command -v ffmpeg &>/dev/null; then
    echo "[ERROR] ffmpeg is not installed"
    exit 1
fi

echo "[INFO] Converting: $INPUT → $OUTPUT (OGG/Opus, ${BITRATE})"

ffmpeg -y -i "$INPUT" \
    -c:a libopus \
    -b:a "$BITRATE" \
    -vbr on \
    -compression_level 10 \
    -frame_duration 20 \
    -application voip \
    "$OUTPUT" \
    2>/dev/null

if [ -f "$OUTPUT" ]; then
    SIZE=$(du -h "$OUTPUT" | cut -f1)
    echo "[OK] Converted: $OUTPUT ($SIZE)"
else
    echo "[ERROR] Conversion failed"
    exit 1
fi
