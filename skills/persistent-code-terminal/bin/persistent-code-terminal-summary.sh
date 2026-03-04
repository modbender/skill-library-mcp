#!/usr/bin/env bash
set -euo pipefail
BASE_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=bin/persistent-code-terminal-lib.sh
source "$BASE_DIR/persistent-code-terminal-lib.sh"
SESSION="$(session_name)"
LINES=120
JSON_MODE=0

while [ "$#" -gt 0 ]; do
  case "$1" in
    --json)
      JSON_MODE=1
      shift
      ;;
    --lines)
      if [ "$#" -lt 2 ]; then
        echo "--lines requires a number." >&2
        exit 1
      fi
      LINES="$2"
      shift 2
      ;;
    -h|--help)
      echo "Usage: persistent-code-terminal-summary.sh [--lines <n>] [--json]"
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      exit 1
      ;;
  esac
done

if ! [[ "$LINES" =~ ^[0-9]+$ ]]; then
  echo "--lines must be an integer." >&2
  exit 1
fi

if [ "$JSON_MODE" -eq 1 ]; then
  ensure_session >/dev/null
else
  ensure_session
fi

CAPTURED="$(tmux capture-pane -pt "$SESSION" -S "-$LINES")"
LATEST_EXIT="$(printf '%s\n' "$CAPTURED" | sed -n 's/.*__PCT_EXIT_CODE__\([0-9][0-9]*\).*/\1/p' | tail -n 1)"
pct_state_update_read_exit "$LATEST_EXIT"

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
  LAST_EXIT_TOKEN="$LATEST_EXIT"
else
  LAST_EXIT_TOKEN="null"
fi

if [ "$JSON_MODE" -eq 1 ]; then
  ERRORS="$(printf '%s\n' "$CAPTURED" | grep -Ei 'error|failed|exception' || true)"
else
  ERRORS="$(printf '%s\n' "$CAPTURED" | grep -Ei 'error|Error:|FAILED|fail|exception|Traceback' || true)"
fi

if [ "$JSON_MODE" -eq 0 ]; then
  DISPLAY_EXIT="$LAST_EXIT_TOKEN"
  DISPLAY_COMMAND="$LAST_COMMAND"
  if [ -z "$DISPLAY_COMMAND" ]; then
    DISPLAY_COMMAND="(none)"
  fi
  if [ -z "$DISPLAY_EXIT" ] || [ "$DISPLAY_EXIT" = "null" ]; then
    DISPLAY_EXIT="unknown"
  fi

  printf 'Summary: exit=%s | cmd=%s\n' "$DISPLAY_EXIT" "$DISPLAY_COMMAND"
  printf '%s\n' '--- Recent Output ---'
  printf '%s\n' "$CAPTURED"

  if [ -n "$ERRORS" ]; then
    printf '%s\n' '--- Errors (grep) ---'
    printf '%s\n' "$ERRORS" | tail -n 40
  fi
  exit 0
fi

ERROR_LINES_JSON="[]"
if [ -n "$ERRORS" ]; then
  ERROR_LINES_JSON="["
  FIRST_LINE=1
  while IFS= read -r line; do
    if [ -z "$line" ]; then
      continue
    fi
    if [ "$FIRST_LINE" -eq 0 ]; then
      ERROR_LINES_JSON+=", "
    fi
    ERROR_LINES_JSON+="\"$(pct_json_escape "$line")\""
    FIRST_LINE=0
  done <<EOF_ERR_LINES
$ERRORS
EOF_ERR_LINES
  ERROR_LINES_JSON+="]"
fi

cat <<EOF_JSON
{
  "projectDir": "$(pct_json_escape "$PROJECT_DIR")",
  "session": "$(pct_json_escape "$STATE_SESSION")",
  "lastCommand": "$(pct_json_escape "$LAST_COMMAND")",
  "lastExitCode": ${LAST_EXIT_TOKEN},
  "phase": $(pct_json_quote_or_null "$PHASE"),
  "updatedAt": "$(pct_json_escape "$UPDATED_AT")",
  "recentOutput": "$(pct_json_escape "$CAPTURED")",
  "errorLines": ${ERROR_LINES_JSON}
}
EOF_JSON
