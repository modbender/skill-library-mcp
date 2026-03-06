#!/usr/bin/env bash
# click_coords.sh - Click at pixel coordinates (fallback when selector isn't available)
# Usage: click_coords.sh X Y [--right] [--double]

set -e

X="${1:?Usage: click_coords.sh X Y}"
Y="${2:?Usage: click_coords.sh X Y}"
BUTTON="left"
CLICK_COUNT=1

shift 2
for arg in "$@"; do
  case "$arg" in
    --right)  BUTTON="right" ;;
    --double) CLICK_COUNT=2 ;;
  esac
done

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

python3 - <<EOF
import os, sys
HELPER = "$SCRIPT_DIR/_connect.py"
exec(open(HELPER).read())

try:
    page.mouse.click(int("$X"), int("$Y"), button="$BUTTON", click_count=$CLICK_COUNT)
    print(f"Clicked at ($X, $Y) button=$BUTTON count=$CLICK_COUNT")
finally:
    cleanup()
EOF
