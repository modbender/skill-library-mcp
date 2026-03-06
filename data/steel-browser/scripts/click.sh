#!/usr/bin/env bash
# click.sh - Click an element by CSS/text selector in the Steel browser
# Usage: click.sh SELECTOR
# Examples:
#   click.sh "button:has-text('Sign in')"
#   click.sh "#submit-btn"
#   click.sh "text=Continue"
#   click.sh "[aria-label='Search']"

set -e

SELECTOR="${1:?Usage: click.sh SELECTOR}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

python3 - <<PYEOF
import os, sys
HELPER = "$SCRIPT_DIR/_connect.py"
exec(open(HELPER).read())

try:
    page.click("""$SELECTOR""")
    print(f"Clicked: $SELECTOR")
finally:
    cleanup()
PYEOF
