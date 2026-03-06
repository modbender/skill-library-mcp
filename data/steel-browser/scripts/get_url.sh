#!/usr/bin/env bash
# get_url.sh - Get current page URL and title
# Usage: get_url.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

python3 - <<EOF
import os, sys
HELPER = "$SCRIPT_DIR/_connect.py"
exec(open(HELPER).read())

try:
    print(f"URL={page.url}")
    print(f"TITLE={page.title()}")
finally:
    cleanup()
EOF
