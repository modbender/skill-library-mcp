#!/bin/bash
# Check Farcaster custody wallet USDC balance on Base

set -e

FARCASTER_CREDS="/home/phan_harry/.openclaw/farcaster-credentials.json"
USDC_BASE="0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
BASE_RPC="https://mainnet.base.org"

if [ ! -f "$FARCASTER_CREDS" ]; then
  echo "❌ Error: Farcaster credentials not found at $FARCASTER_CREDS"
  exit 1
fi

CUSTODY_ADDRESS=$(jq -r '.custodyAddress' "$FARCASTER_CREDS")

if [ -z "$CUSTODY_ADDRESS" ] || [ "$CUSTODY_ADDRESS" = "null" ]; then
  echo "❌ Error: Custody address not found in credentials"
  exit 1
fi

echo "Farcaster Custody Wallet"
echo "━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Address: $CUSTODY_ADDRESS"
echo ""

# Check ETH balance
echo "Checking balances on Base..."
echo ""

ETH_BALANCE_WEI=$(curl -s -X POST "$BASE_RPC" \
  -H "Content-Type: application/json" \
  -d "{\"jsonrpc\":\"2.0\",\"method\":\"eth_getBalance\",\"params\":[\"$CUSTODY_ADDRESS\",\"latest\"],\"id\":1}" \
  | jq -r '.result')

if [ -n "$ETH_BALANCE_WEI" ] && [ "$ETH_BALANCE_WEI" != "null" ]; then
  # Convert wei to ETH (divide by 10^18)
  ETH_BALANCE=$(python3 -c "print(int('$ETH_BALANCE_WEI', 16) / 10**18)")
  echo "💎 ETH Balance: $ETH_BALANCE ETH"
else
  echo "⚠️  Could not fetch ETH balance"
fi

# Check USDC balance (6 decimals)
USDC_BALANCE_RAW=$(curl -s -X POST "$BASE_RPC" \
  -H "Content-Type: application/json" \
  -d "{\"jsonrpc\":\"2.0\",\"method\":\"eth_call\",\"params\":[{\"to\":\"$USDC_BASE\",\"data\":\"0x70a08231000000000000000000000000${CUSTODY_ADDRESS:2}\"},\"latest\"],\"id\":1}" \
  | jq -r '.result')

if [ -n "$USDC_BALANCE_RAW" ] && [ "$USDC_BALANCE_RAW" != "null" ]; then
  # Convert from 6 decimals
  USDC_BALANCE=$(python3 -c "print(int('$USDC_BALANCE_RAW', 16) / 10**6)")
  CASTS_REMAINING=$(python3 -c "print(int(int('$USDC_BALANCE_RAW', 16) / 1000))")
  
  echo "💵 USDC Balance: $USDC_BALANCE USDC"
  echo "📢 Casts Remaining: ~$CASTS_REMAINING (at 0.001 USDC per cast)"
  
  # Check if balance is low (using python for float comparison)
  LOW_BALANCE=$(python3 -c "print('1' if $USDC_BALANCE < 0.1 else '0')")
  if [ "$LOW_BALANCE" = "1" ]; then
    echo ""
    echo "⚠️  Low balance! Consider funding your wallet."
    echo "   Send USDC to: $CUSTODY_ADDRESS (on Base chain)"
  fi
else
  echo "⚠️  Could not fetch USDC balance"
fi

echo ""
echo "View on BaseScan:"
echo "https://basescan.org/address/$CUSTODY_ADDRESS"
