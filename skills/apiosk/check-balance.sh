#!/bin/bash
# Check USDC balance in your Apiosk wallet

WALLET_FILE="$HOME/.apiosk/wallet.json"
CONFIG_FILE="$HOME/.apiosk/config.json"

if [ ! -f "$WALLET_FILE" ]; then
  echo "❌ Wallet not found. Run ./setup-wallet.sh first"
  exit 1
fi

WALLET_ADDRESS=$(jq -r '.address' "$WALLET_FILE")
RPC_URL=$(jq -r '.rpc_url' "$CONFIG_FILE")
USDC_CONTRACT=$(jq -r '.usdc_contract' "$CONFIG_FILE")
GATEWAY_URL=$(jq -r '.gateway_url' "$CONFIG_FILE")

echo "🦞 Apiosk Wallet Balance"
echo ""
echo "Address: $WALLET_ADDRESS"
echo ""

# Check USDC balance on-chain
if command -v cast &> /dev/null; then
  BALANCE_WEI=$(cast call "$USDC_CONTRACT" "balanceOf(address)(uint256)" "$WALLET_ADDRESS" --rpc-url "$RPC_URL")
  BALANCE_USDC=$(echo "scale=2; $BALANCE_WEI / 1000000" | bc)
  echo "💰 USDC Balance: $BALANCE_USDC USDC"
else
  echo "⚠️  Install Foundry to check on-chain balance: curl -L https://foundry.paradigm.xyz | bash"
fi

# Check usage via Apiosk gateway
USAGE=$(curl -s "$GATEWAY_URL/v1/balance?address=$WALLET_ADDRESS")

if [ $? -eq 0 ]; then
  echo ""
  echo "📊 Apiosk Usage:"
  echo "$USAGE" | jq
else
  echo ""
  echo "⚠️  Could not fetch usage stats from gateway"
fi

echo ""
echo "Top up at: https://bridge.base.org"
echo ""
