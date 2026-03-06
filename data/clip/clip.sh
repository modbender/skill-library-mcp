#!/usr/bin/env bash
set -euo pipefail

# youtube-clipper: Download best quality from YouTube, clip a time range, save to ~/Desktop/Clips
# Requires: yt-dlp, ffmpeg

URL="" NAME="" START="" END=""
OUT_DIR="$HOME/Desktop/Clips"
WORK_DIR="/tmp/youtube-clipper"
mkdir -p "$OUT_DIR" "$WORK_DIR"

usage() { echo "Usage: $(basename "$0") --url <url> --start <sec> --end <sec> [--name <name>]"; }

while [[ $# -gt 0 ]]; do
  case "$1" in
    --url) URL="$2"; shift 2;;
    --start) START="$2"; shift 2;;
    --end) END="$2"; shift 2;;
    --name) NAME="$2"; shift 2;;
    -h|--help) usage; exit 0;;
    *) echo "Unknown: $1"; usage; exit 2;;
  esac
done

[[ -z "$URL" || -z "$START" || -z "$END" ]] && { usage; exit 2; }
command -v yt-dlp >/dev/null || { echo "yt-dlp not found"; exit 1; }
command -v ffmpeg >/dev/null || { echo "ffmpeg not found"; exit 1; }

if [[ -z "$NAME" ]]; then
  NAME=$(yt-dlp --get-title "$URL" 2>/dev/null | sed 's/[^a-zA-Z0-9 _-]/_/g; s/  */_/g; s/^_\|_$//g' | head -c 64)
  [[ -z "$NAME" ]] && NAME="clip"
fi

SRC="$WORK_DIR/${NAME}_source.mp4"
OUT="$OUT_DIR/${NAME}.mp4"
rm -f "$SRC"

echo "Downloading..."
yt-dlp --no-playlist -f "bv*+ba/b" --merge-output-format mp4 -o "$SRC" "$URL"
[[ ! -f "$SRC" ]] && { echo "Download failed"; exit 1; }

echo "Clipping..."
# ffmpeg -y -ss "$START" -to "$END" -i "$SRC" -c:v libx264 -preset veryfast -crf 23 -pix_fmt yuv420p -c:a aac -b:a 192k -movflags +faststart "$OUT"
ffmpeg -y -ss "$START" -to "$END" -i "$SRC" -c:v libx264 -preset medium -crf 23 -pix_fmt yuv420p -c:a aac -b:a 192k -movflags +faststart "$OUT"

rm -f "$SRC"
echo "Done: $OUT"
