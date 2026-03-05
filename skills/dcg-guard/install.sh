#!/usr/bin/env bash
set -euo pipefail

echo "=== DCG Guard Installer ==="

# 1. Install DCG binary if missing
if ! command -v dcg &>/dev/null; then
  echo "[1/3] Installing DCG binary..."
  curl -sSL https://raw.githubusercontent.com/Dicklesworthstone/destructive_command_guard/master/install.sh | bash
  echo ""
else
  echo "[1/3] DCG binary already installed: $(which dcg)"
fi

# 2. Find plugin directory (where this script lives)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [[ ! -f "$SCRIPT_DIR/index.ts" ]]; then
  echo "ERROR: index.ts not found in $SCRIPT_DIR"
  exit 1
fi

# 3. Install as linked plugin + restart
if ! command -v openclaw &>/dev/null; then
  echo "ERROR: openclaw CLI not found. Install OpenClaw first: https://docs.openclaw.ai"
  exit 1
fi

echo "[2/3] Linking plugin into OpenClaw..."
openclaw plugins install -l "$SCRIPT_DIR" 2>&1

echo "[3/3] Restarting gateway..."
openclaw gateway restart 2>&1 || echo "NOTE: Gateway restart failed. Run 'openclaw gateway restart' manually."

echo ""
echo "=== DCG Guard installed ==="
echo "Dangerous commands (rm -rf, git push --force, etc.) are now blocked."
echo "Safe commands pass through silently with zero overhead."
