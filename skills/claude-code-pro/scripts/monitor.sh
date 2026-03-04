#!/usr/bin/env bash
# Monitor a Claude Code tmux session
# Usage: monitor.sh --session <name> [--lines <n>] [--watch] [--json]

set -euo pipefail

SESSION=""
LINES=100
WATCH=false
JSON=false

while [[ $# -gt 0 ]]; do
  case $1 in
    --session) SESSION="$2"; shift 2;;
    --lines) LINES="$2"; shift 2;;
    --watch) WATCH=true; shift;;
    --json) JSON=true; shift;;
    *) echo "Unknown option: $1"; exit 1;;
  esac
done

if [[ -z "$SESSION" ]]; then
  echo "Usage: monitor.sh --session <name> [--lines <n>] [--watch] [--json]"
  exit 1
fi

# Add cc- prefix if not present
[[ "$SESSION" != cc-* ]] && SESSION="cc-${SESSION}"

capture() {
  local output
  output=$(tmux -L cc capture-pane -p -J -t "$SESSION" -S "-${LINES}" 2>/dev/null || echo "")

  if [[ "$JSON" == true ]]; then
    local alive="true"
    tmux -L cc has-session -t "$SESSION" 2>/dev/null || alive="false"

    # Pure bash JSON output — no jq dependency
    # Escape output for JSON string
    local escaped
    escaped=$(printf '%s' "$output" | python3 -c 'import sys,json; print(json.dumps(sys.stdin.read()))' 2>/dev/null \
      || printf '%s' "$output" | sed 's/\\/\\\\/g; s/"/\\"/g; s/\t/\\t/g' | awk '{printf "%s\\n", $0}' | sed 's/\\n$//')

    printf '{"session":"%s","alive":%s,"lines":%d,"output":%s}\n' \
      "$SESSION" "$alive" "$LINES" "$escaped"
  else
    echo "=== $SESSION (last $LINES lines) ==="
    echo "$output"
  fi
}

if [[ "$WATCH" == true ]]; then
  while true; do
    clear
    capture
    sleep 5
  done
else
  capture
fi
