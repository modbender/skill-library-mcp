#!/usr/bin/env bash
set -euo pipefail

BASE_DIR="$(cd "$(dirname "$0")/.." && pwd)"
LOG_DIR="$BASE_DIR/logs"
STATE_DIR="$BASE_DIR/state"
mkdir -p "$LOG_DIR" "$STATE_DIR"

# Load .env if present in skill root
if [ -f "$BASE_DIR/.env" ]; then
  set -a
  . "$BASE_DIR/.env"
  set +a
fi

TS="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
LOG_FILE="$LOG_DIR/poll-$(date -u +%Y%m%d).log"

{
  echo "[$TS] poll-pending START"
  python3 "$BASE_DIR/scripts/yuboto_cli.py" --state-dir "$STATE_DIR" poll-pending
  echo "[$TS] poll-pending END"
} | tee -a "$LOG_FILE"
