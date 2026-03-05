#!/usr/bin/env bash
# ipeaky v5 — monitor.sh
# Usage: bash monitor.sh
# Tests all registered keys and prints a summary. Single-run — use openclaw cron for scheduling.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
KEY_PATHS_DIR="$HOME/.ipeaky/key-paths"
STATUS_FILE="$HOME/.ipeaky/status.json"

if [ ! -d "$KEY_PATHS_DIR" ] || [ -z "$(ls -A "$KEY_PATHS_DIR" 2>/dev/null)" ]; then
  echo "No keys registered yet."
  echo "Store a key first: bash scripts/store_key_v3.sh <SERVICE> <config.path>"
  exit 0
fi

echo "🔍 ipeaky monitor — testing all registered keys"
echo "────────────────────────────────────────────────"

PASS=0
FAIL=0
SKIP=0

for KEY_FILE in "$KEY_PATHS_DIR"/*.txt; do
  SERVICE=$(basename "$KEY_FILE" .txt)
  RESULT=$(bash "$SCRIPT_DIR/test_key_v5.sh" "$SERVICE" 2>&1) || true
  echo "$RESULT"
  if echo "$RESULT" | grep -q "✅"; then
    PASS=$((PASS + 1))
  elif echo "$RESULT" | grep -q "⚠️"; then
    SKIP=$((SKIP + 1))
  else
    FAIL=$((FAIL + 1))
  fi
done

echo "────────────────────────────────────────────────"
echo "Summary: ✅ $PASS OK  ❌ $FAIL FAIL  ⚠️  $SKIP SKIP"
echo "Status written to: $STATUS_FILE"
echo "View dashboard: bash $SCRIPT_DIR/dashboard.sh"
