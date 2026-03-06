#!/bin/bash
# Take a screenshot of a URL using headless Chromium
# Usage: bash screenshot.sh <url> <output_path> [width] [height]

URL="${1:?Usage: screenshot.sh <url> <output_path> [width] [height]}"
OUTPUT="${2:?Output path required}"
WIDTH="${3:-1400}"
HEIGHT="${4:-900}"

# Use a temp HTML that loads the target in an iframe after delay,
# or use virtual-time-budget to let JS execute
chromium --headless --disable-gpu --no-sandbox --disable-dev-shm-usage \
  --window-size="${WIDTH},${HEIGHT}" \
  --screenshot="$OUTPUT" \
  --hide-scrollbars \
  --virtual-time-budget=5000 \
  "$URL" 2>/dev/null

if [ -f "$OUTPUT" ]; then
  echo "Screenshot saved to: $OUTPUT"
else
  echo "ERROR: Screenshot failed" >&2
  exit 1
fi
