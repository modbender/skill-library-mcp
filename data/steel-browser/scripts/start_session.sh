#!/usr/bin/env bash
# start_session.sh - Create a new Steel browser session
# Usage: start_session.sh [--proxy] [--captcha] [--timeout MS] [--ua USER_AGENT]
#
# Saves session ID to ~/.steel_state for use by other scripts.
# Prints SESSION_ID and VIEWER_URL.

set -e

USE_PROXY=false
SOLVE_CAPTCHA=false
TIMEOUT_MS=300000  # 5 min default
USER_AGENT=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --proxy)   USE_PROXY=true; shift ;;
    --captcha) SOLVE_CAPTCHA=true; shift ;;
    --timeout) TIMEOUT_MS="$2"; shift 2 ;;
    --ua)      USER_AGENT="$2"; shift 2 ;;
    *) echo "Unknown option: $1" >&2; exit 1 ;;
  esac
done

python3 - <<EOF
import os, json, sys
from steel import Steel

api_key = os.environ.get("STEEL_API_KEY")
if not api_key:
    print("ERROR: STEEL_API_KEY not set", file=sys.stderr)
    sys.exit(1)

client = Steel(steel_api_key=api_key)

use_proxy = "$USE_PROXY" == "true"
solve_captcha = "$SOLVE_CAPTCHA" == "true"
kwargs = dict(
    use_proxy=use_proxy,
    solve_captcha=solve_captcha,
    timeout=int("$TIMEOUT_MS"),
)
if "$USER_AGENT":
    kwargs["user_agent"] = "$USER_AGENT"

session = client.sessions.create(**kwargs)

state = {"session_id": str(session.id)}
state_path = os.path.expanduser("~/.steel_state")
with open(state_path, "w") as f:
    json.dump(state, f)

print(f"SESSION_ID={session.id}")
print(f"VIEWER_URL={session.session_viewer_url}")
print(f"State saved to {state_path}")
EOF
