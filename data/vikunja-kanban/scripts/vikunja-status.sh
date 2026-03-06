#!/bin/bash
# Vikunja Status Board reader for heartbeat/cron agents
# Usage: vikunja-status.sh [bucket_name]

VIKUNJA_URL="https://kanban.pigpen.haus"
TOKEN="${VIKUNJA_TOKEN:?Set VIKUNJA_TOKEN env var}"
PROJECT_ID=1
VIEW_ID=4

# Fetch kanban view and save to temp file
TMPFILE=$(mktemp)
curl -sk "$VIKUNJA_URL/api/v1/projects/$PROJECT_ID/views/$VIEW_ID/tasks" \
  -H "Authorization: Bearer $TOKEN" > "$TMPFILE"

FILTER="$1"

python3 - "$TMPFILE" "$FILTER" << 'PYEOF'
import json, sys

tmpfile = sys.argv[1]
filter_bucket = sys.argv[2] if len(sys.argv) > 2 else ""

with open(tmpfile) as f:
    data = json.load(f)

if not isinstance(data, list):
    print("ERROR: Unexpected API response")
    sys.exit(1)

for b in data:
    title = b["title"]
    tasks = b.get("tasks") or []
    if filter_bucket and filter_bucket.lower() not in title.lower():
        continue
    print(f"\n## {title} ({len(tasks)} tasks)")
    for t in tasks:
        pri = t.get("priority", 0)
        pri_label = {0:"", 1:"low", 2:"med", 3:"high", 4:"urgent"}.get(pri, "")
        due = t.get("due_date", "")
        prefix = f"[{pri_label}] " if pri_label else ""
        if due and not due.startswith("0001"):
            print(f"  - {prefix}{t['title']} (due: {due[:10]})")
        else:
            print(f"  - {prefix}{t['title']}")
PYEOF

rm -f "$TMPFILE"
