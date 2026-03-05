#!/bin/bash
# Telnyx Skill Setup

set -e

echo "🔧 Telnyx Skill Setup"
echo "===================="
echo ""

# Check if Telnyx CLI is installed
if ! command -v telnyx &> /dev/null; then
  echo "📦 Installing Telnyx CLI..."
  npm install -g @telnyx/api-cli
else
  echo "✓ Telnyx CLI found: $(telnyx --version)"
fi

echo ""
echo "🔐 Configuring API key..."
echo ""
echo "You need a Telnyx API key from: https://portal.telnyx.com/#/app/api-keys"
echo ""

# Check if already configured
if [ -f ~/.config/telnyx/config.json ]; then
  echo "ℹ  API key already configured at ~/.config/telnyx/config.json"
  echo ""
  read -p "Reconfigure? (y/n) " -n 1 -r
  echo ""
  if [[ $REPLY =~ ^[Yy]$ ]]; then
    telnyx auth setup
  fi
else
  echo "Running setup..."
  telnyx auth setup
fi

echo ""
echo "✓ Testing connection..."
if telnyx number list --limit 1 &> /dev/null; then
  echo "✓ Connection successful!"
else
  echo "⚠️  Connection test failed. Check your API key."
  exit 1
fi

echo ""
echo "✨ Setup complete!"
echo ""
echo "Try: telnyx number list"
