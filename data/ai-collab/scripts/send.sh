#!/bin/bash
# Send a message from Agent A to Agent B daemon inbox
# Usage: send.sh "message text"
# Atomic write: mktemp + mv prevents partial reads by inotifywait

INBOX="${COLLAB_INBOX:-$HOME/.openclaw/workspace/collab/inbox}"
mkdir -p "$INBOX"

if [ -z "$*" ]; then
  echo "Usage: send.sh \"message text\"" >&2
  exit 1
fi

TMPFILE=$(mktemp "$INBOX/.msg.XXXXXX")
echo "$*" > "$TMPFILE"
mv "$TMPFILE" "$INBOX/msg_$(date +%s%N).txt"
echo "[send.sh] Message dispatched to inbox"
