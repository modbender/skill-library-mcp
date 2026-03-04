#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLIENT="${SCRIPT_DIR}/ares_client.py"

python3 "${CLIENT}" --help >/dev/null

if python3 "${CLIENT}" ico 12345678 >/dev/null 2>&1; then
  echo "Expected invalid IČO to fail"
  exit 1
fi

if python3 "${CLIENT}" search --name ab >/dev/null 2>&1; then
  echo "Expected short search name to fail"
  exit 1
fi

if [[ "${ARES_SMOKE_LIVE:-0}" == "1" ]]; then
  python3 "${CLIENT}" ico 27604977 --json >/dev/null
  python3 "${CLIENT}" search --name Google --limit 3 --json >/dev/null
  python3 "${CLIENT}" search --name Google --limit 3 --pick 1 >/dev/null
fi
