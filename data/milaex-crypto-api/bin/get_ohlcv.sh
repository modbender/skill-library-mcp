#!/usr/bin/env bash
set -euo pipefail
python3 "$(dirname "$0")/../scripts/get_ohlcv.py" "$@"
