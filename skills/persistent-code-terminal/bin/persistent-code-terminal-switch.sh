#!/usr/bin/env bash
set -euo pipefail
BASE_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=bin/persistent-code-terminal-lib.sh
source "$BASE_DIR/persistent-code-terminal-lib.sh"

PROJECT_NAME=""
SESSION_NAME_ARG=""

while [ "$#" -gt 0 ]; do
  case "$1" in
    --project)
      if [ "$#" -lt 2 ]; then
        echo "--project requires a value." >&2
        exit 1
      fi
      PROJECT_NAME="$2"
      shift 2
      ;;
    --session)
      if [ "$#" -lt 2 ]; then
        echo "--session requires a value." >&2
        exit 1
      fi
      SESSION_NAME_ARG="$2"
      shift 2
      ;;
    -h|--help)
      echo "Usage: persistent-code-terminal-switch.sh (--project <project-name> | --session <session-name>)"
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      exit 1
      ;;
  esac
done

if [ -n "$PROJECT_NAME" ] && [ -n "$SESSION_NAME_ARG" ]; then
  echo "Use either --project or --session, not both." >&2
  exit 1
fi

if [ -z "$PROJECT_NAME" ] && [ -z "$SESSION_NAME_ARG" ]; then
  echo "One of --project or --session is required." >&2
  exit 1
fi

if [ -n "$PROJECT_NAME" ]; then
  TARGET_SESSION="$(session_name_from_project "$PROJECT_NAME")"
else
  TARGET_SESSION="$SESSION_NAME_ARG"
fi

require_tmux
if ! tmux has-session -t "$TARGET_SESSION" 2>/dev/null; then
  echo "Session not found: $TARGET_SESSION" >&2
  exit 1
fi

tmux attach -t "$TARGET_SESSION"
