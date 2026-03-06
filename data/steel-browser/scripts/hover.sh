#!/usr/bin/env bash
# hover.sh - Hover over an element by selector
# Usage: hover.sh SELECTOR

set -e

SELECTOR="${1:?Usage: hover.sh SELECTOR}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

python3 - <<PYEOF
import os, sys
HELPER = "$SCRIPT_DIR/_connect.py"
exec(open(HELPER).read())

try:
    page.hover("""$SELECTOR""")
    print(f"Hovered: $SELECTOR")
finally:
    cleanup()
PYEOF
