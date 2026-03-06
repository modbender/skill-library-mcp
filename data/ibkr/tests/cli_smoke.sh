#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

python3 -m py_compile \
  scripts/ibkr_cli.py \
  scripts/get_account_info.py \
  scripts/get_historical_data.py \
  scripts/place_order.py

python3 scripts/ibkr_cli.py --help >/dev/null
python3 scripts/ibkr_cli.py historical --help >/dev/null
python3 scripts/ibkr_cli.py place-order --help >/dev/null

./scripts/ibkr.sh >/dev/null 2>&1 || true
./scripts/ibkr.sh quote --help >/dev/null
./scripts/openclaw.sh quote --help >/dev/null

echo "CLI smoke checks passed"
