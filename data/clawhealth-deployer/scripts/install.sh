#!/usr/bin/env bash
# Install ClawHealth for OpenClaw: clone repo (if needed), run make deploy-openclaw, merge MCP into clawdbot.json5.
# Usage: CLAWHEALTH_INSTALL_DIR=~/ClawHealth ./install.sh
# Requires: docker, docker compose, git, make, node (for merge script), python3 (used by deploy script)

set -e

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
INSTALL_DIR="${CLAWHEALTH_INSTALL_DIR:-$HOME/ClawHealth}"
REPO_URL="${CLAWHEALTH_REPO_URL:-https://github.com/the-momentum/open-wearables.git}"
DEPLOY_JSON="$INSTALL_DIR/.clawhealth-deploy.json"

echo "==> ClawHealth deployer (install dir: $INSTALL_DIR)"

# 1. Clone or update repo
if [[ ! -d "$INSTALL_DIR/.git" ]]; then
  echo "==> Cloning ClawHealth repo..."
  mkdir -p "$(dirname "$INSTALL_DIR")"
  git clone "$REPO_URL" "$INSTALL_DIR"
else
  echo "==> Repo already at $INSTALL_DIR (pull to update: cd $INSTALL_DIR && git pull)"
fi

# 2. Deploy (backend + API key + MCP .env)
echo "==> Running make deploy-openclaw..."
(cd "$INSTALL_DIR" && make deploy-openclaw)

# 3. Merge MCP into clawdbot.json5
if [[ ! -f "$DEPLOY_JSON" ]]; then
  echo "Error: Expected $DEPLOY_JSON after deploy. Run deploy manually: cd $INSTALL_DIR && make deploy-openclaw"
  exit 1
fi

# Install json5 if needed and run merge (must run from SKILL_DIR so require('json5') works)
if [[ ! -d "$SKILL_DIR/node_modules" ]]; then
  echo "==> Installing merge script deps..."
  (cd "$SKILL_DIR" && npm install)
fi
(cd "$SKILL_DIR" && node scripts/merge-mcp.js "$DEPLOY_JSON")

echo ""
echo "==> Done. Restart OpenClaw gateway: clawdbot gateway restart"
echo "    Then in OpenClaw (e.g. Telegram) ask: \"Who can I query health data for?\" or \"How did I sleep last week?\""
