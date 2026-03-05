#!/usr/bin/env bash
set -euo pipefail
python3 "$(dirname "$0")/../scripts/list_markets.py" "$@"
