#!/usr/bin/env bash
# eval_js.sh - Execute JavaScript in the browser and print the result
# Usage: eval_js.sh "js expression"
# Example: eval_js.sh "document.title"
#          eval_js.sh "window.location.href"
#          eval_js.sh "document.querySelectorAll('a').length"

set -e

JS="${1:?Usage: eval_js.sh \"js expression\"}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

python3 - <<PYEOF
import os, sys
HELPER = "$SCRIPT_DIR/_connect.py"
exec(open(HELPER).read())

try:
    result = page.evaluate("""$JS""")
    print(result)
finally:
    cleanup()
PYEOF
