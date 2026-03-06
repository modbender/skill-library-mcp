#!/bin/bash
# video-proof skill — one-time dependency setup
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "==> Installing Node dependencies..."
cd "$SCRIPT_DIR"
if [ ! -f package.json ]; then
  npm init -y --silent > /dev/null 2>&1
fi
npm install --save playwright@latest yaml@latest 2>&1 | tail -3

echo "==> Installing Playwright Chromium..."
npx playwright install chromium 2>&1 | tail -3

echo "==> Installing Playwright system dependencies..."
npx playwright install-deps chromium 2>&1 | tail -5

echo "==> Checking for ffmpeg..."
if command -v ffmpeg &> /dev/null; then
  echo "    ffmpeg found: $(ffmpeg -version 2>&1 | head -1)"
else
  echo "    ffmpeg not found — attempting install..."
  if command -v apt-get &> /dev/null; then
    sudo apt-get update -qq && sudo apt-get install -y -qq ffmpeg
  elif command -v brew &> /dev/null; then
    brew install ffmpeg
  elif command -v dnf &> /dev/null; then
    sudo dnf install -y ffmpeg
  elif command -v pacman &> /dev/null; then
    sudo pacman -S --noconfirm ffmpeg
  else
    echo "    ⚠ Could not install ffmpeg automatically. Install manually for mp4 conversion."
    echo "    Video recording still works (produces .webm without ffmpeg)."
  fi
fi

echo ""
echo "==> Setup complete! Run a test:"
echo "    node $SCRIPT_DIR/record-proof.js --url http://example.com --goto / --screenshot test --output /tmp/proof-test"
