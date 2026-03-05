#!/usr/bin/env bash
set -euo pipefail
BASE_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=bin/persistent-code-terminal-lib.sh
source "$BASE_DIR/persistent-code-terminal-lib.sh"
SESSION="$(session_name)"

require_tmux

if has_session; then
  tmux kill-session -t "$SESSION"
  echo "Killed session: $SESSION"
else
  echo "No session found: $SESSION"
fi
