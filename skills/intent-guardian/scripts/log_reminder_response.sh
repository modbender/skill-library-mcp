#!/bin/bash
# Log user's response to a reminder for the feedback loop.
# Usage: log_reminder_response.sh <task_id> <response_type> [correction_text]
# response_type: accepted | dismissed | ignored | corrected

LOG_DIR="${INTENT_GUARDIAN_DATA_DIR:-$HOME/.openclaw/memory/skills/intent-guardian}"
FEEDBACK_FILE="$LOG_DIR/reminder_feedback.jsonl"

mkdir -p "$LOG_DIR"

TASK_ID="${1:?Usage: log_reminder_response.sh <task_id> <response_type> [correction]}"
RESPONSE="${2:?Usage: log_reminder_response.sh <task_id> <response_type> [correction]}"
CORRECTION="${3:-}"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

python3 -c "
import json
entry = {
    'ts': '$TIMESTAMP',
    'task_id': '$TASK_ID',
    'response': '$RESPONSE',
    'correction': '$CORRECTION' if '$CORRECTION' else None
}
print(json.dumps(entry, ensure_ascii=True))
" >> "$FEEDBACK_FILE"

echo "Logged: $RESPONSE for task $TASK_ID"
