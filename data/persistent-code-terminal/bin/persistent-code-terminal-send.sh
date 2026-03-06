#!/usr/bin/env bash
set -euo pipefail
BASE_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=bin/persistent-code-terminal-lib.sh
source "$BASE_DIR/persistent-code-terminal-lib.sh"
SESSION="$(session_name)"
DRY_RUN=0
TIMEOUT=""
PHASE=""

usage() {
  cat <<'EOF_USAGE'
Usage:
  persistent-code-terminal-send.sh [--dry-run] [--timeout <seconds>] [--phase <name>] "<command>"
EOF_USAGE
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    --timeout)
      if [ "$#" -lt 2 ]; then
        echo "--timeout requires a value in seconds." >&2
        exit 1
      fi
      TIMEOUT="$2"
      shift 2
      ;;
    --phase)
      if [ "$#" -lt 2 ]; then
        echo "--phase requires a value." >&2
        exit 1
      fi
      PHASE="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    --)
      shift
      break
      ;;
    -*)
      echo "Unknown option: $1" >&2
      usage >&2
      exit 1
      ;;
    *)
      break
      ;;
  esac
done

CMD="${1:-}"
if [ -z "$CMD" ]; then
  echo "No command provided." >&2
  usage >&2
  exit 1
fi

if [ -n "$TIMEOUT" ] && ! [[ "$TIMEOUT" =~ ^[0-9]+$ ]]; then
  echo "--timeout must be an integer number of seconds." >&2
  exit 1
fi

INNER_CMD="$CMD; printf '\\n__PCT_EXIT_CODE__%s\\n' \$?"
WRAPPED_ARGS=(bash -lc "$INNER_CMD")
WRAPPED_CMD=""
for arg in "${WRAPPED_ARGS[@]}"; do
  WRAPPED_CMD+="$(printf "%q " "$arg")"
done
WRAPPED_CMD="${WRAPPED_CMD% }"

if [ "$DRY_RUN" -eq 1 ]; then
  echo "$WRAPPED_CMD"
  exit 0
fi

ensure_session
pct_state_update_send "$CMD" "$PHASE"

BASE_SENTINEL_COUNT="$(tmux capture-pane -pt "$SESSION" -S -2000 | grep -c '__PCT_EXIT_CODE__' || true)"
tmux send-keys -t "$SESSION" "$WRAPPED_CMD" C-m

if [ -z "$TIMEOUT" ]; then
  exit 0
fi

START_TS=$SECONDS
while [ $((SECONDS - START_TS)) -lt "$TIMEOUT" ]; do
  READ_OUTPUT="$($BASE_DIR/persistent-code-terminal-read.sh)"
  CURRENT_SENTINEL_COUNT="$(printf '%s\n' "$READ_OUTPUT" | grep -c '__PCT_EXIT_CODE__' || true)"
  if [ "$CURRENT_SENTINEL_COUNT" -gt "$BASE_SENTINEL_COUNT" ] && printf '%s\n' "$READ_OUTPUT" | grep -Eq '__PCT_EXIT_CODE__[0-9]+'; then
    printf '%s\n' "$READ_OUTPUT"
    exit 0
  fi
  sleep 0.2
done

echo "Timed out waiting for command to finish"
echo "Tip: $BASE_DIR/persistent-code-terminal-attach.sh to watch progress."
exit 124
