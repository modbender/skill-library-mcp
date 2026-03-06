#!/bin/bash
# pick-task.sh — Random task picker from project-ideas.md
# Usage: ./pick-task.sh [ideas-file]

WORKSPACE="${OPENCLAW_WORKSPACE:-$HOME/.openclaw/workspace}"
IDEAS_FILE="${1:-$WORKSPACE/memory/project-ideas.md}"

if [ ! -f "$IDEAS_FILE" ]; then
    echo "No project ideas file found at $IDEAS_FILE"
    echo "Create one with tasks like:"
    echo "  - [ ] Build a portfolio tracker"
    echo "  - [ ] Research topic X"
    exit 1
fi

# Extract unchecked items (- [ ] or * [ ])
TASKS=$(grep -E "^[[:space:]]*[-*] \[ \]" "$IDEAS_FILE" | sed 's/^[[:space:]]*[-*] \[ \] //')

if [ -z "$TASKS" ]; then
    echo "No unchecked tasks found!"
    echo "All done, or time to add new ideas."
    exit 0
fi

COUNT=$(echo "$TASKS" | wc -l)
PICK=$((RANDOM % COUNT + 1))
TASK=$(echo "$TASKS" | sed -n "${PICK}p")

echo "🎯 Today's task:"
echo "   $TASK"
echo ""
echo "($COUNT tasks remaining)"
