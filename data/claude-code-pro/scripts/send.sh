#!/usr/bin/env bash
# Send input to a Claude Code tmux session
# Usage: send.sh --session <name> --text <message>
#        send.sh --session <name> --text-file <file>
#        send.sh --session <name> --approve
#        send.sh --session <name> --reject
#        send.sh --session <name> --compact

set -euo pipefail

SESSION=""
TEXT=""
TEXT_FILE=""
ACTION=""

while [[ $# -gt 0 ]]; do
  case $1 in
    --session) SESSION="$2"; shift 2;;
    --text) TEXT="$2"; shift 2;;
    --text-file) TEXT_FILE="$2"; shift 2;;
    --approve) ACTION="approve"; shift;;
    --reject) ACTION="reject"; shift;;
    --compact) ACTION="compact"; shift;;
    *) echo "Unknown option: $1"; exit 1;;
  esac
done

if [[ -z "$SESSION" ]]; then
  echo "Usage: send.sh --session <name> --text <message> | --text-file <file> | --approve | --reject | --compact"
  exit 1
fi

[[ "$SESSION" != cc-* ]] && SESSION="cc-${SESSION}"

case "$ACTION" in
  approve)
    tmux -L cc send-keys -t "$SESSION" "y" Enter
    echo "✅ Approved"
    ;;
  reject)
    tmux -L cc send-keys -t "$SESSION" "n" Enter
    echo "❌ Rejected"
    ;;
  compact)
    tmux -L cc send-keys -t "$SESSION" -l "/compact"
    tmux -L cc send-keys -t "$SESSION" Enter
    echo "🗜️ Compact triggered"
    ;;
  "")
    # Load from file if specified
    if [[ -n "$TEXT_FILE" && -f "$TEXT_FILE" ]]; then
      TEXT=$(cat "$TEXT_FILE")
    fi
    if [[ -z "$TEXT" ]]; then
      echo "Error: --text or --text-file required"
      exit 1
    fi
    # Use tmux load-buffer + paste-buffer for safe multi-line input
    TMPFILE=$(mktemp /tmp/cc-send-XXXXXX.txt)
    printf '%s' "$TEXT" > "$TMPFILE"
    tmux -L cc load-buffer "$TMPFILE"
    tmux -L cc paste-buffer -t "$SESSION"
    rm -f "$TMPFILE"
    sleep 0.3
    tmux -L cc send-keys -t "$SESSION" Enter
    echo "📤 Sent"
    ;;
esac
