#!/usr/bin/env bash
# screenshot.sh - Take a screenshot of the current page
# Usage: screenshot.sh [OUTPUT_FILE] [--full-page]
# Default output: /tmp/steel_screenshot.png

set -e

OUTPUT="/tmp/steel_screenshot.png"
FULL_PAGE=false

for arg in "$@"; do
  case "$arg" in
    --full-page) FULL_PAGE=true ;;
    *.png|*.jpg) OUTPUT="$arg" ;;
  esac
done

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

python3 - <<EOF
import os, sys
HELPER = "$SCRIPT_DIR/_connect.py"
exec(open(HELPER).read())

try:
    full_page = "$FULL_PAGE" == "true"
    page.screenshot(path="$OUTPUT", full_page=full_page)
    print(f"Screenshot saved to: $OUTPUT")
finally:
    cleanup()
EOF
