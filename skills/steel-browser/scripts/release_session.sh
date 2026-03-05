#!/usr/bin/env bash
# release_session.sh - Release (close) a Steel browser session
# Usage: release_session.sh [SESSION_ID]

set -e

if [[ -n "$1" ]]; then
  export STEEL_SESSION_ID="$1"
fi

python3 - <<EOF
import os, json, sys
from steel import Steel

api_key = os.environ.get("STEEL_API_KEY")
if not api_key:
    print("ERROR: STEEL_API_KEY not set", file=sys.stderr)
    sys.exit(1)

client = Steel(steel_api_key=api_key)

session_id = os.environ.get("STEEL_SESSION_ID")
if not session_id:
    state_path = os.path.expanduser("~/.steel_state")
    if os.path.exists(state_path):
        with open(state_path) as f:
            state = json.load(f)
        session_id = state.get("session_id")

if not session_id:
    print("ERROR: No session ID found", file=sys.stderr)
    sys.exit(1)

client.sessions.release(session_id)
print(f"Session {session_id} released.")

state_path = os.path.expanduser("~/.steel_state")
if os.path.exists(state_path):
    os.remove(state_path)
    print("State file removed.")
EOF
