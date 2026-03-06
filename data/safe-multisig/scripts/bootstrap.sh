#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [ -d node_modules ]; then
  exit 0
fi

echo "[safe-multisig-skill] Installing node dependencies..."
# Keep output small; disable audit/fund noise.
npm install --no-audit --no-fund --silent
