#!/usr/bin/env bash
set -euo pipefail

# One-click setup:
# 1) Install/update outsideclaw repo to ~/.outsideclaw/app/outsideclaw
# 2) Patch an OpenClaw config JSON to load the installed skill
# 3) (Optional) Restart OpenClaw gateway
#
# Usage:
#   bash openclaw_oneclick_setup.sh --config /path/to/openclaw.config.json [--restart]

RESTART=0
CONFIG_PATH=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --config)
      CONFIG_PATH="$2"; shift 2 ;;
    --restart)
      RESTART=1; shift 1 ;;
    *)
      echo "Unknown arg: $1"; exit 2 ;;
  esac
done

if [[ -z "$CONFIG_PATH" ]]; then
  echo "Usage: bash openclaw_oneclick_setup.sh --config /path/to/openclaw.config.json [--restart]";
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# step1: install outsideclaw
bash "$SCRIPT_DIR/outsideclaw_setup.sh"

# step2: patch config
node "$SCRIPT_DIR/patch_openclaw_config.js" --config "$CONFIG_PATH"

# step3: restart
if [[ "$RESTART" -eq 1 ]]; then
  if command -v openclaw >/dev/null 2>&1; then
    echo "[openclaw] restarting gateway..."
    openclaw gateway restart
  else
    echo "[openclaw] openclaw CLI not found; please restart gateway manually."
  fi
fi

echo "[oneclick] OK"
