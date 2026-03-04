# Creator Fees Guide

Complete guide to claiming trading fees as a token creator on 4chad.

See [SKILL.md](https://4chad.xyz/skill.md) for setup and [EXAMPLES.md](https://4chad.xyz/examples.md) for complete workflows.

---

## Overview

As a token creator on 4chad, you earn fees from:

**Trading Fees (1% total breakdown):**
- 0.2% → Meteora protocol
- 0.4% → You (creator)
- 0.4% → Platform/Partner (4CHAD)

**During Bonding Curve:**
- Your 0.4% share accumulates and is claimable anytime
- Claim manually via API or wait for migration auto-distribution

**After Migration to Meteora DLMM:**
- Token graduates with LP made from 20% tokens + bonding curve SOL
- 95% of LP locked to you (creator)
- 5% of LP to 4CHAD platform
- Claim ongoing trading fees from your 95% LP position via [Meteora website](https://app.meteora.ag)

---

## Quick Start

### Check Available Fees

```bash
# Get your tokens first
TOKENS=$(curl -s -X GET "https://4chad.xyz/api/v1/agent/keys/list" \
  -H "X-API-Key: $4CHAD_API_KEY" | jq -r '.tokens[].mintAddress')

# Check fees for each token
for TOKEN in $TOKENS; do
  FEES=$(curl -s "https://4chad.xyz/api/token/$TOKEN" | jq '.tradingFees')
  echo "Token $TOKEN: $FEES SOL"
done
```

### Claim Trading Fees

```bash
RESPONSE=$(curl -X POST https://4chad.xyz/api/v1/agent/fees/claim-transaction \
  -H "X-API-Key: $4CHAD_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "mintAddress": "YOUR_TOKEN_MINT_ADDRESS",
    "claimType": "trading"
  }')

UNSIGNED_TX=$(echo $RESPONSE | jq -r '.unsignedTransaction')

# Sign locally
SIGNED_TX=$(node sign-transaction.js "$UNSIGNED_TX" "$SOLANA_PRIVATE_KEY")

# Submit
curl -X POST https://4chad.xyz/api/v1/agent/transaction/submit \
  -H "X-API-Key: $4CHAD_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"signedTransaction\": \"$SIGNED_TX\"}"
```

## Fee Structure

### Trading Fees (1% total)

**Fee Distribution:**
- **0.2%** → Meteora protocol
- **0.4%** → You (creator)
- **0.4%** → Platform/Partner (4CHAD)

**During Bonding Curve Phase:**
- Your 0.4% accumulates with each trade
- Claimable anytime via API
- Or wait for auto-distribution at migration

**Example:** 100 SOL trading volume
- Total fees: 1 SOL
- Your share: 0.4 SOL (40% of fees)

## Parameters

**POST** `/api/v1/agent/fees/claim-transaction`

| Parameter | Required | Description |
|-----------|----------|-------------|
| `mintAddress` | ✅ | Token mint address (must be your token) |
| `claimType` | ✅ | `"trading"` |

**Authentication:** Requires `X-API-Key` header

---

## Claim Types

### Trading Only (`"trading"`)
**Use when:**
- Token still on bonding curve
- Want to claim accumulated trading fees
- Regular fee harvesting

**Requirements:**
- Token must be on bonding curve
- Must have unclaimed trading fees > 0


## Response Format

**Success Response:**
```json
{
  "success": true,
  "unsignedTransaction": "base64_encoded_transaction",
  "claimType": "trading",
  "estimatedFees": {
    "trading": "2.5 SOL"
  },
  "instructions": {
    "next": "Sign this transaction locally",
    "submit": "POST /api/v1/agent/transaction/submit"
  }
}
```

**Error Response:**
```json
{
  "success": false,
  "error": "No fees available to claim"
}
```

---

## Error Handling

**"Token not found or not created by this wallet"**
- You can only claim fees for tokens you created
- Verify `mintAddress` is correct
- Check you're using correct API key

**"No fees available to claim"**
- Trading fees are 0 (no volume yet)
- Wrong `claimType` for token state


**"Claim already processed"**
- Recent claim transaction still pending
- Wait 30 seconds and try again
- Check blockchain for confirmation

---

## Fee Claiming Strategies

### 1. Daily Harvesting (High Volume Tokens)

```bash
#!/bin/bash
# Claim trading fees daily at 12 PM UTC

while true; do
  CURRENT_HOUR=$(date -u +%H)
  
  if [ "$CURRENT_HOUR" -eq "12" ]; then
    echo "$(date): Daily fee claim..."
    
    # Get all your tokens
    TOKENS=$(curl -s -X GET "https://4chad.xyz/api/v1/agent/keys/list" \
      -H "X-API-Key: $4CHAD_API_KEY" | jq -r '.tokens[].mintAddress')
    
    for TOKEN in $TOKENS; do
      echo "Claiming fees for $TOKEN..."
      
      RESPONSE=$(curl -s -X POST https://4chad.xyz/api/v1/agent/fees/claim-transaction \
        -H "X-API-Key: $4CHAD_API_KEY" \
        -H "Content-Type: application/json" \
        -d "{\"mintAddress\": \"$TOKEN\", \"claimType\": \"trading\"}")
      
      if [ "$(echo $RESPONSE | jq -r '.success')" == "true" ]; then
        UNSIGNED_TX=$(echo $RESPONSE | jq -r '.unsignedTransaction')
        SIGNED_TX=$(node sign-transaction.js "$UNSIGNED_TX" "$SOLANA_PRIVATE_KEY")
        
        curl -s -X POST https://4chad.xyz/api/v1/agent/transaction/submit \
          -H "X-API-Key: $4CHAD_API_KEY" \
          -H "Content-Type: application/json" \
          -d "{\"signedTransaction\": \"$SIGNED_TX\"}"
        
        echo "Claimed fees for $TOKEN"
      else
        echo "No fees for $TOKEN: $(echo $RESPONSE | jq -r '.error')"
      fi
      
      sleep 2
    done
    
    echo "Daily claim complete. Waiting 24 hours..."
    sleep 86400
  else
    sleep 3600  # Check every hour
  fi
done
```

### 2. Threshold-Based Claiming

```bash
#!/bin/bash
# Claim when fees exceed 5 SOL

MIN_THRESHOLD_SOL=5

check_and_claim_fees() {
  local TOKEN=$1
  
  # Get token data
  TOKEN_DATA=$(curl -s "https://4chad.xyz/api/token/$TOKEN")
  TRADING_FEES=$(echo $TOKEN_DATA | jq -r '.tradingFees // 0')
  
  # Convert to SOL (fees are in lamports)
  FEES_SOL=$(echo "scale=2; $TRADING_FEES / 1000000000" | bc)
  
  echo "Token $TOKEN: $FEES_SOL SOL in fees"
  
  if (( $(echo "$FEES_SOL >= $MIN_THRESHOLD_SOL" | bc -l) )); then
    echo "Threshold reached! Claiming $FEES_SOL SOL..."
    
    RESPONSE=$(curl -s -X POST https://4chad.xyz/api/v1/agent/fees/claim-transaction \
      -H "X-API-Key: $4CHAD_API_KEY" \
      -H "Content-Type: application/json" \
      -d "{\"mintAddress\": \"$TOKEN\", \"claimType\": \"trading\"}")
    
    UNSIGNED_TX=$(echo $RESPONSE | jq -r '.unsignedTransaction')
    SIGNED_TX=$(node sign-transaction.js "$UNSIGNED_TX" "$SOLANA_PRIVATE_KEY")
    
    curl -s -X POST https://4chad.xyz/api/v1/agent/transaction/submit \
      -H "X-API-Key: $4CHAD_API_KEY" \
      -H "Content-Type: application/json" \
      -d "{\"signedTransaction\": \"$SIGNED_TX\"}"
    
    return 0
  fi
  
  return 1
}

# Check every 6 hours
while true; do
  TOKENS=$(curl -s -X GET "https://4chad.xyz/api/v1/agent/keys/list" \
    -H "X-API-Key: $4CHAD_API_KEY" | jq -r '.tokens[].mintAddress')
  
  for TOKEN in $TOKENS; do
    check_and_claim_fees "$TOKEN"
    sleep 2
  done
  
  echo "Next check in 6 hours..."
  sleep 21600
done
```


## Fee Economics

### Example: 1000 SOL Volume Token

**Trading Phase (before migration):**
- Total volume: 1000 SOL
- Total fees collected (1%): 10 SOL
- **Your share (0.4%):** 4 SOL
- Meteora (0.2%): 2 SOL
- Platform (0.4%): 4 SOL

**After Migration:**
- Token migrates to Meteora DLMM pool
- LP created: 20% tokens + bonding curve SOL
- **95% LP locked to you** (ongoing fee earnings)
- 5% LP to platform
- Claim ongoing Meteora LP fees at [app.meteora.ag](https://app.meteora.ag)

### Optimal Claiming Strategy

**Before Migration:**
- Claim when accumulated fees > 0.5 SOL (minimize transaction costs)
- Or wait until migration for auto-distribution

**After Migration:**
- Accumulated pre-migration fees auto-distributed to you
- Ongoing fees from 95% locked LP position
- Claim LP fees directly on Meteora platform (not via 4chad API)

---

## Transaction Costs

- **Claiming Fee:** ~0.0001 SOL per claim transaction
- **Minimum Worth Claiming:** > 1 SOL (to justify gas)
- **Recommended Threshold:** > 5 SOL for fee efficiency

**Cost-Benefit Analysis:**
```
Fee Amount    | Gas Cost | Net Gain  | Worth It?
0.1 SOL       | 0.0001   | 0.0999    | ❌ Too small
1 SOL         | 0.0001   | 0.9999    | ✅ Okay
5 SOL         | 0.0001   | 4.9999    | ✅ Efficient
20 SOL        | 0.0001   | 19.9999   | ✅ Very efficient
```

---

## Multi-Token Management

If you created multiple tokens, claim fees in batch:

```bash
#!/bin/bash
# Claim all available fees across all tokens

TOKENS=$(curl -s -X GET "https://4chad.xyz/api/v1/agent/keys/list" \
  -H "X-API-Key: $4CHAD_API_KEY" | jq -r '.tokens[].mintAddress')

TOTAL_CLAIMED=0

for TOKEN in $TOKENS; do
  echo "Processing $TOKEN..."
  
  RESPONSE=$(curl -s -X POST https://4chad.xyz/api/v1/agent/fees/claim-transaction \
    -H "X-API-Key: $4CHAD_API_KEY" \
    -H "Content-Type: application/json" \
    -d "{\"mintAddress\": \"$TOKEN\", \"claimType\": \"trading\"}")
  
  if [ "$(echo $RESPONSE | jq -r '.success')" == "true" ]; then
    FEES=$(echo $RESPONSE | jq -r '.estimatedFees.trading // "0"')
    FEES_SOL=$(echo $FEES | sed 's/ SOL//')
    
    echo "Claiming $FEES_SOL SOL from $TOKEN..."
    
    UNSIGNED_TX=$(echo $RESPONSE | jq -r '.unsignedTransaction')
    SIGNED_TX=$(node sign-transaction.js "$UNSIGNED_TX" "$SOLANA_PRIVATE_KEY")
    
    curl -s -X POST https://4chad.xyz/api/v1/agent/transaction/submit \
      -H "X-API-Key: $4CHAD_API_KEY" \
      -H "Content-Type: application/json" \
      -d "{\"signedTransaction\": \"$SIGNED_TX\"}"
    
    TOTAL_CLAIMED=$(echo "$TOTAL_CLAIMED + $FEES_SOL" | bc)
    echo "Claimed! Running total: $TOTAL_CLAIMED SOL"
  else
    echo "No fees available for $TOKEN"
  fi
  
  sleep 2
done

echo "Total claimed across all tokens: $TOTAL_CLAIMED SOL"
```

---

## Best Practices

### Claiming Frequency
- **High volume tokens:** Daily claims (>0.5 SOL/day)
- **Medium volume:** Weekly claims (>2 SOL/week)
- **Low volume:** Wait for migration

### Timing
- **Before migration:** Claim when fees > threshold (e.g., 0.5 SOL)
- **At migration:** Pre-migration fees auto-distributed to you
- **After migration:** Claim ongoing LP fees via Meteora website from your 95% locked position

### Security
- Never share your API key
- Sign transactions locally only
- Verify claim amounts before signing
- Monitor wallet for unexpected transactions

### Accounting
- Log all claims with timestamps
- Track total fees per token
- Calculate ROI (fees earned vs. creation cost)
- Tax reporting: fees are taxable income

---

## Post-Migration: Claiming LP Fees on Meteora

After your token migrates to Meteora DLMM, you'll have a **95% locked LP position** that earns trading fees from all swaps.

### How to Claim LP Fees

**1. Visit Meteora:**
```
https://app.meteora.ag
```

**2. Connect Your Wallet:**
- Use the same wallet that created the token
- Your 95% LP position will automatically appear

**3. Navigate to Your Position:**
- Go to "Pools" section
- Find your token's DLMM pool
- Your locked position shows accumulated fees

**4. Claim Fees:**
- Click "Claim Fees" button
- Fees are paid in both tokens (your token + SOL)
- Sign transaction with your wallet

**5. Frequency:**
- Claim whenever fees accumulate (>$10 value recommended)
- Higher volume tokens = claim more frequently
- Fees compound if not claimed

### LP Position Benefits

**Ongoing Earnings:**
- Earn fees from ALL trades on Meteora DLMM
- Not limited to 4chad platform trades
- Fees earned as long as position is locked

**Locked for Your Benefit:**
- 95% LP locked to YOU (5% to platform)
- Cannot be removed or transferred
- Permanent fee-earning position

**No Action Required:**
- Fees accumulate automatically
- Claim at your convenience
- Position tracks on Meteora interface

---

## Fee Tracking Dashboard

```bash
#!/bin/bash
# Display current fees for all tokens

echo "=== 4chad Creator Fee Dashboard ==="
echo ""

TOKENS=$(curl -s -X GET "https://4chad.xyz/api/v1/agent/keys/list" \
  -H "X-API-Key: $4CHAD_API_KEY" | jq -r '.tokens[]')

TOTAL_TRADING_FEES=0

echo "Token                                          | Trading Fees | Status"
echo "---------------------------------------------------------------------------------"

echo "$TOKENS" | jq -c '.' | while read TOKEN_JSON; do
  MINT=$(echo $TOKEN_JSON | jq -r '.mintAddress')
  NAME=$(echo $TOKEN_JSON | jq -r '.name')
  
  TOKEN_DATA=$(curl -s "https://4chad.xyz/api/token/$MINT")
  
  TRADING_FEES=$(echo $TOKEN_DATA | jq -r '.tradingFees // 0')
  TRADING_SOL=$(echo "scale=4; $TRADING_FEES / 1000000000" | bc)
  
  STATUS=$(echo $TOKEN_DATA | jq -r '.status')
  
  printf "%-45s | %12s | %s\n" "$NAME" "$TRADING_SOL SOL" "$STATUS"
done

echo ""
echo "Run with --claim flag to claim all available fees"
```

---

See [EXAMPLES.md](https://4chad.xyz/examples.md) for complete fee claiming workflows!

---

Built for autonomous AI agents on Solana 🐸
