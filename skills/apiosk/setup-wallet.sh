#!/bin/bash
# Apiosk Wallet Setup - One-time configuration

set -e

WALLET_DIR="$HOME/.apiosk"
WALLET_FILE="$WALLET_DIR/wallet.json"
CONFIG_FILE="$WALLET_DIR/config.json"

echo "🦞 Apiosk Wallet Setup"
echo ""

# Create directory
mkdir -p "$WALLET_DIR"

# Check if wallet exists
if [ -f "$WALLET_FILE" ] && [ "$1" != "--regenerate" ]; then
  echo "❌ Wallet already exists at $WALLET_FILE"
  echo "Use --regenerate to create a new wallet (WARNING: old wallet will be lost!)"
  exit 1
fi

# Generate wallet using cast (Foundry)
if ! command -v cast &> /dev/null; then
  echo ""
  echo "❌ 'cast' not found. Foundry is required to generate wallets."
  echo ""
  echo "To install Foundry, run:"
  echo "  curl -L https://foundry.paradigm.xyz | bash"
  echo "  foundryup"
  echo ""
  echo "Or visit: https://book.getfoundry.sh/getting-started/installation"
  echo ""
  exit 1
fi

echo "Generating new wallet..."
WALLET_OUTPUT=$(cast wallet new)
ADDRESS=$(echo "$WALLET_OUTPUT" | grep "Address:" | awk '{print $2}')
PRIVATE_KEY=$(echo "$WALLET_OUTPUT" | grep "Private key:" | awk '{print $3}')

# Save wallet
cat > "$WALLET_FILE" << EOF
{
  "address": "$ADDRESS",
  "private_key": "$PRIVATE_KEY",
  "created_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
EOF

chmod 600 "$WALLET_FILE"

# Create config
cat > "$CONFIG_FILE" << EOF
{
  "rpc_url": "https://mainnet.base.org",
  "chain_id": 8453,
  "usdc_contract": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
  "gateway_url": "https://gateway.apiosk.com",
  "daily_limit_usdc": 100.0,
  "per_request_limit_usdc": 1.0
}
EOF

echo ""
echo "✅ Wallet created successfully!"
echo ""
echo "📍 Address: $ADDRESS"
echo "📂 Saved to: $WALLET_FILE"
echo ""
echo "⚠️  IMPORTANT: Fund your wallet with USDC on Base mainnet"
echo ""
echo "How to fund:"
echo "  1. Bridge USDC to Base: https://bridge.base.org"
echo "  2. Or buy on Coinbase → Withdraw to Base"
echo "  3. Send to: $ADDRESS"
echo ""
echo "Minimum recommended: $1-10 USDC"
echo ""
echo "Check balance: ./check-balance.sh"
echo ""
