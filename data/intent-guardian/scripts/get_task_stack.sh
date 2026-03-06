#!/bin/bash
# Read and display the current task stack.

LOG_DIR="${INTENT_GUARDIAN_DATA_DIR:-$HOME/.openclaw/memory/skills/intent-guardian}"
STACK_FILE="$LOG_DIR/task_stack.json"

if [ ! -f "$STACK_FILE" ]; then
    echo '{"stack": [], "current_focus": null, "forgotten_candidates": []}'
    exit 0
fi

cat "$STACK_FILE"
