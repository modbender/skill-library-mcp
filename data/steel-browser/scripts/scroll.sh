#!/usr/bin/env bash
# scroll.sh - Scroll the page
# Usage: scroll.sh AMOUNT  (positive=down, negative=up, in pixels)
# Or: scroll.sh --to-bottom / --to-top
# Or: scroll.sh SELECTOR (scroll element into view)

set -e

ARG="${1:?Usage: scroll.sh AMOUNT|--to-bottom|--to-top|SELECTOR}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

python3 - <<PYEOF
import os, sys
HELPER = "$SCRIPT_DIR/_connect.py"
exec(open(HELPER).read())

try:
    arg = """$ARG"""
    if arg == "--to-bottom":
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        print("Scrolled to bottom")
    elif arg == "--to-top":
        page.evaluate("window.scrollTo(0, 0)")
        print("Scrolled to top")
    else:
        try:
            amount = int(arg)
            page.evaluate(f"window.scrollBy(0, {amount})")
            direction = "down" if amount > 0 else "up"
            print(f"Scrolled {direction} by {abs(amount)}px")
        except ValueError:
            page.locator(arg).scroll_into_view_if_needed()
            print(f"Scrolled '{arg}' into view")
finally:
    cleanup()
PYEOF
