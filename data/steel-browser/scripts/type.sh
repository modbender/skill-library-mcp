#!/usr/bin/env bash
# type.sh - Fill a text input by selector
# Usage: type.sh SELECTOR "text to type"
# Use --clear to clear existing content first (default: fills/replaces)

set -e

SELECTOR="${1:?Usage: type.sh SELECTOR TEXT}"
TEXT="${2:?Usage: type.sh SELECTOR TEXT}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

python3 - <<PYEOF
import os, sys
HELPER = "$SCRIPT_DIR/_connect.py"
exec(open(HELPER).read())

try:
    page.fill("""$SELECTOR""", """$TEXT""")
    print(f"Typed into: $SELECTOR")
finally:
    cleanup()
PYEOF
