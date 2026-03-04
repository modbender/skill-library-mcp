#!/usr/bin/env bash
# Resize and reformat a video to a target aspect ratio using ffmpeg (local, no API key).
#
# Crops the video to fill the target ratio (center crop), then scales to the
# standard resolution for that ratio. Safe for all common input sizes.
#
# Usage: resize.sh <input> <ratio> [output]
#
# Args:
#   input:  Path to source video
#   ratio:  Target aspect ratio: "9:16" | "1:1" | "16:9" | "4:3" | "21:9"
#   output: (optional) Output path (default: <input_name>_<ratio>.<ext>)
#
# Output resolutions:
#   9:16  → 1080x1920  (TikTok, Reels, Shorts)
#   1:1   → 1080x1080  (Instagram square)
#   16:9  → 1920x1080  (YouTube, landscape)
#   4:3   → 1440x1080
#   21:9  → 2560x1080  (cinematic ultrawide)
#
# Exit codes: 0=success, 1=bad args, 2=ffmpeg error

set -euo pipefail

# ---------------------------------------------------------------------------
# Validate dependencies
# ---------------------------------------------------------------------------
if ! command -v ffmpeg &>/dev/null; then
  echo "Error: ffmpeg is not installed. Install with: brew install ffmpeg" >&2
  exit 1
fi

# ---------------------------------------------------------------------------
# Validate arguments
# ---------------------------------------------------------------------------
if [[ $# -lt 2 ]]; then
  echo "Usage: resize.sh <input> <ratio> [output]" >&2
  echo "  Ratios: 9:16  1:1  16:9  4:3  21:9" >&2
  echo "  Example: resize.sh video.mp4 9:16" >&2
  exit 1
fi

INPUT="$1"
RATIO="$2"
OUTPUT="${3:-}"

if [[ ! -f "$INPUT" ]]; then
  echo "Error: File not found: $INPUT" >&2
  exit 1
fi

# ---------------------------------------------------------------------------
# Map ratio to target width x height
# ---------------------------------------------------------------------------
case "$RATIO" in
  "9:16")  TW=1080; TH=1920 ;;
  "1:1")   TW=1080; TH=1080 ;;
  "16:9")  TW=1920; TH=1080 ;;
  "4:3")   TW=1440; TH=1080 ;;
  "21:9")  TW=2560; TH=1080 ;;
  *)
    echo "Error: Unsupported ratio '$RATIO'. Supported: 9:16  1:1  16:9  4:3  21:9" >&2
    exit 1
    ;;
esac

# Derive default output path (replace ":" with "-" for filename safety)
if [[ -z "$OUTPUT" ]]; then
  BASE="${INPUT%.*}"
  EXT="${INPUT##*.}"
  RATIO_SAFE="${RATIO/:/-}"
  OUTPUT="${BASE}_${RATIO_SAFE}.${EXT}"
fi

# ---------------------------------------------------------------------------
# Center-crop + scale via ffmpeg crop/scale filter chain
#
# Strategy:
#   1. crop to exact target AR from center of input frame
#   2. scale to target resolution
# The crop formula keeps the largest possible region with the correct AR.
# ---------------------------------------------------------------------------
echo "Resizing: $INPUT → ${TW}x${TH} (${RATIO})  output: $OUTPUT" >&2

ffmpeg -y -loglevel error -stats \
  -i "$INPUT" \
  -vf "crop='if(gt(iw/ih,${TW}/${TH}),ih*${TW}/${TH},iw)':'if(gt(iw/ih,${TW}/${TH}),ih,iw*${TH}/${TW})',scale=${TW}:${TH}" \
  -c:v libx264 -crf 18 -preset fast \
  -c:a aac -b:a 192k \
  "$OUTPUT"

echo "Done: $OUTPUT" >&2
echo "$OUTPUT"
