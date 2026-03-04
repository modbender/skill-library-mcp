#!/usr/bin/env bash
set -euo pipefail

CONFIG="$HOME/.openclaw/openclaw.json"
APPLY_CMD=""
ACK_TIMEOUT=45
REQUIRE_ACK=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --config) CONFIG="$2"; shift 2 ;;
    --apply-cmd) APPLY_CMD="$2"; shift 2 ;;
    --ack-timeout) ACK_TIMEOUT="$2"; shift 2 ;;
    --require-ack) REQUIRE_ACK=1; shift 1 ;;
    *) echo "unknown arg: $1"; exit 1 ;;
  esac
done

if [[ -z "$APPLY_CMD" ]]; then
  echo "--apply-cmd is required"
  exit 1
fi

TS="$(date +%Y%m%d-%H%M%S)"
BACKUP="${CONFIG}.bak.${TS}"
ACK_FILE="/tmp/openclaw-config-ack-${TS}.ok"
STATUS_FILE="/tmp/openclaw-safe-status-${TS}.txt"

cp "$CONFIG" "$BACKUP"
echo "[safe-apply] backup: $BACKUP"

eval "$APPLY_CMD"

echo "[safe-apply] restarting gateway..."
openclaw gateway restart >/dev/null 2>&1 || true
sleep 2

if ! openclaw gateway status >"$STATUS_FILE" 2>&1 || ! grep -q "RPC probe: ok" "$STATUS_FILE"; then
  echo "[safe-apply] health check failed -> rollback"
  cp "$BACKUP" "$CONFIG"
  openclaw gateway restart >/dev/null 2>&1 || true
  sleep 2
  exit 2
fi

echo "[safe-apply] health check passed"

if [[ "$REQUIRE_ACK" -eq 1 ]]; then
  echo "[safe-apply] ack required within ${ACK_TIMEOUT}s"
  echo "[safe-apply] ack file: $ACK_FILE"
  echo "touch '$ACK_FILE'"

  elapsed=0
  while [[ $elapsed -lt $ACK_TIMEOUT ]]; do
    if [[ -f "$ACK_FILE" ]]; then
      echo "[safe-apply] ack received"
      rm -f "$ACK_FILE"
      exit 0
    fi
    sleep 1
    elapsed=$((elapsed+1))
  done

  echo "[safe-apply] ack timeout -> rollback"
  cp "$BACKUP" "$CONFIG"
  openclaw gateway restart >/dev/null 2>&1 || true
  sleep 2
  exit 3
fi

echo "[safe-apply] done"
