#!/usr/bin/env bash
# navigate.sh - Navigate to a URL in the Steel browser session
# Usage: navigate.sh URL [--wait-until load|domcontentloaded|networkidle]

set -e

URL="${1:?Usage: navigate.sh URL [WAIT_UNTIL]}"
WAIT_UNTIL="load"
[[ "${2}" == "networkidle" || "${2}" == "domcontentloaded" || "${2}" == "load" ]] && WAIT_UNTIL="${2}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

python3 - <<EOF
import os, sys
HELPER = "$SCRIPT_DIR/_connect.py"
exec(open(HELPER).read())

try:
    page.goto("$URL", wait_until="$WAIT_UNTIL")
    print(f"Navigated to: {page.url}")
    print(f"Title: {page.title()}")
finally:
    cleanup()
EOF
