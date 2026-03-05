#!/bin/bash
# Pixel Lobster — launch the bundled app
# Usage: bash launch.sh [skill_dir]
#
# The app is bundled inside this skill — no external clone required.
# skill_dir defaults to the directory containing this script's parent.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
APP_DIR="${1:-$SKILL_DIR/app}"

if [ ! -f "$APP_DIR/main.js" ]; then
  echo "App not found at: $APP_DIR"
  exit 1
fi

cd "$APP_DIR" || exit 1

# Copy default config if none exists
if [ ! -f "config.json" ]; then
  cp "$SKILL_DIR/app/config.json" config.json
fi

if [ ! -d "node_modules" ]; then
  echo "Installing dependencies (first run only)..."
  npm install
fi

echo "Starting Pixel Lobster..."
npx electron .
