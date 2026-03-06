#!/usr/bin/env bash
set -euo pipefail

# SatGate CLI Health Check
# Validates that the CLI is installed and can reach the gateway.

echo "⚡ SatGate CLI Health Check"
echo "───────────────────────────"

# Check binary
if ! command -v satgate &>/dev/null; then
  echo "❌ satgate binary not found in PATH"
  echo "   Run: scripts/install.sh"
  exit 1
fi
echo "✓ Binary: $(which satgate)"
satgate version

# Check config
CONFIG="${HOME}/.satgate/config.yaml"
if [ -f "$CONFIG" ]; then
  echo "✓ Config: ${CONFIG}"
else
  echo "⚠️  No config file at ${CONFIG}"
  echo "   Using environment variables or defaults"
fi

# Check connection
echo ""
echo "Testing gateway connection..."
if satgate ping; then
  echo ""
  satgate status
else
  echo ""
  echo "❌ Cannot reach gateway"
  echo "   Run: scripts/configure.sh"
  exit 1
fi
