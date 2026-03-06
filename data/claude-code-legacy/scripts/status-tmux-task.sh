#!/usr/bin/env bash
set -euo pipefail

LABEL=""
SESSION=""
SOCKET="${TMPDIR:-/tmp}/clawdbot-tmux-sockets/clawdbot.sock"
TARGET="local"
SSH_HOST=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --label) LABEL="$2"; shift 2 ;;
    --session) SESSION="$2"; shift 2 ;;
    --socket) SOCKET="$2"; shift 2 ;;
    --target) TARGET="$2"; shift 2 ;;
    --ssh-host) SSH_HOST="$2"; shift 2 ;;
    *) echo "Unknown arg: $1"; exit 1 ;;
  esac
done

[[ -n "$LABEL" ]] || { echo "Usage: $0 --label <label> [--session cc-xxx] [--socket path] [--target local|ssh --ssh-host <alias>]"; exit 1; }
if [[ "$TARGET" == "ssh" && -z "$SSH_HOST" ]]; then
  echo "ERROR: --target ssh requires --ssh-host <alias>"
  exit 2
fi

SESSION="${SESSION:-cc-${LABEL}}"
REPORT_JSON="/tmp/${SESSION}-completion-report.json"

# 1. Check if session exists
session_alive=false
if [[ "$TARGET" == "ssh" ]]; then
  ssh -o BatchMode=yes "$SSH_HOST" "tmux -S '$SOCKET' has-session -t '$SESSION'" 2>/dev/null && session_alive=true
else
  tmux -S "$SOCKET" has-session -t "$SESSION" 2>/dev/null && session_alive=true
fi

# 2. Check if report exists
report_exists=false
if [[ "$TARGET" == "ssh" ]]; then
  ssh -o BatchMode=yes "$SSH_HOST" "test -f '$REPORT_JSON'" 2>/dev/null && report_exists=true
else
  [[ -f "$REPORT_JSON" ]] && report_exists=true
fi

# 3. If session dead and no report → dead
if [[ "$session_alive" != true ]]; then
  if [[ "$report_exists" == true ]]; then
    echo "STATUS=done_session_ended"
  else
    echo "STATUS=dead"
  fi
  echo "SESSION_ALIVE=false"
  echo "REPORT_EXISTS=$report_exists"
  exit 0
fi

# 4. If report exists and session alive → likely done (wake may have been sent)
if [[ "$report_exists" == true ]]; then
  echo "STATUS=likely_done"
  echo "SESSION_ALIVE=true"
  echo "REPORT_EXISTS=true"
  exit 0
fi

# 5. Session alive, no report → check pane output for signals
if [[ "$TARGET" == "ssh" ]]; then
  pane="$(ssh -o BatchMode=yes "$SSH_HOST" "tmux -S '$SOCKET' capture-pane -p -J -t '$SESSION':0.0 -S -50" 2>/dev/null || true)"
else
  pane="$(tmux -S "$SOCKET" capture-pane -p -J -t "$SESSION":0.0 -S -50 2>/dev/null || true)"
fi

# Detect completion signals in pane output
if echo "$pane" | rg -q "REPORT_JSON=|WAKE_SENT=|Co-Authored-By:|completion-report"; then
  echo "STATUS=likely_done"
elif echo "$pane" | rg -q "✗|Error:|FAILED|fatal:"; then
  echo "STATUS=stuck"
elif echo "$pane" | rg -q "Envisioning|Thinking|Running|✽|Mustering|Read [0-9]+ file|Bash\(|Edit\(|Write\("; then
  echo "STATUS=running"
elif echo "$pane" | rg -q "^❯"; then
  echo "STATUS=idle"
else
  echo "STATUS=running"
fi

echo "SESSION_ALIVE=true"
echo "REPORT_EXISTS=false"
