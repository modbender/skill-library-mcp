#!/bin/bash
# Run a Claude Code task in background, notify OpenClaw when done.
# Usage: run-task.sh <project_dir> <task_description> <session_key>
#
# Zero tokens while Claude Code works. Notification only on completion.

PROJECT_DIR="${1:-.}"
TASK="$2"
SESSION_KEY="$3"
TASK_ID="cc-$(date +%s)"
OUTPUT_FILE="/tmp/${TASK_ID}-result.txt"

# Ensure project dir exists and has git
mkdir -p "$PROJECT_DIR"
cd "$PROJECT_DIR"
[ -d .git ] || git init -q

# Get gateway token
TOKEN=$(python3 -c "import json; print(json.load(open('$HOME/.openclaw/openclaw.json'))['gateway']['auth']['token'])")
GW="http://localhost:18789"

# Run Claude Code
claude -p "$TASK" \
  --dangerously-skip-permissions \
  --output-format text \
  > "$OUTPUT_FILE" 2>&1

EXIT_CODE=$?

# Truncate output for notification (first 2000 chars)
RESULT=$(head -c 2000 "$OUTPUT_FILE")
FULL_SIZE=$(wc -c < "$OUTPUT_FILE")

if [ $EXIT_CODE -eq 0 ]; then
    MSG="✅ Claude Code задача завершена!\n\n**Задача:** ${TASK:0:150}\n**Проект:** $PROJECT_DIR\n**Результат** (${FULL_SIZE} bytes):\n\n${RESULT}\n\n📁 Полный вывод: $OUTPUT_FILE"
else
    MSG="❌ Claude Code ошибка (exit $EXIT_CODE)\n\n**Задача:** ${TASK:0:150}\n**Проект:** $PROJECT_DIR\n\n${RESULT}"
fi

# Notify via sessions_send
if [ -n "$SESSION_KEY" ]; then
    python3 -c "
import json, requests
msg = '''$MSG'''
requests.post('$GW/tools/invoke',
    headers={'Authorization': 'Bearer $TOKEN', 'Content-Type': 'application/json'},
    json={'tool': 'sessions_send', 'sessionKey': '$SESSION_KEY',
          'args': {'sessionKey': '$SESSION_KEY', 'message': msg}},
    timeout=30)
" 2>/dev/null
fi
