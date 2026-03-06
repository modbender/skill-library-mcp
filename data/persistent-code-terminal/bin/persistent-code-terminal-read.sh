#!/usr/bin/env bash
set -euo pipefail
BASE_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=bin/persistent-code-terminal-lib.sh
source "$BASE_DIR/persistent-code-terminal-lib.sh"
SESSION="$(session_name)"
JSON_MODE=0

while [ "$#" -gt 0 ]; do
  case "$1" in
    --json)
      JSON_MODE=1
      shift
      ;;
    -h|--help)
      echo "Usage: persistent-code-terminal-read.sh [--json]"
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      exit 1
      ;;
  esac
done

if [ "$JSON_MODE" -eq 1 ]; then
  ensure_session >/dev/null
else
  ensure_session
fi

CAPTURED="$(tmux capture-pane -pt "$SESSION" -S -2000)"
LATEST_EXIT="$(printf '%s\n' "$CAPTURED" | sed -n 's/.*__PCT_EXIT_CODE__\([0-9][0-9]*\).*/\1/p' | tail -n 1)"
pct_state_update_read_exit "$LATEST_EXIT"

if [ "$JSON_MODE" -eq 0 ]; then
  printf '%s\n' "$CAPTURED"
  exit 0
fi

PROJECT_DIR="$(pct_state_read_string "projectDir")"
STATE_SESSION="$(pct_state_read_string "session")"
LAST_COMMAND="$(pct_state_read_string "lastCommand")"
PHASE="$(pct_state_read_string "phase")"
UPDATED_AT="$(pct_state_read_string "updatedAt")"

if [ -z "$PROJECT_DIR" ]; then
  PROJECT_DIR="$(pwd -P)"
fi
if [ -z "$STATE_SESSION" ]; then
  STATE_SESSION="$SESSION"
fi
if [ -z "$UPDATED_AT" ]; then
  UPDATED_AT="$(pct_now_utc)"
fi

if [ -n "$LATEST_EXIT" ]; then
  LAST_EXIT_CODE="$LATEST_EXIT"
else
  LAST_EXIT_CODE="null"
fi

cat <<EOF_JSON
{
  "projectDir": "$(pct_json_escape "$PROJECT_DIR")",
  "session": "$(pct_json_escape "$STATE_SESSION")",
  "lastCommand": "$(pct_json_escape "$LAST_COMMAND")",
  "lastExitCode": ${LAST_EXIT_CODE},
  "phase": $(pct_json_quote_or_null "$PHASE"),
  "updatedAt": "$(pct_json_escape "$UPDATED_AT")",
  "recentOutput": "$(pct_json_escape "$CAPTURED")"
}
EOF_JSON
