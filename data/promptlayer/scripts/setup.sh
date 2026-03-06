#!/usr/bin/env bash
# Setup helper for PromptLayer skill
set -euo pipefail

echo "🔧 PromptLayer Setup"
echo ""

if [[ -n "${PROMPTLAYER_API_KEY:-}" ]]; then
  echo "✅ PROMPTLAYER_API_KEY is already set"
else
  echo "Get your API key from: https://dashboard.promptlayer.com/settings"
  read -rp "Enter your PromptLayer API key: " key
  
  # Add to OpenClaw env
  ENV_FILE="${HOME}/.openclaw/.env"
  if [[ -f "$ENV_FILE" ]]; then
    if grep -q "PROMPTLAYER_API_KEY" "$ENV_FILE"; then
      sed -i "s/^PROMPTLAYER_API_KEY=.*/PROMPTLAYER_API_KEY=$key/" "$ENV_FILE"
    else
      echo "PROMPTLAYER_API_KEY=$key" >> "$ENV_FILE"
    fi
  else
    mkdir -p "$(dirname "$ENV_FILE")"
    echo "PROMPTLAYER_API_KEY=$key" >> "$ENV_FILE"
  fi
  
  export PROMPTLAYER_API_KEY="$key"
  echo "✅ API key saved to $ENV_FILE"
fi

# Verify connection
echo ""
echo "Verifying connection..."
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
if "$SCRIPT_DIR/pl.sh" templates list >/dev/null 2>&1; then
  echo "✅ Connected to PromptLayer successfully"
else
  echo "❌ Failed to connect. Check your API key."
  exit 1
fi
