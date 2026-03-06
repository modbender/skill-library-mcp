#!/usr/bin/env bash
# =============================================================================
# check-calendar.sh — Fetch upcoming calendar events via gog, sanitize, output JSON
# =============================================================================
#
# Usage:
#   ./check-calendar.sh [--raw] [--help]
#
# Options:
#   --raw   Skip audit logging (just output sanitized JSON)
#   --help  Show this help message
#
# Environment:
#   CAL_ACCOUNTS  Comma-separated list of Google accounts to check
#                 Default: reads from accounts.conf or empty
#
# Requires: gog CLI (https://github.com/liamg/gog), python3
# =============================================================================

set -euo pipefail

# --- Help ---
if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
    sed -n '2,/^# =====/{ /^# =====/d; s/^# \?//p }' "$0"
    exit 0
fi

# --- Configuration ---
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CAL_SANITIZER="$SCRIPT_DIR/cal_sanitizer.py"
AUDIT="$SCRIPT_DIR/audit.py"
ACCOUNTS_CONF="$SCRIPT_DIR/accounts.conf"

# Load accounts: env var > config file > empty
if [ -n "${CAL_ACCOUNTS:-}" ]; then
    IFS=',' read -ra ACCOUNTS <<< "$CAL_ACCOUNTS"
elif [ -f "$ACCOUNTS_CONF" ]; then
    mapfile -t ACCOUNTS < <(grep -v '^\s*#' "$ACCOUNTS_CONF" | grep -v '^\s*$')
else
    echo '{"events": []}'
    exit 0
fi

# --- Fetch and sanitize ---
all_events="[]"

for account in "${ACCOUNTS[@]}"; do
    account="$(echo "$account" | xargs)"  # trim whitespace
    [ -z "$account" ] && continue

    # Fetch events via gog
    raw_output=$(gog cal list --account "$account" 2>/dev/null || true)
    [ -z "$raw_output" ] && continue

    # Parse gog text output into JSON event objects
    events_json=$(python3 -c "
import json, sys, re

raw = sys.argv[1]
account = sys.argv[2]
events = []

blocks = re.split(r'\n(?:---+|\s*)\n', raw)

for block in blocks:
    block = block.strip()
    if not block:
        continue

    event = {'account': account}
    lines = block.split('\n')

    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.startswith('Title:') or line.startswith('Summary:'):
            event['summary'] = line.split(':', 1)[1].strip()
        elif line.startswith('When:') or line.startswith('Start:'):
            event['start'] = line.split(':', 1)[1].strip()
        elif line.startswith('End:'):
            event['end'] = line.split(':', 1)[1].strip()
        elif line.startswith('Where:') or line.startswith('Location:'):
            event['location'] = line.split(':', 1)[1].strip()
        elif line.startswith('Organizer:'):
            event['organizer'] = line.split(':', 1)[1].strip()
        elif line.startswith('Description:') or line.startswith('Notes:'):
            event['description'] = line.split(':', 1)[1].strip()
        elif line.startswith('Attendees:'):
            att = line.split(':', 1)[1].strip()
            event['attendees'] = [a.strip() for a in att.split(',') if a.strip()]
        elif 'summary' not in event:
            event['summary'] = line

    if event.get('summary') or event.get('start'):
        events.append(event)

print(json.dumps(events))
" "$raw_output" "$account")

    # Sanitize through cal_sanitizer
    sanitized=$(echo "$events_json" | python3 "$CAL_SANITIZER")

    # Merge results
    all_events=$(python3 -c "
import json, sys
arr = json.loads(sys.argv[1])
new_data = json.loads(sys.argv[2])
if isinstance(new_data, dict) and 'events' in new_data:
    arr.extend(new_data['events'])
elif isinstance(new_data, list):
    arr.extend(new_data)
else:
    arr.append(new_data)
print(json.dumps(arr))
" "$all_events" "$sanitized")

done

# --- Output ---
python3 -c "
import json, sys
print(json.dumps({'events': json.loads(sys.argv[1])}, indent=2))
" "$all_events"

# Audit log (unless --raw)
if [[ "${1:-}" != "--raw" ]]; then
    echo "$all_events" | python3 "$AUDIT" 2>/dev/null || true
fi
