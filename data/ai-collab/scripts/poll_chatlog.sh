#!/bin/bash
# Poll chat.log for new Agent B → Agent A messages and forward to Agent A
# Run via cron: * * * * * /bin/bash ~/.openclaw/workspace/skills/ai-collab/scripts/poll_chatlog.sh

LOG="${COLLAB_LOG:-$HOME/.openclaw/workspace/collab/chat.log}"
PTR_FILE="/tmp/agentb_chatlog_ptr"
AGENT_B_NAME="${AGENT_B_NAME:-AgentB}"

[ ! -f "$LOG" ] && exit 0

TOTAL=$(wc -l < "$LOG")
LAST=$(cat "$PTR_FILE" 2>/dev/null || echo "0")

[ "$TOTAL" -le "$LAST" ] && echo "$TOTAL" > "$PTR_FILE" && exit 0

# Extract new B→A lines after the pointer
NEW=$(tail -n +"$((LAST + 1))" "$LOG" | grep "$AGENT_B_NAME -> " | sed "s/.*$AGENT_B_NAME -> [^:]*: //")

echo "$TOTAL" > "$PTR_FILE"
[ -z "$NEW" ] && exit 0

while IFS= read -r line; do
  [ -z "$line" ] && continue
  if command -v openclaw &>/dev/null; then
    openclaw agent --agent main -m "[$AGENT_B_NAME]: $line" --json > /dev/null 2>&1
  fi
done <<< "$NEW"
