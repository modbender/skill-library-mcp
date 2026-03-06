#!/bin/bash
# === Anemone: macOS setup ===
# Configures OpenClaw to use a managed Chrome with anti-detection.
# No VNC needed on Mac (you have a display).
set -e

echo "🌊 Anemone — macOS Setup"
echo "========================"

# Detect Chrome
CHROME_PATHS=(
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
  "/Applications/Google Chrome Canary.app/Contents/MacOS/Google Chrome Canary"
  "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"
  "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"
  "/Applications/Chromium.app/Contents/MacOS/Chromium"
)

CHROME_PATH=""
for p in "${CHROME_PATHS[@]}"; do
  if [ -f "$p" ]; then
    CHROME_PATH="$p"
    echo "✅ Found browser: $p"
    break
  fi
done

if [ -z "$CHROME_PATH" ]; then
  echo "❌ No Chromium-based browser found!"
  echo "   Install Chrome: https://www.google.com/chrome/"
  exit 1
fi

# Check OpenClaw
if ! command -v openclaw &>/dev/null; then
  echo "❌ OpenClaw not found! Install: npm i -g openclaw"
  exit 1
fi

echo ""
echo "Configuring OpenClaw browser..."

# Set browser config via openclaw CLI
openclaw config set browser.enabled true
openclaw config set browser.defaultProfile openclaw
openclaw config set browser.headless false
openclaw config set browser.executablePath "$CHROME_PATH"

echo ""
echo "=========================================="
echo "  Anemone macOS Setup Complete! 🌊"
echo "=========================================="
echo ""
echo "  Browser: $CHROME_PATH"
echo "  Profile: openclaw (managed, isolated)"
echo ""
echo "  Test it:"
echo "    openclaw browser status"
echo "    openclaw browser start"
echo "    openclaw browser open https://www.google.com"
echo ""
echo "  The agent can now use the 'browser' tool"
echo "  with profile=openclaw automatically."
echo "=========================================="
