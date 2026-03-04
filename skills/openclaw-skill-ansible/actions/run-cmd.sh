#!/usr/bin/env bash
set -euo pipefail

TASK_FILE="$1"
TASK_ID=$(jq -r '.task_id' "$TASK_FILE")
CMD=$(jq -r '.params.cmd // ""' "$TASK_FILE")
TIMEOUT_SECONDS=$(jq -r '.params.timeout // 30' "$TASK_FILE")

ARTROOT=${OPENCLAW_ARTIFACT_ROOT:-/var/lib/openclaw/artifacts}
mkdir -p "$ARTROOT"
OUT="$ARTROOT/${TASK_ID}-run-cmd.json"
STDOUT_LOG="$ARTROOT/${TASK_ID}-stdout.log"
STDERR_LOG="$ARTROOT/${TASK_ID}-stderr.log"

if [ -z "$CMD" ]; then
  echo "Missing params.cmd" >&2
  exit 2
fi

if [ "${OPENCLAW_ALLOW_RUN_CMD:-0}" != "1" ]; then
  echo "run-cmd disabled: set OPENCLAW_ALLOW_RUN_CMD=1" >&2
  exit 3
fi

ALLOWLIST=${OPENCLAW_RUN_CMD_ALLOWLIST:-"openclaw status,openclaw ansible status,openclaw gateway health,openclaw plugins list,openclaw agent --help"}
ALLOWED=0
IFS=',' read -r -a PREFIXES <<< "$ALLOWLIST"
for p in "${PREFIXES[@]}"; do
  TRIM=$(echo "$p" | sed 's/^ *//;s/ *$//')
  if [ -n "$TRIM" ] && [[ "$CMD" == "$TRIM"* ]]; then
    ALLOWED=1
    break
  fi
done

if [ "$ALLOWED" -ne 1 ]; then
  echo "Command blocked by allowlist: $CMD" >&2
  exit 4
fi

set +e
timeout "${TIMEOUT_SECONDS}s" bash -lc "$CMD" >"$STDOUT_LOG" 2>"$STDERR_LOG"
RC=$?
set -e

STATUS="completed"
if [ "$RC" -ne 0 ]; then
  STATUS="failed"
fi

jq -n \
  --arg task_id "$TASK_ID" \
  --arg status "$STATUS" \
  --arg cmd "$CMD" \
  --arg stdout "$(cat "$STDOUT_LOG" 2>/dev/null || true)" \
  --arg stderr "$(cat "$STDERR_LOG" 2>/dev/null || true)" \
  --argjson exit_code "$RC" \
  '{task_id:$task_id,status:$status,command:$cmd,exit_code:$exit_code,stdout:$stdout,stderr:$stderr}' > "$OUT"

[ "$RC" -eq 0 ] || exit "$RC"
