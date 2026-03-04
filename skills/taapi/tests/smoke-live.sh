#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CLI="$ROOT_DIR/scripts/taapi-agent.sh"
EXAMPLES_DIR="$ROOT_DIR/examples"

if [[ -z "${TAAPI_SECRET:-}" ]]; then
  echo "error: set TAAPI_SECRET before running live smoke tests" >&2
  exit 1
fi

echo "[1/3] direct rsi"
"$CLI" direct \
  --indicator rsi \
  --exchange binance \
  --symbol BTC/USDT \
  --interval 1h \
  --json >/dev/null

echo "[2/3] bulk single construct"
"$CLI" bulk \
  --payload-file "$EXAMPLES_DIR/bulk-single-construct.json" \
  --json >/dev/null

echo "[3/3] multi constructs from flags"
"$CLI" multi \
  --exchange binance \
  --symbols BTC/USDT,ETH/USDT \
  --intervals 15m,1h \
  --indicators rsi,supertrend \
  --json >/dev/null

echo "live smoke tests passed"
