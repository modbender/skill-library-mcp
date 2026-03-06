#!/usr/bin/env bash
set -euo pipefail

# Install/update outsideclaw repo into a fixed location and initialize it.
# Goal: make OpenClaw integration easy via a single skill.
#
# Default install dir: ~/.outsideclaw/app/outsideclaw
# Usage:
#   bash outsideclaw_setup.sh
#   OUTSIDECLAW_HOME=~/.outsideclaw OUTSIDECLAW_APP_DIR=~/.outsideclaw/app/outsideclaw bash outsideclaw_setup.sh

OUTSIDECLAW_HOME="${OUTSIDECLAW_HOME:-$HOME/.outsideclaw}"
OUTSIDECLAW_APP_DIR="${OUTSIDECLAW_APP_DIR:-$OUTSIDECLAW_HOME/app/outsideclaw}"
OUTSIDECLAW_REPO_URL="${OUTSIDECLAW_REPO_URL:-https://github.com/jack4world/outsideclaw.git}"

mkdir -p "$OUTSIDECLAW_HOME/app"

if [ -d "$OUTSIDECLAW_APP_DIR/.git" ]; then
  echo "[outsideclaw] Updating repo in $OUTSIDECLAW_APP_DIR"
  git -C "$OUTSIDECLAW_APP_DIR" pull --ff-only
else
  echo "[outsideclaw] Cloning repo to $OUTSIDECLAW_APP_DIR"
  git clone "$OUTSIDECLAW_REPO_URL" "$OUTSIDECLAW_APP_DIR"
fi

cd "$OUTSIDECLAW_APP_DIR"

if command -v npm >/dev/null 2>&1; then
  echo "[outsideclaw] Installing npm deps"
  npm install --silent
else
  echo "[outsideclaw] ERROR: npm not found. Install Node.js first."
  exit 2
fi

echo "[outsideclaw] Running setup (db/routes dirs)"
npm run -s setup

echo "[outsideclaw] OK"
echo "OUTSIDECLAW_APP_DIR=$OUTSIDECLAW_APP_DIR"
