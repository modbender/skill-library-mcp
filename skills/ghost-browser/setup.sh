#!/bin/bash
# Ghost Browser — Setup Script
# Creates a venv and installs nodriver

set -e

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SKILL_DIR/.venv"

echo "=== Ghost Browser Setup ==="

# Check for Chrome
if ! command -v google-chrome &>/dev/null && ! command -v chromium &>/dev/null && \
   ! [ -d "/Applications/Google Chrome.app" ] && ! [ -d "/Applications/Chromium.app" ]; then
    echo "ERROR: Google Chrome or Chromium not found."
    echo "Install Chrome from https://google.com/chrome before using ghost-browser."
    exit 1
fi

# Create venv
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating Python venv..."
    python3 -m venv "$VENV_DIR"
fi

# Install nodriver
echo "Installing nodriver..."
"$VENV_DIR/bin/pip" install --upgrade -r "$SKILL_DIR/requirements.txt"

# Make CLI executable
chmod +x "$SKILL_DIR/scripts/ghost-browser.sh"

echo ""
echo "=== Setup complete ==="
echo "Run: ghost-browser start"
