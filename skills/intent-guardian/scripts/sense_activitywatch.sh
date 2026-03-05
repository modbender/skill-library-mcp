#!/bin/bash
# Fetch recent window activity from ActivityWatch API.
# Requires ActivityWatch running at localhost:5600.

AW_URL="${INTENT_GUARDIAN_AW_URL:-http://localhost:5600}"
LOG_DIR="${INTENT_GUARDIAN_DATA_DIR:-$HOME/.openclaw/memory/skills/intent-guardian}"
LOG_FILE="$LOG_DIR/activity_log.jsonl"
LOOKBACK_MINUTES="${1:-5}"

mkdir -p "$LOG_DIR"

HOSTNAME=$(hostname -s 2>/dev/null || hostname)
BUCKET="aw-watcher-window_$HOSTNAME"

END=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
if [[ "$(uname)" == "Darwin" ]]; then
    START=$(date -u -v-${LOOKBACK_MINUTES}M +"%Y-%m-%dT%H:%M:%SZ")
else
    START=$(date -u -d "$LOOKBACK_MINUTES minutes ago" +"%Y-%m-%dT%H:%M:%SZ")
fi

RESPONSE=$(curl -s "${AW_URL}/api/0/buckets/${BUCKET}/events?start=${START}&end=${END}&limit=50" 2>/dev/null)

if [ $? -ne 0 ] || [ -z "$RESPONSE" ]; then
    echo '{"error": "ActivityWatch not reachable", "url": "'"$AW_URL"'"}'
    exit 1
fi

echo "$RESPONSE" | python3 -c "
import sys, json
try:
    events = json.load(sys.stdin)
    for e in events:
        ts = e.get('timestamp', '')
        dur = e.get('duration', 0)
        data = e.get('data', {})
        app = data.get('app', 'unknown')
        title = data.get('title', 'N/A')
        entry = {'ts': ts, 'duration': dur, 'app': app, 'title': title, 'source': 'activitywatch'}
        line = json.dumps(entry, ensure_ascii=True)
        print(line)
except Exception as ex:
    print(json.dumps({'error': str(ex)}))
" | tee -a "$LOG_FILE"
