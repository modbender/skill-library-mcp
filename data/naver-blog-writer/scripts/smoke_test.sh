#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

echo "[1/3] preflight should return RUNNER_NOT_READY without local token"
set +e
OUTPUT="$(bash "$ROOT_DIR/scripts/preflight.sh" 2>&1)"
CODE=$?
set -e

if [[ $CODE -ne 2 ]]; then
  echo "[FAIL] expected exit code 2, got $CODE"
  echo "$OUTPUT"
  exit 1
fi

echo "$OUTPUT" | grep -q '"error": "RUNNER_NOT_READY"'

echo "[2/3] publish input validation"
set +e
OUT2="$(bash "$ROOT_DIR/scripts/publish.sh" --title "" --body "" 2>&1)"
CODE2=$?
set -e
if [[ $CODE2 -eq 0 ]]; then
  echo "[FAIL] publish should fail on empty title/body"
  exit 1
fi
echo "$OUT2" | grep -q 'title and body are required'

echo "[3/3] script syntax check"
bash -n "$ROOT_DIR/scripts/preflight.sh"
bash -n "$ROOT_DIR/scripts/setup_runner.sh"
bash -n "$ROOT_DIR/scripts/publish.sh"

echo "[OK] Smoke test passed"
