#!/usr/bin/env bash
# Stop a Claude Code tmux session
# Usage: stop.sh --session <name> [--all]

set -euo pipefail

SESSION=""
ALL=false

while [[ $# -gt 0 ]]; do
  case $1 in
    --session) SESSION="$2"; shift 2;;
    --all) ALL=true; shift;;
    *) echo "Unknown option: $1"; exit 1;;
  esac
done

if [[ "$ALL" == true ]]; then
  sessions=$(tmux -L cc list-sessions -F '#{session_name}' 2>/dev/null | grep '^cc-' || true)
  if [[ -z "$sessions" ]]; then
    echo "No active sessions."
    exit 0
  fi
  while IFS= read -r s; do
    tmux -L cc kill-session -t "$s" 2>/dev/null && echo "🛑 Killed $s" || echo "⚠️ Failed to kill $s"
  done <<< "$sessions"
  exit 0
fi

if [[ -z "$SESSION" ]]; then
  echo "Usage: stop.sh --session <name> | --all"
  exit 1
fi

[[ "$SESSION" != cc-* ]] && SESSION="cc-${SESSION}"
tmux -L cc kill-session -t "$SESSION" 2>/dev/null && echo "🛑 Killed $SESSION" || echo "⚠️ Session $SESSION not found"
