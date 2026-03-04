#!/bin/bash
# check.sh — Local sanity checks for Codeflow scripts
#
# Runs:
#  - Python syntax compile (py_compile) for all *.py under scripts/
#  - Unit tests (unittest discover) under scripts/tests/ when present
#  - Bash syntax check (bash -n) for all *.sh under scripts/

set -euo pipefail

BIN_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$BIN_DIR/../.." && pwd)"
PY_DIR="$(cd "$BIN_DIR/../py" && pwd)"

echo "== codeflow: python compile =="
PY_FILES=()
while IFS= read -r -d '' f; do
  PY_FILES+=("$f")
done < <(find "$PY_DIR" -type f -name '*.py' -print0)

if [ "${#PY_FILES[@]}" -gt 0 ]; then
  python3 -m py_compile "${PY_FILES[@]}"
else
  echo "(no python files found)"
fi

echo "== codeflow: unit tests =="
if [ -d "$PY_DIR/tests" ]; then
  python3 -m unittest discover -s "$PY_DIR/tests" -p 'test_*.py'
else
  echo "(no scripts/tests directory)"
fi

echo "== codeflow: bash syntax =="
SH_FILES=()
while IFS= read -r -d '' f; do
  SH_FILES+=("$f")
done < <(find "$BIN_DIR" -type f -name '*.sh' -print0)

if [ "${#SH_FILES[@]}" -gt 0 ]; then
  for f in "${SH_FILES[@]}"; do
    bash -n "$f"
  done
else
  echo "(no shell scripts found)"
fi

# Also validate the public router entrypoint (scripts/codeflow).
if [ -f "$ROOT_DIR/codeflow" ]; then
  bash -n "$ROOT_DIR/codeflow"
fi

echo "OK"
