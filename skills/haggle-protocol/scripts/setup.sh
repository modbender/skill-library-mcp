#!/usr/bin/env bash
# Haggle Protocol - OpenClaw Skill Setup
# Accessed env vars: HAGGLE_PRIVATE_KEY
# Accessed endpoints: https://registry.npmjs.org (npm install)
set -euo pipefail

echo "Installing Haggle Protocol MCP Server v0.2.0..."
npm install -g @haggle-protocol/mcp@0.2.0

if [ -z "${HAGGLE_PRIVATE_KEY:-}" ]; then
  echo ""
  echo "WARNING: HAGGLE_PRIVATE_KEY is not set."
  echo "Set it in your environment to enable transaction signing:"
  echo "  export HAGGLE_PRIVATE_KEY=\"0x...\""
  echo ""
  echo "IMPORTANT: Use a dedicated wallet with limited funds."
  echo "Do NOT use your main wallet's private key."
  echo ""
  echo "Without it, you can only read negotiation state (read-only mode)."
else
  echo "HAGGLE_PRIVATE_KEY is configured."
  echo "IMPORTANT: Make sure this is a dedicated agent wallet, not your main wallet."
fi

echo ""
echo "Haggle Protocol skill is ready!"
echo "Run: npx @haggle-protocol/mcp@0.2.0"
