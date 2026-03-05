#!/bin/bash
set -e

# Detect OpenClaw install path
OPENCLAW_PATH=$(dirname "$(which openclaw 2>/dev/null || echo "")")
if [ -z "$OPENCLAW_PATH" ] || [ ! -d "$OPENCLAW_PATH" ]; then
  # Try common locations
  for p in \
    "$HOME/.npm-global/lib/node_modules/openclaw" \
    "/usr/local/lib/node_modules/openclaw" \
    "/usr/lib/node_modules/openclaw" \
    "$(npm root -g 2>/dev/null)/openclaw"; do
    if [ -d "$p" ]; then
      OPENCLAW_PATH="$p"
      break
    fi
  done
fi

if [ -z "$OPENCLAW_PATH" ] || [ ! -d "$OPENCLAW_PATH" ]; then
  echo "ERROR: Could not find OpenClaw installation. Install OpenClaw first."
  exit 1
fi

echo "OpenClaw found at: $OPENCLAW_PATH"

# Install xvfb (virtual display)
echo ""
echo "=== Installing xvfb ==="
if command -v Xvfb &>/dev/null; then
  echo "xvfb already installed ✓"
else
  if command -v apt-get &>/dev/null; then
    sudo apt-get update && sudo apt-get install -y xvfb
  elif command -v dnf &>/dev/null; then
    sudo dnf install -y xorg-x11-server-Xvfb
  elif command -v pacman &>/dev/null; then
    sudo pacman -S --noconfirm xorg-server-xvfb
  else
    echo "ERROR: Could not detect package manager. Install xvfb manually."
    exit 1
  fi
fi

# Install Patchright
echo ""
echo "=== Installing Patchright ==="
cd "$OPENCLAW_PATH"
if node -e "require('patchright')" 2>/dev/null; then
  echo "Patchright already installed ✓"
else
  npm install patchright --legacy-peer-deps
fi

# Install Patchright's Chromium
echo ""
echo "=== Installing Chromium for Patchright ==="
ARCH=$(uname -m)
if [ "$ARCH" = "aarch64" ] || [ "$ARCH" = "arm64" ]; then
  echo "ARM64 detected — installing Chromium (Google Chrome not available on ARM64)"
  npx patchright install chromium
else
  echo "x86_64 detected — installing Google Chrome (recommended for best stealth)"
  npx patchright install chrome 2>/dev/null || {
    echo "Chrome install failed, falling back to Chromium"
    npx patchright install chromium
  }
fi

# Install Playwright deps (system libraries needed by Chromium)
echo ""
echo "=== Installing Chromium system dependencies ==="
npx patchright install-deps chromium 2>/dev/null || {
  echo "WARN: Could not install system deps automatically. If the browser fails to launch, install them manually."
}

# Verify
echo ""
echo "=== Verifying ==="
RESULT=$(xvfb-run --auto-servernum node -e "
const { createRequire } = require('module');
const pr = require('patchright');
(async () => {
  const browser = await pr.chromium.launch({ headless: false, args: ['--no-sandbox'] });
  const page = await browser.newPage();
  await page.goto('https://example.com');
  console.log('Title: ' + await page.title());
  await browser.close();
  console.log('OK');
})().catch(e => { console.error('FAIL:', e.message); process.exit(1); });
" 2>&1)

echo "$RESULT"

if echo "$RESULT" | grep -q "OK"; then
  echo ""
  echo "✅ Setup complete! Stealth browser is working."
  echo "OpenClaw path: $OPENCLAW_PATH"
else
  echo ""
  echo "❌ Verification failed. Check the error above."
  exit 1
fi
