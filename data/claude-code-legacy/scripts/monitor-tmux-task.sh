#!/usr/bin/env bash
set -euo pipefail

SESSION=""
LINES=200
ATTACH=false
SOCKET="${TMPDIR:-/tmp}/clawdbot-tmux-sockets/clawdbot.sock"

TARGET="local"   # local | ssh
SSH_HOST=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --session) SESSION="$2"; shift 2 ;;
    --lines) LINES="$2"; shift 2 ;;
    --attach) ATTACH=true; shift ;;
    --socket) SOCKET="$2"; shift 2 ;;

    --target) TARGET="$2"; shift 2 ;;
    --ssh-host) SSH_HOST="$2"; shift 2 ;;

    *) echo "Unknown arg: $1"; exit 1 ;;
  esac
done

[[ -n "$SESSION" ]] || { echo "Usage: $0 --session <name> [--lines 200] [--attach] [--socket path] [--target local|ssh --ssh-host <alias>]"; exit 1; }
if [[ "$TARGET" == "ssh" && -z "$SSH_HOST" ]]; then
  echo "ERROR: --target ssh requires --ssh-host <alias>"
  exit 2
fi

if $ATTACH; then
  if [[ "$TARGET" == "ssh" ]]; then
    exec ssh "$SSH_HOST" "tmux -S '$SOCKET' attach -t '$SESSION'"
  else
    exec tmux -S "$SOCKET" attach -t "$SESSION"
  fi
else
  if [[ "$TARGET" == "ssh" ]]; then
    ssh "$SSH_HOST" "tmux -S '$SOCKET' capture-pane -p -J -t '$SESSION':0.0 -S -'$LINES'"
  else
    tmux -S "$SOCKET" capture-pane -p -J -t "$SESSION":0.0 -S -"$LINES"
  fi
fi
