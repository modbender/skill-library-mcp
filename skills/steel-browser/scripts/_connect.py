"""
_connect.py - Shared helper: connect to a Steel session via Playwright CDP.

Usage in scripts:
    exec(open(HELPER).read())
    # After this: 'page', 'browser', 'playwright', 'session_id', 'client' are available.
    # Call cleanup() when done.

State file: ~/.steel_state (JSON with session_id)
"""
import os, json, sys
from playwright.sync_api import sync_playwright
from steel import Steel

api_key = os.environ.get("STEEL_API_KEY")
if not api_key:
    print("ERROR: STEEL_API_KEY not set", file=sys.stderr)
    sys.exit(1)

client = Steel(steel_api_key=api_key)

# Load session ID
session_id = os.environ.get("STEEL_SESSION_ID")
if not session_id:
    state_path = os.path.expanduser("~/.steel_state")
    if os.path.exists(state_path):
        with open(state_path) as f:
            state = json.load(f)
        session_id = state.get("session_id")

if not session_id:
    print("ERROR: No session ID. Run start_session.sh first or set STEEL_SESSION_ID", file=sys.stderr)
    sys.exit(1)

_pw = sync_playwright().start()
browser = _pw.chromium.connect_over_cdp(
    f"wss://connect.steel.dev?apiKey={api_key}&sessionId={session_id}"
)
context = browser.contexts[0] if browser.contexts else browser.new_context()
page = context.pages[0] if context.pages else context.new_page()

def cleanup():
    # In CDP mode, do NOT call browser.close() — it kills remote browser contexts.
    # Just stop the local playwright driver; the CDP connection drops cleanly on exit.
    try:
        _pw.stop()
    except:
        pass
