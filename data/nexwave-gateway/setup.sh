#!/usr/bin/env bash
# Nexwave Gateway — One-command setup
# Initializes a Node.js project with Circle Gateway + Circle Programmable Wallets dependencies.
# No raw private keys needed — uses Circle's MPC-secured developer-controlled wallets.

set -e

echo "═══════════════════════════════════════════════"
echo "  Nexwave Gateway — Setup"
echo "═══════════════════════════════════════════════"

# Create project directory
mkdir -p gateway-app && cd gateway-app

# Initialize Node.js project (if needed)
if [ ! -f package.json ]; then
  echo '{ "type": "module" }' > package.json
fi

# Install dependencies
echo "📦 Installing dependencies..."
npm install viem dotenv @circle-fin/developer-controlled-wallets

# Copy skill files into the project
echo "📂 Copying skill files..."
SKILL_DIR="$(cd "$(dirname "$0")" && pwd)"
for f in abis.js gateway-client.js circle-wallet-client.js typed-data.js setup-gateway.js check-balance.js deposit.js transfer.js; do
  cp "$SKILL_DIR/$f" ./ 2>/dev/null || true
done

# Create .env template (if not already configured)
if [ ! -f .env ]; then
  echo "🔧 Creating .env template..."
  cat > .env << 'EOF'
# Circle Programmable Wallets (from circle-wallet skill)
# Get these from https://console.circle.com → Developer Services
CIRCLE_API_KEY=
CIRCLE_ENTITY_SECRET=
CIRCLE_WALLET_SET_ID=
EOF
  echo "   ⚠️  Fill in .env with your Circle Developer Console credentials"
  echo "   💡 If you have the circle-wallet skill installed, these should"
  echo "      already be in your agent's environment."
else
  echo "   .env already exists — keeping your existing configuration"
fi

echo ""
echo "═══════════════════════════════════════════════"
echo "✅ Setup complete!"
echo ""
echo "Prerequisites:"
echo "  1. Install the circle-wallet skill: clawhub install eltontay/circle-wallet"
echo "  2. Set up a Circle Developer Account: https://console.circle.com"
echo "  3. Create a wallet set with wallets on ETH-SEPOLIA, BASE-SEPOLIA, ARC-TESTNET"
echo "  4. Get testnet USDC from https://faucet.circle.com"
echo ""
echo "Usage:"
echo "  node check-balance.js   # Check unified USDC balance"
echo "  node deposit.js         # Deposit USDC into Gateway"
echo "  node transfer.js        # Transfer USDC crosschain"
echo "═══════════════════════════════════════════════"
