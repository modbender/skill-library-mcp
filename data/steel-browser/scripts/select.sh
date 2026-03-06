#!/usr/bin/env bash
# select.sh - Select an option from a <select> dropdown
# Usage: select.sh SELECTOR VALUE
# VALUE can be the option text or value attribute

set -e

SELECTOR="${1:?Usage: select.sh SELECTOR VALUE}"
VALUE="${2:?Usage: select.sh SELECTOR VALUE}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

python3 - <<PYEOF
import os, sys
HELPER = "$SCRIPT_DIR/_connect.py"
exec(open(HELPER).read())

try:
    sel = """$SELECTOR"""
    val = """$VALUE"""
    page.select_option(sel, label=val)
    print(f"Selected '{val}' in {sel}")
finally:
    cleanup()
PYEOF
