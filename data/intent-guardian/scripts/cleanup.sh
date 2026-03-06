#!/bin/bash
# Clean up old activity logs to manage disk usage.
# Keeps the last N days of logs (default: 30).

LOG_DIR="${INTENT_GUARDIAN_DATA_DIR:-$HOME/.openclaw/memory/skills/intent-guardian}"
KEEP_DAYS="${1:-30}"

if [ ! -d "$LOG_DIR" ]; then
    echo "No data directory found at $LOG_DIR"
    exit 0
fi

CUTOFF_DATE=$(date -v-${KEEP_DAYS}d +%Y-%m-%d 2>/dev/null || date -d "$KEEP_DAYS days ago" +%Y-%m-%d)
LOG_FILE="$LOG_DIR/activity_log.jsonl"

if [ -f "$LOG_FILE" ]; then
    BEFORE=$(wc -l < "$LOG_FILE" | tr -d ' ')
    python3 -c "
import json, sys

cutoff = '$CUTOFF_DATE'
kept = 0
with open('$LOG_FILE') as f:
    lines = f.readlines()

with open('$LOG_FILE', 'w') as f:
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            e = json.loads(line)
            ts = e.get('ts', '')
            if ts[:10] >= cutoff:
                f.write(line + '\n')
                kept += 1
        except json.JSONDecodeError:
            continue

print(f'Kept {kept} entries from {cutoff} onwards')
" 2>/dev/null
    AFTER=$(wc -l < "$LOG_FILE" | tr -d ' ')
    echo "Activity log: $BEFORE -> $AFTER lines (kept last $KEEP_DAYS days)"
fi

echo "Cleanup complete."
