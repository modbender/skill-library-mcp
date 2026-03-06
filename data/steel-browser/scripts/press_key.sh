#!/usr/bin/env bash
# press_key.sh - Press a keyboard key or combination
# Usage: press_key.sh KEY
# Examples:
#   press_key.sh Enter
#   press_key.sh "Control+a"
#   press_key.sh "Control+Shift+t"
#   press_key.sh Tab
#   press_key.sh Escape

set -e

KEY="${1:?Usage: press_key.sh KEY  (e.g. Enter, Tab, Control+a)}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

python3 - <<EOF
import os, sys
HELPER = "$SCRIPT_DIR/_connect.py"
exec(open(HELPER).read())

try:
    page.keyboard.press("$KEY")
    print(f"Pressed: $KEY")
finally:
    cleanup()
EOF
