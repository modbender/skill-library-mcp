#!/usr/bin/env bash
# setup.sh — One-time setup for Confidant skill
# Installs the CLI globally for fast execution (no npx overhead)

set -euo pipefail

# --- Dependency checks (fail fast with machine-readable errors) ---

if ! command -v npm &>/dev/null; then
  echo '{"error":"npm is required but not found","code":"MISSING_DEPENDENCY","hint":"Install Node.js from https://nodejs.org"}' >&2
  echo "ERROR: npm not found. Install Node.js first: https://nodejs.org" >&2
  exit 2
fi

if ! command -v jq &>/dev/null; then
  echo '{"error":"jq is required but not found","code":"MISSING_DEPENDENCY","hint":"Ubuntu/Debian: apt-get install -y jq | macOS: brew install jq"}' >&2
  echo "ERROR: jq not found." >&2
  echo "  Ubuntu/Debian: apt-get install -y jq" >&2
  echo "  macOS:         brew install jq" >&2
  exit 2
fi

# --- Install Confidant CLI (idempotent) ---

if command -v confidant &>/dev/null; then
  echo "✅ confidant already installed: $(confidant --version 2>/dev/null || echo 'version unknown')"
else
  echo "📦 Installing Confidant CLI globally..."
  npm install -g @aiconnect/confidant
fi

# --- Install localtunnel (idempotent) ---

if command -v lt &>/dev/null; then
  echo "✅ localtunnel already installed: $(lt --version 2>/dev/null || echo 'version unknown')"
else
  echo "📦 Installing localtunnel globally (for --tunnel support)..."
  npm install -g localtunnel
fi

echo ""
echo "✅ Setup complete!"
echo "   - confidant $(confidant --version 2>/dev/null || echo '(installed)')"
echo "   - lt $(lt --version 2>/dev/null || echo '(installed)')"
