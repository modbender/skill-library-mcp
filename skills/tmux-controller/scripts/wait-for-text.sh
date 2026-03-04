#!/usr/bin/env bash
# wait-for-text.sh — Poll a tmux pane for a regex match.
# Uses default tmux server (no custom sockets).
#
# Two timeout modes:
#   -T <seconds>        Hard timeout — fail after N seconds regardless
#   --stale <seconds>   Stale timeout — only timeout if pane output hasn't
#                       changed for N seconds (default: 300 = 5 min of no output)
#
# Usage:
#   wait-for-text.sh -t oc-project-feature -p '❯'                    # stale timeout (default 5 min)
#   wait-for-text.sh -t oc-project-feature -p '❯' --stale 600        # stale timeout 10 min
#   wait-for-text.sh -t oc-project-feature -p '❯' -T 60              # hard timeout 60s

set -euo pipefail

target=""
pattern=""
grep_flag="-E"
hard_timeout=0
stale_timeout=300
interval=5
lines=1000

while [[ $# -gt 0 ]]; do
  case "$1" in
    -t|--target)    target="${2-}"; shift 2 ;;
    -p|--pattern)   pattern="${2-}"; shift 2 ;;
    -F|--fixed)     grep_flag="-F"; shift ;;
    -T|--timeout)   hard_timeout="${2-}"; shift 2 ;;
    --stale)        stale_timeout="${2-}"; shift 2 ;;
    -i|--interval)  interval="${2-}"; shift 2 ;;
    -l|--lines)     lines="${2-}"; shift 2 ;;
    -h|--help)
      echo "Usage: wait-for-text.sh -t <session:win.pane> -p <pattern> [--stale secs | -T secs] [-i secs]"
      echo ""
      echo "  --stale <s>  Timeout only if output unchanged for <s> seconds (default: 300)"
      echo "  -T <s>       Hard timeout after <s> seconds regardless"
      exit 0
      ;;
    *) echo "Unknown option: $1" >&2; exit 1 ;;
  esac
done

[[ -z "$target" || -z "$pattern" ]] && { echo "target (-t) and pattern (-p) required" >&2; exit 1; }

start_epoch=$(date +%s)
last_output=""
last_change_epoch=$start_epoch

while true; do
  pane_text="$(tmux capture-pane -p -J -t "$target" -S "-${lines}" 2>/dev/null || true)"

  # Check for pattern match
  if printf '%s\n' "$pane_text" | grep $grep_flag -- "$pattern" >/dev/null 2>&1; then
    exit 0
  fi

  now=$(date +%s)

  # Track output changes
  if [[ "$pane_text" != "$last_output" ]]; then
    last_output="$pane_text"
    last_change_epoch=$now
  fi

  # Hard timeout (if set)
  if (( hard_timeout > 0 )) && (( now - start_epoch >= hard_timeout )); then
    echo "Hard timeout after ${hard_timeout}s waiting for: $pattern" >&2
    exit 1
  fi

  # Stale timeout — only fire if output hasn't changed
  if (( stale_timeout > 0 )) && (( now - last_change_epoch >= stale_timeout )); then
    echo "Stale timeout: no output change for ${stale_timeout}s waiting for: $pattern" >&2
    exit 1
  fi

  sleep "$interval"
done
