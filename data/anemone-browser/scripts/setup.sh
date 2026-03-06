#!/bin/bash
# === One-time setup: Install Chrome + VNC dependencies ===
# Run inside the Docker container once.
set -e

echo "=== Installing dependencies ==="
apt-get update -qq
DEBIAN_FRONTEND=noninteractive apt-get install -y -qq \
  wget curl gnupg2 \
  xvfb x11vnc novnc websockify fluxbox \
  openssl \
  2>&1 | tail -5

# Install Google Chrome if not present
if ! command -v google-chrome-stable &>/dev/null; then
  echo "=== Installing Google Chrome ==="
  wget -q -O /tmp/chrome.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
  apt-get install -y -qq /tmp/chrome.deb 2>&1 | tail -3
  rm -f /tmp/chrome.deb
fi

# Install Python websockets for CDP testing
pip3 install websockets --break-system-packages -q 2>/dev/null || true

# Copy start script
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
if [ -f "$SCRIPT_DIR/start.sh" ]; then
  cp "$SCRIPT_DIR/start.sh" /root/start.sh
  chmod +x /root/start.sh
fi

echo "=== Setup complete ==="
echo "Chrome: $(google-chrome-stable --version 2>/dev/null || echo 'not found')"
echo "Run: bash /root/start.sh [password] [novnc_port] [cdp_port]"
