#!/bin/bash
# Agent B daemon — listens for messages in collab/inbox and responds via claude --print
# Customize: AGENT_B_NAME, MODEL, SYSTEM_PROMPT

AGENT_B_NAME="${AGENT_B_NAME:-AgentB}"
MODEL="${AGENT_B_MODEL:-claude-haiku-4-5-20251001}"
INBOX="${COLLAB_INBOX:-$HOME/.openclaw/workspace/collab/inbox}"
LOG="${COLLAB_LOG:-$HOME/.openclaw/workspace/collab/chat.log}"
AGENT_A_NAME="${AGENT_A_NAME:-AgentA}"

# Single-instance guard
PIDFILE="/tmp/agentb_daemon.pid"
if [ -f "$PIDFILE" ] && kill -0 "$(cat $PIDFILE)" 2>/dev/null; then
  echo "Daemon already running (PID $(cat $PIDFILE)). Exiting." >&2
  exit 1
fi
echo $$ > "$PIDFILE"
trap "rm -f $PIDFILE" EXIT

# Required: unset so nested claude --print works
unset CLAUDECODE

mkdir -p "$INBOX"

logline() {
  printf "%s %s\n" "$(date '+%Y-%m-%d %H:%M:%S')" "$1" >> "$LOG"
}

logline "SYSTEM: $AGENT_B_NAME daemon started (model: $MODEL)"

inotifywait -m -e moved_to "$INBOX" 2>/dev/null | while read dir event file; do
  FULLPATH="$INBOX/$file"
  [ ! -f "$FULLPATH" ] && continue

  MSG=$(cat "$FULLPATH")
  rm "$FULLPATH"

  logline "$AGENT_A_NAME -> $AGENT_B_NAME: $MSG"

  SYSTEM_PROMPT="You are $AGENT_B_NAME, an autonomous AI agent collaborating with $AGENT_A_NAME.
Use the protocol: [ACK:name] to acknowledge, [DONE:name] result to close tasks, [BLOCKED:name] reason if stuck.
Keep responses under 100 words. Be direct. No preamble.
Chat log location: $LOG"

  RESPONSE=$(claude --print --model "$MODEL" \
    "$SYSTEM_PROMPT

$AGENT_A_NAME says: $MSG" 2>/dev/null)

  logline "$AGENT_B_NAME -> $AGENT_A_NAME: $RESPONSE"

  # Route response back to Agent A
  if command -v openclaw &>/dev/null; then
    openclaw agent --agent main -m "[$AGENT_B_NAME]: $RESPONSE" --json > /dev/null 2>&1
  fi
done
