#!/bin/bash
# ACC: Load state at session start
# Shows current error patterns and lessons learned

set -e

WORKSPACE="${WORKSPACE:-$HOME/.openclaw/workspace}"
STATE_FILE="$WORKSPACE/memory/acc-state.json"
STATE_MD="$WORKSPACE/ACC_STATE.md"

# Check if state file exists
if [ ! -f "$STATE_FILE" ]; then
    echo "⚡ ACC: No state file yet (fresh start)"
    exit 0
fi

# Check if markdown state exists
if [ ! -f "$STATE_MD" ]; then
    echo "⚡ ACC: State exists but no ACC_STATE.md — run sync-state.sh"
    exit 0
fi

# Output the markdown state for context
echo "⚡ ACC State Loaded:"
echo ""
cat "$STATE_MD"
