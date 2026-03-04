#!/usr/bin/env bash
set -euo pipefail

CONFIG="$HOME/.openclaw/openclaw.json"
APPLY_CMD=""
APPLY_FILE=""
ACK_TIMEOUT=45
REQUIRE_ACK=0
NO_RESTART=0
HEALTH_CMD="openclaw gateway status"
HEALTH_GREP="RPC probe: ok"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --config) CONFIG="$2"; shift 2 ;;
    --apply-cmd) APPLY_CMD="$2"; shift 2 ;;
    --apply-file) APPLY_FILE="$2"; shift 2 ;;
    --ack-timeout) ACK_TIMEOUT="$2"; shift 2 ;;
    --require-ack) REQUIRE_ACK=1; shift 1 ;;
    --no-restart) NO_RESTART=1; shift 1 ;;
    --health-cmd) HEALTH_CMD="$2"; shift 2 ;;
    --health-grep) HEALTH_GREP="$2"; shift 2 ;;
    *) echo "unknown arg: $1"; exit 1 ;;
  esac
done

if [[ -z "$APPLY_CMD" && -z "$APPLY_FILE" ]]; then
  echo "--apply-cmd or --apply-file is required"
  exit 1
fi

if [[ -n "$APPLY_CMD" && -n "$APPLY_FILE" ]]; then
  echo "use either --apply-cmd or --apply-file, not both"
  exit 1
fi

TS="$(date +%Y%m%d-%H%M%S)"
BACKUP="${CONFIG}.bak.${TS}"
ACK_FILE="/tmp/openclaw-config-ack-${TS}.ok"
STATUS_FILE="/tmp/openclaw-safe-status-${TS}.txt"

restart_gateway() {
  if [[ "$NO_RESTART" -eq 1 ]]; then
    echo "[safe-apply] skip restart (--no-restart)"
    return 0
  fi
  openclaw gateway restart >/dev/null 2>&1 || true
  sleep 2
}

health_ok() {
  if ! bash -lc "$HEALTH_CMD" >"$STATUS_FILE" 2>&1; then
    return 1
  fi
  grep -q "$HEALTH_GREP" "$STATUS_FILE"
}

rollback() {
  echo "[safe-apply] rollback -> $CONFIG"
  cp "$BACKUP" "$CONFIG"
  restart_gateway
}

cp "$CONFIG" "$BACKUP"
echo "[safe-apply] backup: $BACKUP"

if [[ -n "$APPLY_FILE" ]]; then
  bash "$APPLY_FILE" || { echo "[safe-apply] apply-file failed"; rollback; exit 4; }
else
  bash -lc "$APPLY_CMD" || { echo "[safe-apply] apply-cmd failed"; rollback; exit 4; }
fi

echo "[safe-apply] restarting + health check..."
restart_gateway

if ! health_ok; then
  echo "[safe-apply] health check failed"
  rollback
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

  echo "[safe-apply] ack timeout"
  rollback
  exit 3
fi

echo "[safe-apply] done"
