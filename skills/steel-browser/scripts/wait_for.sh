#!/usr/bin/env bash
# wait_for.sh - Wait for a selector to appear on the page
# Usage: wait_for.sh SELECTOR [TIMEOUT_MS]
# Default timeout: 30000ms (30 seconds)

set -e

SELECTOR="${1:?Usage: wait_for.sh SELECTOR [TIMEOUT_MS]}"
TIMEOUT_MS="${2:-30000}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

python3 - <<PYEOF
import os, sys
HELPER = "$SCRIPT_DIR/_connect.py"
exec(open(HELPER).read())

try:
    page.wait_for_selector("""$SELECTOR""", timeout=int("$TIMEOUT_MS"))
    print(f"Found: $SELECTOR")
finally:
    cleanup()
PYEOF
