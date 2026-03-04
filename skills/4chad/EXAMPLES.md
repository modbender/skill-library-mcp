# Complete Examples

End-to-end workflows for autonomous AI agents using 4chad.

---

## Table of Contents

1. [Setup: Get Your API Key](#1-setup-get-your-api-key)
2. [Launch Your First Token](#2-launch-your-first-token)
3. [Buy Your Token After Launch](#3-buy-your-token-after-launch)
4. [Sell Tokens for SOL](#4-sell-tokens-for-sol)
5. [Claim Creator Fees](#5-claim-creator-fees)
6. [Advanced Token with Custom Economics](#6-advanced-token-with-custom-economics)
7. [Complete Trading Bot](#7-complete-trading-bot)
8. [Multi-Token Portfolio Manager](#8-multi-token-portfolio-manager)
9. [Daily Fee Harvesting Agent](#9-daily-fee-harvesting-agent)
10. [Full Lifecycle: Launch → Trade → Claim](#10-full-lifecycle-launch--trade--claim)

---

## 1. Setup: Get Your API Key

**First time only - register your wallet:**

```bash
#!/bin/bash
# setup.sh - Initialize 4chad agent

# Store your Solana wallet private key
export SOLANA_PRIVATE_KEY="your_base58_private_key"
export WALLET_ADDRESS="your_wallet_public_address"

# Create API key
API_KEY_RESPONSE=$(curl -X POST https://4chad.xyz/api/v1/agent/keys/create \
  -H "Content-Type: application/json" \
  -d "{\"walletAddress\": \"$WALLET_ADDRESS\"}")

# Extract and save key
API_KEY=$(echo $API_KEY_RESPONSE | jq -r '.apiKey')
echo "export 4CHAD_API_KEY=$API_KEY" >> ~/.bashrc
echo "✅ API key created: $API_KEY"

# Save key securely
echo "$API_KEY" > ~/.4chad_api_key
chmod 600 ~/.4chad_api_key

echo "Setup complete! Run: source ~/.bashrc"
```

**Load API key in future sessions:**

```bash
export 4CHAD_API_KEY=$(cat ~/.4chad_api_key)
```

---

## 2. Launch Your First Token

**Easy Mode - 85 SOL target, 1B supply:**

```bash
#!/bin/bash
# launch-token.sh - Create a new meme token

# Token metadata
export TOKEN_NAME="Chad Frog"
export TOKEN_SYMBOL="CHAD"
export TOKEN_DESCRIPTION="The chadliest frog on Solana"
export TOKEN_IMAGE_URL="https://i.imgur.com/example.jpg"
export TOKEN_TWITTER="https://twitter.com/chadfrog"
export TOKEN_TELEGRAM="https://t.me/chadfrog"
export TOKEN_WEBSITE="https://chadfrog.xyz"

# Create token
echo "Creating token: $TOKEN_NAME ($TOKEN_SYMBOL)..."

RESPONSE=$(curl -X POST https://4chad.xyz/api/v1/agent/token/create-transaction \
  -H "X-API-Key: $4CHAD_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"name\": \"$TOKEN_NAME\",
    \"symbol\": \"$TOKEN_SYMBOL\",
    \"description\": \"$TOKEN_DESCRIPTION\",
    \"imageUrl\": \"$TOKEN_IMAGE_URL\",
    \"twitter\": \"$TOKEN_TWITTER\",
    \"telegram\": \"$TOKEN_TELEGRAM\",
    \"website\": \"$TOKEN_WEBSITE\"
  }")

echo "Response: $RESPONSE"

# Extract unsigned transaction
UNSIGNED_TX=$(echo $RESPONSE | jq -r '.unsignedTransaction')

if [ "$UNSIGNED_TX" == "null" ]; then
  echo "❌ Error creating token:"
  echo $RESPONSE | jq -r '.error'
  exit 1
fi

# Sign locally (never send private key to server!)
SIGNED_TX=$(node sign-transaction.js "$UNSIGNED_TX" "$SOLANA_PRIVATE_KEY")

# Submit to blockchain
echo "Submitting transaction..."

SUBMIT_RESPONSE=$(curl -X POST https://4chad.xyz/api/v1/agent/transaction/submit \
  -H "X-API-Key: $4CHAD_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"signedTransaction\": \"$SIGNED_TX\"}")

# Extract token address
TX_SIGNATURE=$(echo $SUBMIT_RESPONSE | jq -r '.signature')
MINT_ADDRESS=$(echo $RESPONSE | jq -r '.mintAddress')

echo "✅ Token created!"
echo "Mint address: $MINT_ADDRESS"
echo "Transaction: https://solscan.io/tx/$TX_SIGNATURE"
echo "Token page: https://4chad.xyz/token/$MINT_ADDRESS"

# Save for later use
echo "export MY_TOKEN_MINT=$MINT_ADDRESS" >> ~/.bashrc
```

---

## 3. Buy Your Token After Launch

**Initial buy to support your token:**

```bash
#!/bin/bash
# buy-token.sh - Buy tokens with SOL

TOKEN_MINT="$MY_TOKEN_MINT"  # From previous example
BUY_AMOUNT_SOL=5  # Buy 5 SOL worth

# Convert SOL to lamports
BUY_AMOUNT_LAMPORTS=$((BUY_AMOUNT_SOL * 1000000000))

echo "Buying $BUY_AMOUNT_SOL SOL worth of tokens..."

# Create swap transaction
RESPONSE=$(curl -X POST https://4chad.xyz/api/v1/agent/trade/create-swap \
  -H "X-API-Key: $4CHAD_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"inputMint\": \"So11111111111111111111111111111111111111112\",
    \"outputMint\": \"$TOKEN_MINT\",
    \"amount\": $BUY_AMOUNT_LAMPORTS,
    \"slippageBps\": 500
  }")

UNSIGNED_TX=$(echo $RESPONSE | jq -r '.unsignedTransaction')
EXPECTED_TOKENS=$(echo $RESPONSE | jq -r '.outAmount')

echo "Expected tokens: $EXPECTED_TOKENS"

# Sign and submit
SIGNED_TX=$(node sign-transaction.js "$UNSIGNED_TX" "$SOLANA_PRIVATE_KEY")

SUBMIT_RESPONSE=$(curl -X POST https://4chad.xyz/api/v1/agent/transaction/submit \
  -H "X-API-Key: $4CHAD_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"signedTransaction\": \"$SIGNED_TX\"}")

TX_SIGNATURE=$(echo $SUBMIT_RESPONSE | jq -r '.signature')

echo "✅ Bought tokens!"
echo "Transaction: https://solscan.io/tx/$TX_SIGNATURE"
```

---

## 4. Sell Tokens for SOL

**Take profits when price goes up:**

```bash
#!/bin/bash
# sell-token.sh - Sell tokens for SOL

TOKEN_MINT="$MY_TOKEN_MINT"

# Get token balance first
echo "Checking token balance..."

BALANCE_RESPONSE=$(curl -s "https://api.mainnet-beta.solana.com" \
  -X POST \
  -H "Content-Type: application/json" \
  -d "{
    \"jsonrpc\": \"2.0\",
    \"id\": 1,
    \"method\": \"getTokenAccountsByOwner\",
    \"params\": [
      \"$WALLET_ADDRESS\",
      {\"mint\": \"$TOKEN_MINT\"},
      {\"encoding\": \"jsonParsed\"}
    ]
  }")

TOKEN_BALANCE=$(echo $BALANCE_RESPONSE | jq -r '.result.value[0].account.data.parsed.info.tokenAmount.amount')

echo "Token balance: $TOKEN_BALANCE"

# Sell 50% of holdings
SELL_AMOUNT=$((TOKEN_BALANCE / 2))

echo "Selling $SELL_AMOUNT tokens..."

# Create sell transaction
RESPONSE=$(curl -X POST https://4chad.xyz/api/v1/agent/trade/create-swap \
  -H "X-API-Key: $4CHAD_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"inputMint\": \"$TOKEN_MINT\",
    \"outputMint\": \"So11111111111111111111111111111111111111112\",
    \"amount\": $SELL_AMOUNT,
    \"slippageBps\": 500
  }")

UNSIGNED_TX=$(echo $RESPONSE | jq -r '.unsignedTransaction')
EXPECTED_SOL=$(echo $RESPONSE | jq -r '.outAmount')
EXPECTED_SOL_FORMATTED=$(echo "scale=4; $EXPECTED_SOL / 1000000000" | bc)

echo "Expected SOL: $EXPECTED_SOL_FORMATTED"

# Sign and submit
SIGNED_TX=$(node sign-transaction.js "$UNSIGNED_TX" "$SOLANA_PRIVATE_KEY")

SUBMIT_RESPONSE=$(curl -X POST https://4chad.xyz/api/v1/agent/transaction/submit \
  -H "X-API-Key: $4CHAD_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"signedTransaction\": \"$SIGNED_TX\"}")

TX_SIGNATURE=$(echo $SUBMIT_RESPONSE | jq -r '.signature')

echo "✅ Sold tokens for $EXPECTED_SOL_FORMATTED SOL!"
echo "Transaction: https://solscan.io/tx/$TX_SIGNATURE"
```

---

## 5. Claim Creator Fees

**Harvest trading fees from your token:**

```bash
#!/bin/bash
# claim-fees.sh - Claim accumulated creator fees

TOKEN_MINT="$MY_TOKEN_MINT"

echo "Checking available fees..."

# Get token data
TOKEN_DATA=$(curl -s "https://4chad.xyz/api/token/$TOKEN_MINT")

TRADING_FEES=$(echo $TOKEN_DATA | jq -r '.tradingFees // 0')
TRADING_SOL=$(echo "scale=4; $TRADING_FEES / 1000000000" | bc)
STATUS=$(echo $TOKEN_DATA | jq -r '.status')

echo "Trading fees available: $TRADING_SOL SOL"
echo "Token status: $STATUS"

# Always claim trading fees
CLAIM_TYPE="trading"
echo "Claiming trading fees..."

# Create claim transaction
RESPONSE=$(curl -X POST https://4chad.xyz/api/v1/agent/fees/claim-transaction \
  -H "X-API-Key: $4CHAD_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"mintAddress\": \"$TOKEN_MINT\",
    \"claimType\": \"$CLAIM_TYPE\"
  }")

if [ "$(echo $RESPONSE | jq -r '.success')" != "true" ]; then
  echo "❌ Cannot claim fees:"
  echo $RESPONSE | jq -r '.error'
  exit 1
fi

UNSIGNED_TX=$(echo $RESPONSE | jq -r '.unsignedTransaction')

# Sign and submit
SIGNED_TX=$(node sign-transaction.js "$UNSIGNED_TX" "$SOLANA_PRIVATE_KEY")

SUBMIT_RESPONSE=$(curl -X POST https://4chad.xyz/api/v1/agent/transaction/submit \
  -H "X-API-Key: $4CHAD_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"signedTransaction\": \"$SIGNED_TX\"}")

TX_SIGNATURE=$(echo $SUBMIT_RESPONSE | jq -r '.signature')

echo "✅ Fees claimed!"
echo "Transaction: https://solscan.io/tx/$TX_SIGNATURE"
```

---

## 6. Advanced Token with Custom Economics

**Create token with custom supply and bonding curve target:**

```bash
#!/bin/bash
# advanced-token.sh - Custom token economics

# Custom parameters
TOTAL_SUPPLY=500000000000  # 500 billion tokens
BONDING_TARGET_SOL=150     # 150 SOL target (harder to complete)

echo "Creating advanced token:"
echo "- Total supply: $TOTAL_SUPPLY (500B tokens)"
echo "- Bonding target: $BONDING_TARGET_SOL SOL"

RESPONSE=$(curl -X POST https://4chad.xyz/api/v1/agent/token/create-transaction \
  -H "X-API-Key: $4CHAD_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"name\": \"Mega Chad\",
    \"symbol\": \"MEGA\",
    \"description\": \"Ultra rare mega supply token\",
    \"imageUrl\": \"https://i.imgur.com/mega.jpg\",
    \"mode\": \"advanced\",
    \"totalSupply\": $TOTAL_SUPPLY,
    \"bondingTargetSol\": $BONDING_TARGET_SOL
  }")

UNSIGNED_TX=$(echo $RESPONSE | jq -r '.unsignedTransaction')
MINT_ADDRESS=$(echo $RESPONSE | jq -r '.mintAddress')

# Sign and submit
SIGNED_TX=$(node sign-transaction.js "$UNSIGNED_TX" "$SOLANA_PRIVATE_KEY")

SUBMIT_RESPONSE=$(curl -X POST https://4chad.xyz/api/v1/agent/transaction/submit \
  -H "X-API-Key: $4CHAD_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"signedTransaction\": \"$SIGNED_TX\"}")

echo "✅ Advanced token created!"
echo "Mint: $MINT_ADDRESS"
echo "Total supply: $TOTAL_SUPPLY"
echo "Bonding target: $BONDING_TARGET_SOL SOL"
echo "Token page: https://4chad.xyz/token/$MINT_ADDRESS"
```

---

## 7. Complete Trading Bot

**Automated buy/sell with stop-loss and take-profit:**

```bash
#!/bin/bash
# trading-bot.sh - Autonomous trading agent

TOKEN_MINT="$1"
ENTRY_AMOUNT_SOL="$2"  # Initial buy amount

# Strategy parameters
STOP_LOSS_PERCENT=20    # -20% stop loss
TAKE_PROFIT_PERCENT=100 # +100% (2x) take profit

echo "🤖 Trading Bot Started"
echo "Token: $TOKEN_MINT"
echo "Entry: $ENTRY_AMOUNT_SOL SOL"
echo "Stop loss: -$STOP_LOSS_PERCENT%"
echo "Take profit: +$TAKE_PROFIT_PERCENT%"

# STEP 1: Initial buy
echo -e "\n📈 Executing entry buy..."

ENTRY_LAMPORTS=$((ENTRY_AMOUNT_SOL * 1000000000))

BUY_RESPONSE=$(curl -s -X POST https://4chad.xyz/api/v1/agent/trade/create-swap \
  -H "X-API-Key: $4CHAD_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"inputMint\": \"So11111111111111111111111111111111111111112\",
    \"outputMint\": \"$TOKEN_MINT\",
    \"amount\": $ENTRY_LAMPORTS,
    \"slippageBps\": 500
  }")

UNSIGNED_TX=$(echo $BUY_RESPONSE | jq -r '.unsignedTransaction')
ENTRY_TOKENS=$(echo $BUY_RESPONSE | jq -r '.outAmount')

SIGNED_TX=$(node sign-transaction.js "$UNSIGNED_TX" "$SOLANA_PRIVATE_KEY")

curl -s -X POST https://4chad.xyz/api/v1/agent/transaction/submit \
  -H "X-API-Key: $4CHAD_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"signedTransaction\": \"$SIGNED_TX\"}" > /dev/null

echo "✅ Bought $ENTRY_TOKENS tokens for $ENTRY_AMOUNT_SOL SOL"

# Calculate thresholds
STOP_LOSS_LAMPORTS=$(echo "$ENTRY_LAMPORTS * (100 - $STOP_LOSS_PERCENT) / 100" | bc)
TAKE_PROFIT_LAMPORTS=$(echo "$ENTRY_LAMPORTS * (100 + $TAKE_PROFIT_PERCENT) / 100" | bc)

echo "Stop loss: $STOP_LOSS_LAMPORTS lamports"
echo "Take profit: $TAKE_PROFIT_LAMPORTS lamports"

# STEP 2: Monitor and execute exit
echo -e "\n👀 Monitoring price..."

while true; do
  # Get current quote
  QUOTE=$(curl -s -X POST https://4chad.xyz/api/v1/agent/trade/quote \
    -H "Content-Type: application/json" \
    -d "{
      \"inputMint\": \"$TOKEN_MINT\",
      \"outputMint\": \"So11111111111111111111111111111111111111112\",
      \"amount\": $ENTRY_TOKENS,
      \"slippageBps\": 500
    }")
  
  CURRENT_VALUE=$(echo $QUOTE | jq -r '.outAmount')
  CURRENT_SOL=$(echo "scale=4; $CURRENT_VALUE / 1000000000" | bc)
  PNL_PERCENT=$(echo "scale=2; (($CURRENT_VALUE - $ENTRY_LAMPORTS) / $ENTRY_LAMPORTS) * 100" | bc)
  
  echo "[$(date +%H:%M:%S)] Value: $CURRENT_SOL SOL | PnL: ${PNL_PERCENT}%"
  
  # Check stop loss
  if (( $(echo "$CURRENT_VALUE <= $STOP_LOSS_LAMPORTS" | bc -l) )); then
    echo "🛑 STOP LOSS triggered at ${PNL_PERCENT}%"
    
    SELL_RESPONSE=$(curl -s -X POST https://4chad.xyz/api/v1/agent/trade/create-swap \
      -H "X-API-Key: $4CHAD_API_KEY" \
      -H "Content-Type: application/json" \
      -d "{
        \"inputMint\": \"$TOKEN_MINT\",
        \"outputMint\": \"So11111111111111111111111111111111111111112\",
        \"amount\": $ENTRY_TOKENS,
        \"slippageBps\": 500
      }")
    
    UNSIGNED_TX=$(echo $SELL_RESPONSE | jq -r '.unsignedTransaction')
    SIGNED_TX=$(node sign-transaction.js "$UNSIGNED_TX" "$SOLANA_PRIVATE_KEY")
    
    curl -s -X POST https://4chad.xyz/api/v1/agent/transaction/submit \
      -H "X-API-Key: $4CHAD_API_KEY" \
      -H "Content-Type: application/json" \
      -d "{\"signedTransaction\": \"$SIGNED_TX\"}" > /dev/null
    
    echo "Sold for $CURRENT_SOL SOL (loss: ${PNL_PERCENT}%)"
    break
  fi
  
  # Check take profit
  if (( $(echo "$CURRENT_VALUE >= $TAKE_PROFIT_LAMPORTS" | bc -l) )); then
    echo "🎯 TAKE PROFIT triggered at ${PNL_PERCENT}%"
    
    SELL_RESPONSE=$(curl -s -X POST https://4chad.xyz/api/v1/agent/trade/create-swap \
      -H "X-API-Key: $4CHAD_API_KEY" \
      -H "Content-Type: application/json" \
      -d "{
        \"inputMint\": \"$TOKEN_MINT\",
        \"outputMint\": \"So11111111111111111111111111111111111111112\",
        \"amount\": $ENTRY_TOKENS,
        \"slippageBps\": 500
      }")
    
    UNSIGNED_TX=$(echo $SELL_RESPONSE | jq -r '.unsignedTransaction')
    SIGNED_TX=$(node sign-transaction.js "$UNSIGNED_TX" "$SOLANA_PRIVATE_KEY")
    
    curl -s -X POST https://4chad.xyz/api/v1/agent/transaction/submit \
      -H "X-API-Key: $4CHAD_API_KEY" \
      -H "Content-Type: application/json" \
      -d "{\"signedTransaction\": \"$SIGNED_TX\"}" > /dev/null
    
    echo "Sold for $CURRENT_SOL SOL (profit: ${PNL_PERCENT}%)"
    break
  fi
  
  sleep 30  # Check every 30 seconds
done

echo "🤖 Trading bot finished"
```

**Usage:**
```bash
./trading-bot.sh YOUR_TOKEN_MINT 5  # Buy 5 SOL, exit at -20% or +100%
```

---

## 8. Multi-Token Portfolio Manager

**Manage multiple tokens with automated rebalancing:**

```bash
#!/bin/bash
# portfolio-manager.sh - Multi-token portfolio

# Portfolio allocation (must sum to 100)
declare -A PORTFOLIO=(
  ["CHAD_TOKEN_1"]=40  # 40% allocation
  ["CHAD_TOKEN_2"]=30  # 30% allocation
  ["CHAD_TOKEN_3"]=30  # 30% allocation
)

TOTAL_PORTFOLIO_SOL=10  # Total portfolio size

echo "🎯 Portfolio Manager"
echo "Total allocation: $TOTAL_PORTFOLIO_SOL SOL"

# Deploy initial capital
for TOKEN_MINT in "${!PORTFOLIO[@]}"; do
  ALLOCATION_PERCENT=${PORTFOLIO[$TOKEN_MINT]}
  ALLOCATION_SOL=$(echo "$TOTAL_PORTFOLIO_SOL * $ALLOCATION_PERCENT / 100" | bc)
  ALLOCATION_LAMPORTS=$(echo "$ALLOCATION_SOL * 1000000000" | bc)
  
  echo -e "\n📊 Token: $TOKEN_MINT"
  echo "Allocation: ${ALLOCATION_PERCENT}% = $ALLOCATION_SOL SOL"
  
  # Buy tokens
  BUY_RESPONSE=$(curl -s -X POST https://4chad.xyz/api/v1/agent/trade/create-swap \
    -H "X-API-Key: $4CHAD_API_KEY" \
    -H "Content-Type: application/json" \
    -d "{
      \"inputMint\": \"So11111111111111111111111111111111111111112\",
      \"outputMint\": \"$TOKEN_MINT\",
      \"amount\": $ALLOCATION_LAMPORTS,
      \"slippageBps\": 500
    }")
  
  UNSIGNED_TX=$(echo $BUY_RESPONSE | jq -r '.unsignedTransaction')
  SIGNED_TX=$(node sign-transaction.js "$UNSIGNED_TX" "$SOLANA_PRIVATE_KEY")
  
  curl -s -X POST https://4chad.xyz/api/v1/agent/transaction/submit \
    -H "X-API-Key: $4CHAD_API_KEY" \
    -H "Content-Type: application/json" \
    -d "{\"signedTransaction\": \"$SIGNED_TX\"}" > /dev/null
  
  echo "✅ Bought $ALLOCATION_SOL SOL worth"
  
  sleep 2
done

echo -e "\n✅ Portfolio deployed!"
```

---

## 9. Daily Fee Harvesting Agent

**Automated daily fee claiming across all tokens:**

```bash
#!/bin/bash
# fee-harvester.sh - Daily fee claiming agent

echo "💰 Fee Harvesting Agent Started"

while true; do
  CURRENT_HOUR=$(date -u +%H)
  
  # Run at 12:00 UTC daily
  if [ "$CURRENT_HOUR" -eq "12" ]; then
    echo -e "\n[$(date)] Daily fee harvest..."
    
    # Get all your tokens
    TOKENS=$(curl -s -X GET "https://4chad.xyz/api/v1/agent/keys/list" \
      -H "X-API-Key: $4CHAD_API_KEY" | jq -r '.tokens[].mintAddress')
    
    TOTAL_CLAIMED_SOL=0
    
    for TOKEN in $TOKENS; do
      echo -e "\n📊 Checking $TOKEN..."
      
      # Get token status
      TOKEN_DATA=$(curl -s "https://4chad.xyz/api/token/$TOKEN")
      STATUS=$(echo $TOKEN_DATA | jq -r '.status')
      TRADING_FEES=$(echo $TOKEN_DATA | jq -r '.tradingFees // 0')
      TRADING_SOL=$(echo "scale=4; $TRADING_FEES / 1000000000" | bc)
      
      echo "Status: $STATUS"
echo "Trading fees (your 0.4% share): $TRADING_SOL SOL"
      # Always claim trading fees
      CLAIM_TYPE="trading"
      
      # Only claim if fees > 0.1 SOL (worth the gas)
      if (( $(echo "$TRADING_SOL >= 0.1" | bc -l) )); then
        echo "Claiming fees..."
        
        RESPONSE=$(curl -s -X POST https://4chad.xyz/api/v1/agent/fees/claim-transaction \
          -H "X-API-Key: $4CHAD_API_KEY" \
          -H "Content-Type: application/json" \
          -d "{\"mintAddress\": \"$TOKEN\", \"claimType\": \"$CLAIM_TYPE\"}")
        
        if [ "$(echo $RESPONSE | jq -r '.success')" == "true" ]; then
          UNSIGNED_TX=$(echo $RESPONSE | jq -r '.unsignedTransaction')
          SIGNED_TX=$(node sign-transaction.js "$UNSIGNED_TX" "$SOLANA_PRIVATE_KEY")
          
          SUBMIT_RESPONSE=$(curl -s -X POST https://4chad.xyz/api/v1/agent/transaction/submit \
            -H "X-API-Key: $4CHAD_API_KEY" \
            -H "Content-Type: application/json" \
            -d "{\"signedTransaction\": \"$SIGNED_TX\"}")
          
          TX=$(echo $SUBMIT_RESPONSE | jq -r '.signature')
          echo "✅ Claimed $TRADING_SOL SOL | TX: $TX"
          
          TOTAL_CLAIMED_SOL=$(echo "$TOTAL_CLAIMED_SOL + $TRADING_SOL" | bc)
        else
          echo "No fees to claim"
        fi
      else
        echo "Fees too small, waiting for more volume..."
      fi
      
      sleep 2
    done
    
    echo -e "\n✅ Daily harvest complete!"
    echo "Total claimed: $TOTAL_CLAIMED_SOL SOL"
    
    # Wait 24 hours
    sleep 86400
  else
    # Check every hour
    sleep 3600
  fi
done
```

---

## 10. Full Lifecycle: Launch → Trade → Claim

**Complete autonomous token lifecycle:**

```bash
#!/bin/bash
# full-lifecycle.sh - Complete token lifecycle example

set -e  # Exit on error

echo "🐸 4chad Full Lifecycle Example"
echo "================================"

# PHASE 1: Launch Token
echo -e "\n📢 PHASE 1: Launching token..."

LAUNCH_RESPONSE=$(curl -s -X POST https://4chad.xyz/api/v1/agent/token/create-transaction \
  -H "X-API-Key: $4CHAD_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Lifecycle Test",
    "symbol": "LIFE",
    "description": "Testing full agent lifecycle",
    "imageUrl": "https://i.imgur.com/test.jpg"
  }')

MINT_ADDRESS=$(echo $LAUNCH_RESPONSE | jq -r '.mintAddress')
UNSIGNED_TX=$(echo $LAUNCH_RESPONSE | jq -r '.unsignedTransaction')

SIGNED_TX=$(node sign-transaction.js "$UNSIGNED_TX" "$SOLANA_PRIVATE_KEY")

SUBMIT_RESPONSE=$(curl -s -X POST https://4chad.xyz/api/v1/agent/transaction/submit \
  -H "X-API-Key: $4CHAD_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"signedTransaction\": \"$SIGNED_TX\"}")

echo "✅ Token launched!"
echo "Mint: $MINT_ADDRESS"
echo "View: https://4chad.xyz/token/$MINT_ADDRESS"

sleep 5

# PHASE 2: Initial Buy
echo -e "\n💰 PHASE 2: Initial buy (3 SOL)..."

BUY_RESPONSE=$(curl -s -X POST https://4chad.xyz/api/v1/agent/trade/create-swap \
  -H "X-API-Key: $4CHAD_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"inputMint\": \"So11111111111111111111111111111111111111112\",
    \"outputMint\": \"$MINT_ADDRESS\",
    \"amount\": 3000000000,
    \"slippageBps\": 500
  }")

UNSIGNED_TX=$(echo $BUY_RESPONSE | jq -r '.unsignedTransaction')
TOKENS_BOUGHT=$(echo $BUY_RESPONSE | jq -r '.outAmount')

SIGNED_TX=$(node sign-transaction.js "$UNSIGNED_TX" "$SOLANA_PRIVATE_KEY")

curl -s -X POST https://4chad.xyz/api/v1/agent/transaction/submit \
  -H "X-API-Key: $4CHAD_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"signedTransaction\": \"$SIGNED_TX\"}" > /dev/null

echo "✅ Bought $TOKENS_BOUGHT tokens with 3 SOL"

sleep 5

# PHASE 3: Wait and Monitor
echo -e "\n⏳ PHASE 3: Monitoring (simulating trading activity)..."
echo "In real scenario, wait for other traders to buy/sell..."
echo "This generates trading fees for you as creator!"

sleep 10

# PHASE 4: Claim Fees
echo -e "\n💸 PHASE 4: Claiming creator fees..."

CLAIM_RESPONSE=$(curl -s -X POST https://4chad.xyz/api/v1/agent/fees/claim-transaction \
  -H "X-API-Key: $4CHAD_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"mintAddress\": \"$MINT_ADDRESS\",
    \"claimType\": \"trading\"
  }")

if [ "$(echo $CLAIM_RESPONSE | jq -r '.success')" == "true" ]; then
  FEES=$(echo $CLAIM_RESPONSE | jq -r '.estimatedFees.trading')
  UNSIGNED_TX=$(echo $CLAIM_RESPONSE | jq -r '.unsignedTransaction')
  
  SIGNED_TX=$(node sign-transaction.js "$UNSIGNED_TX" "$SOLANA_PRIVATE_KEY")
  
  curl -s -X POST https://4chad.xyz/api/v1/agent/transaction/submit \
    -H "X-API-Key: $4CHAD_API_KEY" \
    -H "Content-Type: application/json" \
    -d "{\"signedTransaction\": \"$SIGNED_TX\"}" > /dev/null
  
  echo "✅ Claimed fees: $FEES"
else
  echo "No fees available yet (need more trading volume)"
fi

sleep 5

# PHASE 5: Sell Portion
echo -e "\n📉 PHASE 5: Taking profits (sell 50%)..."

SELL_AMOUNT=$((TOKENS_BOUGHT / 2))

SELL_RESPONSE=$(curl -s -X POST https://4chad.xyz/api/v1/agent/trade/create-swap \
  -H "X-API-Key: $4CHAD_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"inputMint\": \"$MINT_ADDRESS\",
    \"outputMint\": \"So11111111111111111111111111111111111111112\",
    \"amount\": $SELL_AMOUNT,
    \"slippageBps\": 500
  }")

UNSIGNED_TX=$(echo $SELL_RESPONSE | jq -r '.unsignedTransaction')
SOL_RECEIVED=$(echo $SELL_RESPONSE | jq -r '.outAmount')
SOL_FORMATTED=$(echo "scale=4; $SOL_RECEIVED / 1000000000" | bc)

SIGNED_TX=$(node sign-transaction.js "$UNSIGNED_TX" "$SOLANA_PRIVATE_KEY")

curl -s -X POST https://4chad.xyz/api/v1/agent/transaction/submit \
  -H "X-API-Key: $4CHAD_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"signedTransaction\": \"$SIGNED_TX\"}" > /dev/null

echo "✅ Sold 50% for $SOL_FORMATTED SOL"

echo -e "\n🎉 LIFECYCLE COMPLETE!"
echo "================================"
echo "Summary:"
echo "- Launched token: $MINT_ADDRESS"
echo "- Bought with 3 SOL"
echo "- Claimed creator fees"
echo "- Sold 50% for $SOL_FORMATTED SOL"
echo "- Holding remaining 50% for future gains"
echo ""
echo "View token: https://4chad.xyz/token/$MINT_ADDRESS"
```

---

## Tips for Autonomous Agents

### Error Handling
Always check response success before proceeding:
```bash
if [ "$(echo $RESPONSE | jq -r '.success')" != "true" ]; then
  echo "Error: $(echo $RESPONSE | jq -r '.error')"
  exit 1
fi
```

### Rate Limiting
Respect 1000 requests/hour limit:
```bash
# Add delays between requests
sleep 2
```

### Transaction Confirmation
Wait for confirmation before dependent actions:
```bash
# After submitting, wait 5-10 seconds
sleep 5
```

### Logging
Log all operations for debugging:
```bash
echo "[$(date)] Action performed" >> agent.log
```

### Backup Data
Save important addresses:
```bash
echo "TOKEN=$MINT_ADDRESS" >> .env
```

---

## sign-transaction.js Helper

**Required for all examples (local transaction signing):**

```javascript
// sign-transaction.js
const bs58 = require('bs58');
const { Transaction, Keypair, VersionedTransaction } = require('@solana/web3.js');

const unsignedTxBase64 = process.argv[2];
const privateKeyBase58 = process.argv[3];

const privateKey = bs58.decode(privateKeyBase58);
const keypair = Keypair.fromSecretKey(privateKey);

const txBuffer = Buffer.from(unsignedTxBase64, 'base64');
const transaction = VersionedTransaction.deserialize(txBuffer);

transaction.sign([keypair]);

const signedTxBase64 = Buffer.from(transaction.serialize()).toString('base64');
console.log(signedTxBase64);
```

**Install dependencies:**
```bash
npm install @solana/web3.js bs58
```

---

See [SKILL.md](https://4chad.xyz/skill.md) for API reference!

Built for autonomous AI agents on Solana 🐸
