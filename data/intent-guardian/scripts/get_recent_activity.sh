#!/bin/bash
# Get the last N lines of activity log for LLM analysis.

LOG_DIR="${INTENT_GUARDIAN_DATA_DIR:-$HOME/.openclaw/memory/skills/intent-guardian}"
LOG_FILE="$LOG_DIR/activity_log.jsonl"
NUM_LINES="${1:-100}"

if [ ! -f "$LOG_FILE" ]; then
    echo '[]'
    exit 0
fi

tail -n "$NUM_LINES" "$LOG_FILE"
