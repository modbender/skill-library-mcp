#!/usr/bin/env bash
set -euo pipefail

echo "🎭 Playwright Browser Setup for Clawdbot"
echo "========================================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

info() { echo -e "${GREEN}[INFO]${NC} $*"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $*"; }
error() { echo -e "${RED}[ERROR]${NC} $*"; exit 1; }

# Step 1: Install Playwright Chromium
info "Installing Playwright Chromium..."
if command -v npx &>/dev/null; then
    npx playwright install chromium
else
    error "npx not found. Install Node.js first."
fi

# Step 2: Find the Chromium executable
CHROME_PATH=$(find ~/.cache/ms-playwright -name "chrome" -path "*/chrome-linux64/*" 2>/dev/null | head -1)
if [[ -z "$CHROME_PATH" ]]; then
    error "Chromium not found after installation"
fi
info "Found Chromium at: $CHROME_PATH"

# Step 3: Check for missing libraries
info "Checking system dependencies..."
MISSING_LIBS=$(ldd "$CHROME_PATH" 2>&1 | grep "not found" || true)
if [[ -n "$MISSING_LIBS" ]]; then
    warn "Missing libraries detected:"
    echo "$MISSING_LIBS"
    echo ""
    info "Installing dependencies (requires sudo)..."
    
    # Detect package manager and install
    if command -v apt-get &>/dev/null; then
        # Try libasound2t64 first (newer Ubuntu), fall back to libasound2
        sudo apt-get update
        sudo apt-get install -y libnss3 || true
        sudo apt-get install -y libasound2t64 2>/dev/null || sudo apt-get install -y libasound2 || true
    elif command -v dnf &>/dev/null; then
        sudo dnf install -y nss alsa-lib
    elif command -v pacman &>/dev/null; then
        sudo pacman -S --noconfirm nss alsa-lib
    else
        warn "Unknown package manager. Install manually: libnss3, libasound2"
    fi
    
    # Verify again
    MISSING_LIBS=$(ldd "$CHROME_PATH" 2>&1 | grep "not found" || true)
    if [[ -n "$MISSING_LIBS" ]]; then
        warn "Some libraries still missing:"
        echo "$MISSING_LIBS"
    fi
else
    info "All system dependencies satisfied"
fi

# Step 4: Test Chromium
info "Testing Chromium..."
if "$CHROME_PATH" --headless --no-sandbox --disable-gpu --dump-dom https://example.com 2>&1 | grep -q "Example Domain"; then
    info "Chromium works!"
else
    error "Chromium test failed"
fi

# Step 5: Configure Clawdbot
info "Configuring Clawdbot..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
"$SCRIPT_DIR/configure-clawdbot.sh" "$CHROME_PATH"

echo ""
echo -e "${GREEN}✅ Setup complete!${NC}"
echo ""
echo "Browser tool is now configured. Test with:"
echo '  browser action=start profile=clawd'
