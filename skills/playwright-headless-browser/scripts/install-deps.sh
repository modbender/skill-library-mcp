#!/usr/bin/env bash
set -euo pipefail

# Install system dependencies for Playwright Chromium
# Run with: sudo ./install-deps.sh

echo "Installing Chromium system dependencies..."

if command -v apt-get &>/dev/null; then
    apt-get update
    apt-get install -y libnss3
    # Ubuntu 24.04+ uses libasound2t64, older uses libasound2
    apt-get install -y libasound2t64 2>/dev/null || apt-get install -y libasound2
    
elif command -v dnf &>/dev/null; then
    dnf install -y nss alsa-lib
    
elif command -v pacman &>/dev/null; then
    pacman -S --noconfirm nss alsa-lib
    
elif command -v apk &>/dev/null; then
    apk add --no-cache nss alsa-lib
    
else
    echo "Unknown package manager. Install these packages manually:"
    echo "  - libnss3 (or nss)"
    echo "  - libasound2 (or alsa-lib)"
    exit 1
fi

echo "✅ Dependencies installed"
