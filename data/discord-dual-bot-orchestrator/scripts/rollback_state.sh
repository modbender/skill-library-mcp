#!/usr/bin/env bash
set -euo pipefail

BK_DIR="${1:-}"
if [[ -z "$BK_DIR" ]]; then
  echo "Usage: $0 <BACKUP_DIR>"
  exit 1
fi

cp -f "$BK_DIR/openclaw.main.json" "$HOME/.openclaw/openclaw.json"
cp -f "$BK_DIR/openclaw.bot-b.json" "$HOME/.openclaw-bot-b/openclaw.json"

echo "Restored configs. Restart gateways manually:"
echo "  openclaw gateway restart"
echo "  openclaw --profile bot-b gateway run --port 28789"
