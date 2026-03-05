#!/usr/bin/env bash
set -euo pipefail

PARAKEET_DIR="${PARAKEET_DIR:-$HOME/parakeet-asr}"

if [ ! -x "$PARAKEET_DIR/start-parakeet.sh" ]; then
  echo "start-parakeet.sh not found in $PARAKEET_DIR"
  echo "Run: bash scripts/bootstrap.sh"
  exit 1
fi

cd "$PARAKEET_DIR"
./start-parakeet.sh
