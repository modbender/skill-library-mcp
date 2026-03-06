#!/bin/bash
set -e
echo "🚀 NFT Mint Bot Setup"
cd "$(dirname "$0")"

if [ ! -f package.json ]; then
  npm init -y
  # Set type to module for ESM imports
  node -e "const p=require('./package.json'); p.type='module'; require('fs').writeFileSync('package.json', JSON.stringify(p,null,2))"
fi

npm install ethers@^6

if [ ! -f config.json ]; then
  cp ../assets/config-template.json config.json
  echo "📄 Created config.json from template — edit it with your settings"
else
  echo "⚠️  config.json already exists, skipping"
fi

echo "✅ Setup complete. Edit config.json then run: node mint-bot.js"
