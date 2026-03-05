#!/usr/bin/env bash
#
# Channel Alchemica for a single Gotchi
# Secure Bankr-based channeling with no private keys
#
# Usage: ./channel.sh <gotchi-id> <parcel-id>
# Example: ./channel.sh 9638 867

set -euo pipefail

if [ $# -lt 2 ]; then
  echo "❌ Usage: channel.sh <gotchi-id> <parcel-id>"
  exit 1
fi

GOTCHI_ID="$1"
PARCEL_ID="$2"

# Contract addresses
REALM_DIAMOND="0x4B0040c3646D3c44B8a28Ad7055cfCF536c05372"
RPC_URL="${BASE_MAINNET_RPC:-https://mainnet.base.org}"
BANKR_CONFIG="$HOME/.openclaw/skills/bankr/config.json"

echo "🔮 Gotchi Channeling"
echo "===================="
echo "👻 Gotchi: #$GOTCHI_ID"
echo "🏰 Parcel: #$PARCEL_ID"
echo ""

# Step 1: Check cooldown
echo "⏰ Checking cooldown..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COOLDOWN_RESULT=$("$SCRIPT_DIR/check-cooldown.sh" "$GOTCHI_ID" 2>/dev/null | tail -1 || echo "ready:0")

if [[ ! "$COOLDOWN_RESULT" =~ ^ready ]]; then
  WAIT_TIME=$(echo "$COOLDOWN_RESULT" | cut -d: -f2)
  HOURS=$((WAIT_TIME / 3600))
  MINS=$(((WAIT_TIME % 3600) / 60))
  
  echo "⏰ Not ready yet!"
  echo "   Wait: ${HOURS}h ${MINS}m"
  echo "   Check back later! 👻"
  exit 1
fi

echo "✅ Cooldown ready!"
echo ""

# Step 2: Build transaction calldata
echo "📦 Building transaction..."

# channelAlchemica(uint256,uint256,uint256,bytes)
# Signature parameter is IGNORED (legacy), pass empty bytes
CALLDATA=$(cast calldata \
  "channelAlchemica(uint256,uint256,uint256,bytes)" \
  "$PARCEL_ID" \
  "$GOTCHI_ID" \
  0 \
  "0x")

echo "   Function: channelAlchemica"
echo "   Parcel: $PARCEL_ID"
echo "   Gotchi: $GOTCHI_ID"
echo "   Calldata: ${CALLDATA:0:66}..."
echo ""

# Step 3: Get Bankr API key
if [ ! -f "$BANKR_CONFIG" ]; then
  echo "❌ Bankr config not found: $BANKR_CONFIG"
  exit 1
fi

API_KEY=$(jq -r '.apiKey' "$BANKR_CONFIG")

if [ -z "$API_KEY" ] || [ "$API_KEY" = "null" ]; then
  # Fallback to env var
  API_KEY="${BANKR_API_KEY:-}"
  if [ -z "$API_KEY" ]; then
    echo "❌ Bankr API key not found"
    exit 1
  fi
fi

# Step 4: Submit via Bankr
echo "🦞 Submitting to Bankr..."
echo ""

RESPONSE=$(curl -s -X POST "https://api.bankr.bot/agent/submit" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"transaction\": {
      \"to\": \"$REALM_DIAMOND\",
      \"chainId\": 8453,
      \"value\": \"0\",
      \"data\": \"$CALLDATA\"
    },
    \"description\": \"Channel Alchemica: Gotchi #$GOTCHI_ID on Parcel #$PARCEL_ID\",
    \"waitForConfirmation\": true
  }")

# Parse response
SUCCESS=$(echo "$RESPONSE" | jq -r '.success // false')

if [ "$SUCCESS" = "true" ]; then
  TX_HASH=$(echo "$RESPONSE" | jq -r '.transactionHash')
  BLOCK=$(echo "$RESPONSE" | jq -r '.blockNumber // "pending"')
  
  echo "============================================"
  echo "✅ CHANNELING SUCCESSFUL!"
  echo "============================================"
  echo ""
  echo "👻 Gotchi #$GOTCHI_ID channeled on Parcel #$PARCEL_ID"
  echo "📦 Block: $BLOCK"
  echo "🔗 Transaction: $TX_HASH"
  echo "🌐 View: https://basescan.org/tx/$TX_HASH"
  echo ""
  
  # Try to get Alchemica amounts from logs
  echo "💰 Fetching rewards..."
  sleep 3
  
  RECEIPT=$(cast receipt "$TX_HASH" --rpc-url "$RPC_URL" --json 2>/dev/null || echo "{}")
  
  # Extract Transfer events (topic[0] = 0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef)
  # Look for mints (from address 0x0000...)
  FUD=$(echo "$RECEIPT" | jq -r '.logs[] | select(.topics[0] == "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef" and .address == "0x2028b4043e6722ea164946c82fe806c4a43a0ff4") | .data' | head -1)
  FOMO=$(echo "$RECEIPT" | jq -r '.logs[] | select(.topics[0] == "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef" and .address == "0xa32137bfb57d2b6a9fd2956ba4b54741a6d54b58") | .data' | head -1)
  ALPHA=$(echo "$RECEIPT" | jq -r '.logs[] | select(.topics[0] == "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef" and .address == "0x15e7cac885e3730ce6389447bc0f7ac032f31947") | .data' | head -1)
  KEK=$(echo "$RECEIPT" | jq -r '.logs[] | select(.topics[0] == "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef" and .address == "0xe52b9170ff4ece4c35e796ffd74b57dec68ca0e5") | .data' | head -1)
  
  if [ -n "$FUD" ] && [ "$FUD" != "null" ]; then
    FUD_DEC=$(cast --to-dec "$FUD" | awk '{printf "%.2f", $1/1e18}')
    FOMO_DEC=$(cast --to-dec "$FOMO" | awk '{printf "%.2f", $1/1e18}')
    ALPHA_DEC=$(cast --to-dec "$ALPHA" | awk '{printf "%.2f", $1/1e18}')
    KEK_DEC=$(cast --to-dec "$KEK" | awk '{printf "%.2f", $1/1e18}')
    
    echo "💎 Alchemica Earned:"
    echo "   🔥 FUD:   $FUD_DEC"
    echo "   😱 FOMO:  $FOMO_DEC"
    echo "   🧠 ALPHA: $ALPHA_DEC"
    echo "   💚 KEK:   $KEK_DEC"
    
    TOTAL=$(echo "$FUD_DEC + $FOMO_DEC + $ALPHA_DEC + $KEK_DEC" | bc)
    echo "   💰 Total: $TOTAL Alchemica"
  else
    echo "💎 Alchemica minted! (Check transaction for amounts)"
  fi
  
  echo ""
  echo "⏰ Next channel: $(date -u -d '+24 hours' '+%Y-%m-%d %H:%M UTC' 2>/dev/null || echo '24 hours from now')"
  echo ""
  echo "LFGOTCHi! 🦞🔮💜"
  
  exit 0
else
  ERROR=$(echo "$RESPONSE" | jq -r '.error // "Unknown error"')
  
  echo "============================================"
  echo "❌ CHANNELING FAILED"
  echo "============================================"
  echo "Error: $ERROR"
  echo ""
  echo "Response:"
  echo "$RESPONSE" | jq '.'
  
  exit 1
fi
