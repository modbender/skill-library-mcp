#!/usr/bin/env bash
set -euo pipefail
BASE_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=bin/persistent-code-terminal-lib.sh
source "$BASE_DIR/persistent-code-terminal-lib.sh"

require_tmux

PROJECT_DIR="$(pwd -P)"
SESSION="$(session_name)"
SESSION_STATUS="missing"
LAST_COMMAND=""
LAST_EXIT="unknown"

if has_session; then
  SESSION_STATUS="exists"
fi

if [ -f "$(pct_state_path)" ]; then
  LAST_COMMAND="$(pct_state_read_string "lastCommand")"
  LAST_EXIT_TOKEN="$(pct_state_read_token "lastExitCode" 2>/dev/null || true)"
  if [ -n "$LAST_EXIT_TOKEN" ] && [ "$LAST_EXIT_TOKEN" != "null" ]; then
    LAST_EXIT="$LAST_EXIT_TOKEN"
  fi
fi

if [ -z "$LAST_COMMAND" ]; then
  LAST_COMMAND="(none)"
fi

GIT_STATE="n/a"
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  if [ -n "$(git status --porcelain)" ]; then
    GIT_STATE="dirty"
  else
    GIT_STATE="clean"
  fi
fi

printf 'Project: %s\n' "$PROJECT_DIR"
printf 'Session: %s (%s)\n' "$SESSION" "$SESSION_STATUS"
printf 'Last command: %s\n' "$LAST_COMMAND"
printf 'Last exit code: %s\n' "$LAST_EXIT"
printf 'Git: %s\n' "$GIT_STATE"
