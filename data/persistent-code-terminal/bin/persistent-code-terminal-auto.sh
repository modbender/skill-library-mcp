#!/usr/bin/env bash
set -euo pipefail
BASE_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=bin/persistent-code-terminal-lib.sh
source "$BASE_DIR/persistent-code-terminal-lib.sh"

MAX_RETRIES=3
INSTRUCTION=""
TIMEOUT=""
JSON_MODE=0

usage() {
  cat <<'EOF_USAGE'
Usage:
  persistent-code-terminal-auto.sh --instruction "<text>" [--max-retries <N>] [--timeout <seconds>] [--json]
EOF_USAGE
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --max-retries)
      if [ "$#" -lt 2 ]; then
        echo "--max-retries requires a value." >&2
        exit 1
      fi
      MAX_RETRIES="$2"
      shift 2
      ;;
    --instruction)
      if [ "$#" -lt 2 ]; then
        echo "--instruction requires a value." >&2
        exit 1
      fi
      INSTRUCTION="$2"
      shift 2
      ;;
    --timeout)
      if [ "$#" -lt 2 ]; then
        echo "--timeout requires a value." >&2
        exit 1
      fi
      TIMEOUT="$2"
      shift 2
      ;;
    --json)
      JSON_MODE=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
done

if [ -z "$INSTRUCTION" ]; then
  echo "--instruction is required." >&2
  usage >&2
  exit 1
fi

if ! [[ "$MAX_RETRIES" =~ ^[1-9][0-9]*$ ]]; then
  echo "--max-retries must be a positive integer." >&2
  exit 1
fi

if [ -n "$TIMEOUT" ] && ! [[ "$TIMEOUT" =~ ^[0-9]+$ ]]; then
  echo "--timeout must be an integer number of seconds." >&2
  exit 1
fi

parse_last_exit_from_read_json() {
  awk -F: '/"lastExitCode"/ {gsub(/[ ,]/, "", $2); print $2; exit}'
}

wait_for_completion() {
  local timeout="${1:-}"
  local start_ts read_json exit_token

  start_ts=$SECONDS
  while :; do
    read_json="$("$BASE_DIR/persistent-code-terminal-read.sh" --json)"
    exit_token="$(printf '%s\n' "$read_json" | parse_last_exit_from_read_json)"
    if [ -n "$exit_token" ] && [ "$exit_token" != "null" ]; then
      printf '%s\n' "$exit_token"
      return 0
    fi

    if [ -n "$timeout" ] && [ $((SECONDS - start_ts)) -ge "$timeout" ]; then
      printf '124\n'
      return 124
    fi
    sleep 1
  done
}

if [ "$JSON_MODE" -eq 1 ]; then
  "$BASE_DIR/persistent-code-terminal-start.sh" >/dev/null
else
  "$BASE_DIR/persistent-code-terminal-start.sh" >/dev/null
fi

attempt=0
success=false
final_exit_code="null"
current_instruction="$INSTRUCTION"

while [ "$attempt" -lt "$MAX_RETRIES" ]; do
  attempt=$((attempt + 1))

  if [ -n "$TIMEOUT" ]; then
    if ! PCT_SEND_TIMEOUT="$TIMEOUT" PCT_SEND_PHASE="attempt-$attempt" "$BASE_DIR/persistent-code-terminal-codex-exec.sh" "$current_instruction" >/dev/null 2>&1; then
      :
    fi
  else
    if ! PCT_SEND_PHASE="attempt-$attempt" "$BASE_DIR/persistent-code-terminal-codex-exec.sh" "$current_instruction" >/dev/null 2>&1; then
      :
    fi
  fi

  if [ -n "$TIMEOUT" ]; then
    if exit_value="$(wait_for_completion "$TIMEOUT")"; then
      final_exit_code="$exit_value"
    else
      final_exit_code="124"
    fi
  else
    exit_value="$(wait_for_completion "")"
    final_exit_code="$exit_value"
  fi

  if [ "$final_exit_code" = "0" ]; then
    success=true
    break
  fi

  current_instruction="The previous attempt failed with exit code $final_exit_code. Fix the issues and ensure build/test pass. Do not force push. Do not switch branches. Then rerun necessary checks."
done

LAST_COMMAND="$(pct_state_read_string "lastCommand")"
PHASE="$(pct_state_read_string "phase")"

if [ "$JSON_MODE" -eq 1 ]; then
  cat <<EOF_JSON
{
  "success": ${success},
  "attempts": ${attempt},
  "finalExitCode": ${final_exit_code},
  "lastCommand": "$(pct_json_escape "$LAST_COMMAND")",
  "phase": $(pct_json_quote_or_null "$PHASE")
}
EOF_JSON
else
  if [ "$success" = true ]; then
    RESULT="success"
  else
    RESULT="failure"
  fi
  echo "Auto loop: $RESULT"
  echo "Attempts: $attempt/$MAX_RETRIES"
  echo "Final exit code: $final_exit_code"
fi

if [ "$success" = true ]; then
  exit 0
fi

if [ "$final_exit_code" = "null" ]; then
  exit 1
fi
exit "$final_exit_code"
