#!/usr/bin/env bash
# ClawSouls CLI wrapper
# Usage: ./clawsouls.sh <command> [args...]
# Commands: install, use, restore, list

set -euo pipefail

# Check if clawsouls is installed globally
if command -v clawsouls &>/dev/null; then
  exec clawsouls "$@"
fi

# Check if npx is available
if command -v npx &>/dev/null; then
  exec npx --yes clawsouls "$@"
fi

# Fallback: try node directly
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CLI_PATH="$SCRIPT_DIR/../node_modules/clawsouls/dist/bin/clawsouls.js"

if [ -f "$CLI_PATH" ]; then
  exec node "$CLI_PATH" "$@"
fi

echo "Error: clawsouls CLI not found. Install with: npm install -g clawsouls"
exit 1
