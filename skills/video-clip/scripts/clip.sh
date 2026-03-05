#!/usr/bin/env bash
# Trim a video to a specified time range using ffmpeg (local, no API key needed).
#
# Usage: clip.sh <input> <start> <end> [output]
#
# Args:
#   input:   Path to source video (mp4, mov, mkv, ...)
#   start:   Start time — HH:MM:SS, MM:SS, or seconds (e.g. "1:30", "90", "0:01:30")
#   end:     End time or duration — same format, OR "+Ns" for relative duration
#            e.g. "3:00" = cut until 3:00 | "+120" = take 120s from start
#   output:  (optional) Output file path (default: <input_name>_clip.<ext>)
#
# Examples:
#   clip.sh video.mp4 "1:30" "3:00"               # 1:30 → 3:00
#   clip.sh video.mp4 "0" "+120"                   # first 120 seconds
#   clip.sh video.mp4 "5:00" "7:30" highlight.mp4  # with custom output name
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
if [[ $# -lt 3 ]]; then
  echo "Usage: clip.sh <input> <start> <end_or_+duration> [output]" >&2
  echo "  Examples:" >&2
  echo "    clip.sh video.mp4 '1:30' '3:00'           # trim 1:30-3:00" >&2
  echo "    clip.sh video.mp4 '0' '+120'               # first 2 minutes" >&2
  exit 1
fi

INPUT="$1"
START="$2"
END="$3"
OUTPUT="${4:-}"

if [[ ! -f "$INPUT" ]]; then
  echo "Error: File not found: $INPUT" >&2
  exit 1
fi

# Derive default output path
if [[ -z "$OUTPUT" ]]; then
  BASE="${INPUT%.*}"
  EXT="${INPUT##*.}"
  OUTPUT="${BASE}_clip.${EXT}"
fi

# ---------------------------------------------------------------------------
# Build ffmpeg command
# Duration mode: end starts with "+" → treat as duration seconds
# ---------------------------------------------------------------------------
if [[ "$END" == +* ]]; then
  DURATION="${END:1}"  # strip leading "+"
  echo "Clipping: $INPUT  [$START + ${DURATION}s] → $OUTPUT" >&2
  ffmpeg -y -loglevel error -stats \
    -ss "$START" -i "$INPUT" \
    -t "$DURATION" \
    -c copy \
    "$OUTPUT"
else
  echo "Clipping: $INPUT  [$START → $END] → $OUTPUT" >&2
  ffmpeg -y -loglevel error -stats \
    -ss "$START" -to "$END" -i "$INPUT" \
    -c copy \
    "$OUTPUT"
fi

echo "Done: $OUTPUT" >&2
echo "$OUTPUT"
