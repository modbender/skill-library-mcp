#!/usr/bin/env bash
set -euo pipefail

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PLUGIN_DIR="$BASE_DIR/plugin"

if [[ ! -f "$PLUGIN_DIR/openclaw.plugin.json" ]]; then
  echo "ERROR: openclaw.plugin.json not found in $PLUGIN_DIR"
  exit 1
fi

echo "Installing plugin from: $PLUGIN_DIR"
openclaw plugins install "$PLUGIN_DIR"

echo "Done. Verify with: openclaw plugins info lunara-voice && openclaw plugins doctor"
