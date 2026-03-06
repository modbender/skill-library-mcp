#!/usr/bin/env bash
# get_content.sh - Extract readable text content from the current page
# Usage: get_content.sh [--html] [SELECTOR]
# --html: return raw HTML instead of text
# SELECTOR: limit extraction to a specific element

set -e

MODE="text"
SELECTOR=""

for arg in "$@"; do
  case "$arg" in
    --html) MODE="html" ;;
    *) SELECTOR="$arg" ;;
  esac
done

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

python3 - <<PYEOF
import os, sys
HELPER = "$SCRIPT_DIR/_connect.py"
exec(open(HELPER).read())

try:
    selector = """$SELECTOR"""
    mode = "$MODE"
    if selector:
        el = page.locator(selector)
        content = el.inner_html() if mode == "html" else el.inner_text()
    else:
        content = page.content() if mode == "html" else page.evaluate("document.body.innerText")
    print(content)
finally:
    cleanup()
PYEOF
