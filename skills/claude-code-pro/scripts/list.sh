#!/usr/bin/env bash
# List all active Claude Code tmux sessions
# Usage: list.sh [--json]

set -euo pipefail

JSON=false
[[ "${1:-}" == "--json" ]] && JSON=true

sessions=$(tmux -L cc list-sessions -F '#{session_name} #{session_created} #{session_activity}' 2>/dev/null | grep '^cc-' || true)

if [[ -z "$sessions" ]]; then
  if [[ "$JSON" == true ]]; then
    echo "[]"
  else
    echo "No active Claude Code sessions."
  fi
  exit 0
fi

if [[ "$JSON" == true ]]; then
  echo "["
  first=true
  while IFS= read -r line; do
    name=$(echo "$line" | awk '{print $1}')
    created=$(echo "$line" | awk '{print $2}')
    activity=$(echo "$line" | awk '{print $3}')
    last_line=$(tmux -L cc capture-pane -p -J -t "$name" -S -5 2>/dev/null | tail -1 | sed 's/\\/\\\\/g; s/"/\\"/g' || echo "")

    [[ "$first" == true ]] && first=false || echo ","
    printf '  {"session":"%s","created":%s,"lastActivity":%s,"lastLine":"%s"}' \
      "$name" "$created" "$activity" "$last_line"
  done <<< "$sessions"
  echo ""
  echo "]"
else
  echo "Active Claude Code sessions:"
  echo "---"
  while IFS= read -r line; do
    name=$(echo "$line" | awk '{print $1}')
    label=${name#cc-}
    last_line=$(tmux -L cc capture-pane -p -J -t "$name" -S -3 2>/dev/null | tail -1 || echo "")
    echo "⚡ $label → $last_line"
  done <<< "$sessions"
fi
