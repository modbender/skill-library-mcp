#!/usr/bin/env bash
set -euo pipefail

BASE_DIR="$(cd "$(dirname "$0")" && pwd)"
SESSION="$("$BASE_DIR/persistent-code-terminal-session-name.sh")"
INSTR=""
USER_FLAGS=()

usage() {
  cat <<'EOF'
Usage:
  persistent-code-terminal-codex-exec.sh "<instruction>"
  persistent-code-terminal-codex-exec.sh [codex exec flags...] "<instruction>"

Behavior:
  - By default, this script runs:
      codex exec --full-auto --sandbox workspace-write --cd <current-dir> "<instruction>"
  - Set PCT_CODEX_NO_DEFAULT_FLAGS=1 to disable default flags.

Examples:
  persistent-code-terminal-codex-exec.sh "Fix tests and commit."
  persistent-code-terminal-codex-exec.sh --json -o /tmp/codex.json "Implement feature X."
EOF
}

if [ "${1:-}" = "-h" ] || [ "${1:-}" = "--help" ]; then
  usage
  exit 0
fi

if [ "$#" -lt 1 ]; then
  usage
  exit 1
fi

if [ "$#" -eq 1 ]; then
  INSTR="$1"
else
  INSTR="${!#}"
  USER_FLAGS=("${@:1:$#-1}")
fi

if [ -z "$INSTR" ]; then
  usage
  exit 1
fi

command -v codex >/dev/null 2>&1 || {
  echo "codex not found. Install Codex CLI first (command name must be 'codex')."
  exit 1
}

DEFAULT_FLAGS=()
if [ "${PCT_CODEX_NO_DEFAULT_FLAGS:-0}" != "1" ]; then
  DEFAULT_FLAGS=(--full-auto --sandbox workspace-write --cd "$(pwd)")
fi

CMD=(codex exec "${DEFAULT_FLAGS[@]}" "${USER_FLAGS[@]}" "$INSTR")
CMD_STR=""
for arg in "${CMD[@]}"; do
  CMD_STR+="$(printf "%q " "$arg")"
done
CMD_STR="${CMD_STR% }"

# Ensure session exists
"$BASE_DIR/persistent-code-terminal-start.sh"

# Run Codex one-shot inside the persistent session
SEND_ARGS=()
if [ -n "${PCT_SEND_TIMEOUT:-}" ]; then
  SEND_ARGS+=(--timeout "$PCT_SEND_TIMEOUT")
fi
if [ -n "${PCT_SEND_PHASE:-}" ]; then
  SEND_ARGS+=(--phase "$PCT_SEND_PHASE")
fi

"$BASE_DIR/persistent-code-terminal-send.sh" "${SEND_ARGS[@]}" "$CMD_STR"
"$BASE_DIR/persistent-code-terminal-read.sh"

echo "Codex started in session: $SESSION"
echo "Tip: $BASE_DIR/persistent-code-terminal-attach.sh to watch progress."
