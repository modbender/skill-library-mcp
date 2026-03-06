#!/usr/bin/env bash
set -euo pipefail

PASS=1
WARN=0

print_fix() {
  echo "  Fix: $1"
}

if command -v tmux >/dev/null 2>&1; then
  echo "[PASS] tmux installed"
else
  echo "[FAIL] tmux missing"
  print_fix "macOS: brew install tmux"
  print_fix "Ubuntu/Debian: sudo apt install tmux"
  PASS=0
fi

if command -v bash >/dev/null 2>&1; then
  echo "[PASS] bash available"
else
  echo "[FAIL] bash missing"
  PASS=0
fi

if command -v codex >/dev/null 2>&1; then
  echo "[PASS] codex available"
else
  echo "[FAIL] codex missing"
  print_fix "Install Codex CLI and ensure command 'codex' is in PATH"
  print_fix "Then verify: command -v codex"
  PASS=0
fi

if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "[PASS] current directory is a git repo"
else
  echo "[FAIL] current directory is not a git repo"
  print_fix "cd <your-repo-root>"
  print_fix "or initialize repo: git init"
  PASS=0
fi

if [ "$PASS" -eq 1 ]; then
  TMP_SESSION="pct-doctor-$$"
  if tmux new-session -d -s "$TMP_SESSION" -c "$(pwd)" >/dev/null 2>&1; then
    tmux kill-session -t "$TMP_SESSION" >/dev/null 2>&1 || true
    echo "[PASS] tmux can create sessions"
  else
    echo "[FAIL] tmux cannot create a session in this environment"
    print_fix "Check tmux permissions and run inside a writable project directory"
    PASS=0
  fi
fi

if [ "$PASS" -eq 1 ]; then
  echo "Doctor result: healthy (ready for persistent-code-terminal + Codex workflow)"
  exit 0
fi

if [ "$WARN" -eq 1 ]; then
  echo "Doctor result: warnings found"
else
  echo "Doctor result: not healthy"
fi
exit 1
