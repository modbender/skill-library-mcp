#!/bin/bash
# OpenClaw Anti-Bot Browser Launcher
# Perplexity PRO Integration - Levels 1-6 Anti-Bot Protection

set -e

# Configuration
PROFILE_DIR="${HOME}/.openclaw/browser-profile"
XVFB_DISPLAY=":99"
CDP_PORT=18800
LOG_FILE="/tmp/chrome_stealth.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting OpenClaw Stealth Browser...${NC}"

# Kill existing instances
echo "Cleaning up existing processes..."
pkill -f "Xvfb ${XVFB_DISPLAY}" 2>/dev/null || true
pkill -f "google-chrome.*remote-debugging-port=${CDP_PORT}" 2>/dev/null || true
sleep 1

# Create persistent profile directory
echo "Setting up persistent profile at ${PROFILE_DIR}..."
mkdir -p "${PROFILE_DIR}"

# Check if Xvfb is installed
if ! command -v Xvfb &> /dev/null; then
    echo -e "${RED}Error: Xvfb is not installed. Run: sudo apt-get install -y Xvfb${NC}"
    exit 1
fi

# Check if Google Chrome is installed
if ! command -v google-chrome &> /dev/null; then
    echo -e "${RED}Error: Google Chrome is not installed.${NC}"
    echo "Install from: https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb"
    exit 1
fi

# Start Xvfb (virtual display)
echo "Starting Xvfb on display ${XVFB_DISPLAY}..."
export DISPLAY=${XVFB_DISPLAY}
Xvfb ${XVFB_DISPLAY} -screen 0 1920x1080x24 -ac +extension GLX +render -noreset &
XVFB_PID=$!
sleep 2

# Verify Xvfb started
if ! ps -p ${XVFB_PID} > /dev/null; then
    echo -e "${RED}Error: Xvfb failed to start${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Xvfb running (PID: ${XVFB_PID})${NC}"

# Start Chrome with anti-bot settings
echo "Starting Chrome with stealth settings..."
google-chrome \
    --no-sandbox \
    --disable-setuid-sandbox \
    --disable-dev-shm-usage \
    --disable-gpu \
    --disable-software-rasterizer \
    --remote-debugging-port=${CDP_PORT} \
    --user-data-dir=${PROFILE_DIR} \
    --window-size=1920,1080 \
    --force-color-profile=srgb \
    --disable-blink-features=AutomationControlled \
    --disable-features=IsolateOrigins,site-per-process,Translate \
    --no-first-run \
    --no-default-browser-check \
    --password-store=basic \
    --use-mock-keychain \
    --enable-features=NetworkService,NetworkServiceInProcess \
    --disable-background-timer-throttling \
    --disable-backgrounding-occluded-windows \
    --disable-renderer-backgrounding \
    --disable-background-networking \
    --enable-automation=false \
    > "${LOG_FILE}" 2>&1 &

CHROME_PID=$!

# Wait for Chrome to be ready
echo -n "Waiting for Chrome to start"
for i in {1..15}; do
    sleep 1
    echo -n "."
    if curl -s http://127.0.0.1:${CDP_PORT}/json/version > /dev/null 2>&1; then
        echo ""
        echo -e "${GREEN}✓ Chrome running (PID: ${CHROME_PID})${NC}"
        echo -e "${GREEN}✓ CDP Endpoint: http://127.0.0.1:${CDP_PORT}${NC}"
        echo ""
        echo "User-Agent:"
        curl -s http://127.0.0.1:${CDP_PORT}/json/version | grep -o '"User-Agent": "[^"]*"' || echo "Unknown"
        echo ""
        echo -e "${YELLOW}Profile location:${NC} ${PROFILE_DIR}"
        echo -e "${YELLOW}Log file:${NC} ${LOG_FILE}"
        exit 0
    fi
done

echo ""
echo -e "${RED}✗ Chrome failed to start within 15 seconds${NC}"
echo "Check log: ${LOG_FILE}"
exit 1
