#!/bin/bash
set -euo pipefail
# Warren Deploy - Quick Setup
# Run: bash setup.sh

cd "$(dirname "$0")"
npm init -y > /dev/null 2>&1
npm install ethers
echo ""
echo "✅ Setup complete! Usage:"
echo "  PRIVATE_KEY=0x... node deploy.js --html '<h1>Hello</h1>' --name 'My Site'"
echo ""
echo "Prerequisites:"
echo "  1. Get MegaETH mainnet ETH via official bridge"
echo "  2. 0xRabbit.agent Key auto-mints (free)"
