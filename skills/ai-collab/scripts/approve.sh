#!/bin/bash
# Approve a terminal prompt in Agent B's tmux session
# Usage: approve.sh "Yes"   or   approve.sh "2"

RESPONSE="${1:-Yes}"
SESSION_NAME="${AGENT_B_SESSION:-agentb-session}"

SESSION=$(tmux ls 2>/dev/null | grep "$SESSION_NAME" | head -1 | cut -d: -f1)
if [ -z "$SESSION" ]; then
  echo "No tmux session '$SESSION_NAME' found" >&2
  echo "Active sessions:" >&2
  tmux ls 2>/dev/null || echo "(none)" >&2
  exit 1
fi

tmux send-keys -t "$SESSION" "$RESPONSE" Enter
echo "Sent '$RESPONSE' to tmux session: $SESSION"
