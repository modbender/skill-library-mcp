#!/usr/bin/env bash
set -euo pipefail
BASE_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=bin/persistent-code-terminal-lib.sh
source "$BASE_DIR/persistent-code-terminal-lib.sh"
PROJECT_OVERRIDE=""

while [ "$#" -gt 0 ]; do
  case "$1" in
    --project)
      if [ "$#" -lt 2 ]; then
        echo "--project requires a value." >&2
        exit 1
      fi
      PROJECT_OVERRIDE="$2"
      shift 2
      ;;
    -h|--help)
      echo "Usage: persistent-code-terminal-start.sh [--project <custom-name>]"
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      exit 1
      ;;
  esac
done

if [ -n "$PROJECT_OVERRIDE" ]; then
  SESSION="$(session_name_from_project "$PROJECT_OVERRIDE")"
else
  SESSION="$(session_name)"
fi

require_tmux
if tmux has-session -t "$SESSION" 2>/dev/null; then
  echo "Using existing session: $SESSION"
  pct_state_update_start "$SESSION"
  exit 0
fi

tmux new-session -d -s "$SESSION" -c "$(pwd)"
echo "Created session: $SESSION"
pct_state_update_start "$SESSION"
