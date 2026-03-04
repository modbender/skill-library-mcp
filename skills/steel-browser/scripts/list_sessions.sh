#!/usr/bin/env bash
# list_sessions.sh - List all active Steel browser sessions
# Usage: list_sessions.sh

set -e

python3 - <<EOF
import os, sys
from steel import Steel

api_key = os.environ.get("STEEL_API_KEY")
if not api_key:
    print("ERROR: STEEL_API_KEY not set", file=sys.stderr)
    sys.exit(1)

client = Steel(steel_api_key=api_key)
sessions = client.sessions.list()

# SDK may return iterable or object with .data
items = getattr(sessions, 'data', None) or list(sessions)
if not items:
    print("No active sessions.")
else:
    for s in items:
        print(f"  id={s.id}  status={getattr(s,'status','?')}  viewer={getattr(s,'session_viewer_url','?')}")
EOF
