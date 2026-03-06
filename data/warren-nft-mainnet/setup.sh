#!/bin/bash
set -euo pipefail
# Warren NFT Deploy - Quick Setup
cd "$(dirname "$0")"
npm init -y > /dev/null 2>&1
npm install ethers
echo ""
echo "✅ Setup complete!"
echo ""
echo "Deploy NFT collection:"
echo "  PRIVATE_KEY=0x... node deploy-nft.js --generate-svg 10 --name 'My NFT' --symbol 'MNFT'"
echo ""
echo "Prerequisites:"
echo "  1. Get MegaETH mainnet ETH via official bridge"
echo "  2. 0xRabbit.agent Key auto-mints (free)"
