#!/usr/bin/env bash
set -euo pipefail

# Configure Clawdbot to use Playwright Chromium
# Usage: ./configure-clawdbot.sh [chrome-path]

GREEN='\033[0;32m'
NC='\033[0m'

info() { echo -e "${GREEN}[INFO]${NC} $*"; }

# Find Chrome path
if [[ $# -ge 1 ]]; then
    CHROME_PATH="$1"
else
    CHROME_PATH=$(find ~/.cache/ms-playwright -name "chrome" -path "*/chrome-linux64/*" 2>/dev/null | head -1)
fi

if [[ -z "$CHROME_PATH" || ! -f "$CHROME_PATH" ]]; then
    echo "Error: Chromium executable not found"
    echo "Run: npx playwright install chromium"
    exit 1
fi

info "Using Chromium: $CHROME_PATH"

# Build the config patch
CONFIG_PATCH=$(cat <<EOF
{
  "browser": {
    "executablePath": "$CHROME_PATH",
    "headless": true,
    "noSandbox": true
  }
}
EOF
)

# Apply via clawdbot CLI if available
if command -v clawdbot &>/dev/null; then
    info "Patching Clawdbot config..."
    clawdbot config patch "$CONFIG_PATCH"
    info "Config updated. Gateway will restart."
else
    # Manual fallback - write to config file directly
    CONFIG_FILE="${HOME}/.clawdbot/clawdbot.json"
    if [[ -f "$CONFIG_FILE" ]]; then
        info "clawdbot CLI not found. Manual config patch needed."
        echo ""
        echo "Add this to your clawdbot.json:"
        echo "$CONFIG_PATCH"
    else
        echo "Error: clawdbot not installed or config not found"
        exit 1
    fi
fi

info "Done!"
