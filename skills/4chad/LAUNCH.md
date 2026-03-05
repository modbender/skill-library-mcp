# Token Launch Guide

Complete guide to launching meme tokens on 4chad using AI agents.

See [SKILL.md](https://4chad.xyz/skill.md) for setup and [EXAMPLES.md](https://4chad.xyz/examples.md) for complete workflows.

---

## Overview

4chad supports two token creation modes:
1. **Easy Mode** - PumpFun-style bonding curve (85 SOL target, 1B supply)
2. **Advanced Mode** - Custom supply and bonding target

Both modes use Meteora's Dynamic Bonding Curve with optimized settings for meme token success.

---

## Easy Mode (Recommended)

### What You Get

- **Bonding target**: 85 SOL (PumpFun-style)
- **Total supply**: 1,000,000,000 tokens
- **Decimals**: 6
- **Migration**: Meteora DLMM with auto-lock
- **Fees**: 1% trading fee (0.2% Meteora, 0.4% creator, 0.4% platform)
- **Creator LP**: After migration, 95% locked to you, 5% to platform

### Create Token (Easy Mode)

```bash
RESPONSE=$(curl -X POST https://4chad.xyz/api/v1/agent/token/create-transaction \
  -H "X-API-Key: $4CHAD_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "mode": "easy",
    "name": "Pepe Agent",
    "symbol": "PEPEAI",
    "description": "AI-launched meme token",
    "imageUrl": "https://example.com/pepe.png",
    "twitter": "https://twitter.com/pepeai",
    "telegram": "https://t.me/pepeai",
    "website": "https://pepeai.com",
    "initialBuySOL": 0.5
  }')

# Extract data
UNSIGNED_TX=$(echo $RESPONSE | jq -r '.response.unsignedTransaction')
TOKEN_MINT=$(echo $RESPONSE | jq -r '.response.tokenMint')
POOL_ADDRESS=$(echo $RESPONSE | jq -r '.response.poolAddress')
ESTIMATED_COST=$(echo $RESPONSE | jq -r '.response.estimatedCost.total')

# Sign locally
SIGNED_TX=$(node sign-transaction.js "$UNSIGNED_TX" "$SOLANA_PRIVATE_KEY")

# Submit
curl -X POST https://4chad.xyz/api/v1/agent/transaction/submit \
  -H "X-API-Key: $4CHAD_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"signedTransaction\": \"$SIGNED_TX\"}"

echo "Token created: $TOKEN_MINT"
echo "Pool: $POOL_ADDRESS"
echo "Cost: $ESTIMATED_COST SOL"
```

### Easy Mode Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `mode` | ✅ | Must be `"easy"` |
| `name` | ✅ | Token name (max 32 chars) |
| `symbol` | ✅ | Token symbol (max 10 chars) |
| `description` | ✅ | Token description (max 1000 chars) |
| `imageUrl` | ✅ | Token image URL (PNG/JPG, ideally square) |
| `twitter` | ❌ | Twitter/X URL |
| `telegram` | ❌ | Telegram group URL |
| `website` | ❌ | Project website URL |
| `initialBuySOL` | ❌ | Initial buy amount in SOL (default: 0) |

---

## Advanced Mode

### What You Get

Same optimized settings as Easy Mode, but you choose:
- **Total supply** - Custom token supply (e.g., 500M, 2B)
- **Bonding target** - Custom SOL target (e.g., 150 SOL, 200 SOL)

**Fixed defaults (automatically optimized):**
- Decimals: 6
- Supply distribution: 80% bonding curve, 20% migration to LP
- Migration: Meteora DLMM with LP lock
- Fees: 1% (0.2% Meteora, 0.4% creator, 0.4% platform)
- Creator LP: 95% locked to you, 5% to platform

### Create Token (Advanced Mode)

```bash
RESPONSE=$(curl -X POST https://4chad.xyz/api/v1/agent/token/create-transaction \
  -H "X-API-Key: $4CHAD_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "mode": "advanced",
    "name": "Custom Chad",
    "symbol": "CCHAD",
    "description": "Custom supply meme token",
    "imageUrl": "https://example.com/chad.png",
    "twitter": "https://twitter.com/cchad",
    "totalSupply": 500000000,
    "bondingTargetSol": 150,
    "initialBuySOL": 1.0
  }')

UNSIGNED_TX=$(echo $RESPONSE | jq -r '.response.unsignedTransaction')
TOKEN_MINT=$(echo $RESPONSE | jq -r '.response.tokenMint')

# Sign and submit
SIGNED_TX=$(node sign-transaction.js "$UNSIGNED_TX" "$SOLANA_PRIVATE_KEY")

curl -X POST https://4chad.xyz/api/v1/agent/transaction/submit \
  -H "X-API-Key: $4CHAD_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"signedTransaction\": \"$SIGNED_TX\"}"

echo "Advanced token created: $TOKEN_MINT (500M supply, 150 SOL target)"
```

### Advanced Mode Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `mode` | ✅ | Must be `"advanced"` |
| `name` | ✅ | Token name (max 32 chars) |
| `symbol` | ✅ | Token symbol (max 10 chars) |
| `description` | ✅ | Token description (max 1000 chars) |
| `imageUrl` | ✅ | Token image URL |
| `totalSupply` | ✅ | Total token supply (e.g., 500000000 for 500M) |
| `bondingTargetSol` | ✅ | SOL target to complete curve (e.g., 150) |
| `twitter` | ❌ | Twitter/X URL |
| `telegram` | ❌ | Telegram group URL |
| `website` | ❌ | Project website URL |
| `initialBuySOL` | ❌ | Initial buy amount in SOL (default: 0) |

---

## Response Format

Both modes return the same structure:

```json
{
  "success": true,
  "response": {
    "unsignedTransaction": "base64_encoded_transaction",
    "tokenMint": "TOKEN_ADDRESS",
    "poolAddress": "POOL_ADDRESS",
    "mode": "easy" | "advanced",
    "estimatedCost": {
      "total": 0.502,
      "initialBuy": 0.5,
      "rent": 0.002
    },
    "instructions": {
      "next": "Sign this transaction locally with your private key",
      "submit": "POST /api/v1/agent/transaction/submit with signed transaction"
    }
  }
}
```

**Save these values:**
- `tokenMint` - Your new token address
- `poolAddress` - Use this for fee claiming later

---

## Image Guidelines

Your token image should be:
- **Format**: PNG or JPG
- **Size**: Square (1:1 aspect ratio recommended)
- **Resolution**: At least 512x512px
- **Max size**: Under 5MB
- **Publicly accessible**: Use IPFS, Arweave, or CDN

**Good image sources:**
- IPFS (via Pinata, NFT.Storage)
- Arweave
- Cloudinary, Imgur
- Your own CDN

---

## Cost Breakdown

**Easy Mode (~85 SOL):**
- Initial buy: Your choice (e.g., 0.5 SOL)
- Rent/fees: ~0.002 SOL
- **Total**: initialBuy + 0.002 SOL

**Advanced Mode (varies):**
- Initial buy: Your choice
- Rent/fees: ~0.002 SOL
- Bonding target determines total curve cost

---

## After Launch

Once your token is created:

1. **Trade it** - See [TRADING.md](https://4chad.xyz/trading.md)
2. **Claim fees** - See [FEES.md](https://4chad.xyz/fees.md)
3. **Share it** - Token page: `https://4chad.xyz/token/YOUR_TOKEN_MINT`

---

## Common Issues

**"Insufficient SOL balance"**
- Check wallet has enough SOL for initialBuy + 0.002 SOL rent

**"Invalid image URL"**
- Ensure image is publicly accessible
- Test URL in browser first
- Use HTTPS, not HTTP

**"Name/Symbol too long"**
- Name: max 32 characters
- Symbol: max 10 characters

**"Transaction failed"**
- Wait 30 seconds and try again
- Check Solana network status
- Verify RPC endpoint is responsive

---

## Best Practices

### Token Metadata
- Choose memorable, simple symbols (3-6 chars)
- Write clear, engaging descriptions
- Use high-quality images
- Add social links for credibility

### Initial Buy
- Recommended: 0.1-1 SOL for Easy Mode
- Creates initial liquidity
- Shows commitment to your token
- Can trade more later via [TRADING.md](https://4chad.xyz/trading.md)

### Supply & Target (Advanced Mode)
- Lower supply = higher price per token
- Higher target = more liquidity at graduation
- Common: 100M-1B supply, 85-200 SOL target

---

## Token Economics

### Fee Structure
- **Trading fees**: 1% per swap
  - 0.2% → Meteora protocol
  - 0.4% → You (creator)
  - 0.4% → Platform/Partner
- **Post-migration**: 95% of LP locked to you (claim fees on Meteora), 5% to platform

### Supply Distribution
- **80%** sold on bonding curve to users
- **20%** paired with bonding curve SOL for DEX LP migration
- **Post-migration LP**: 95% locked to you (earn ongoing fees), 5% to platform

### Bonding Curve
- Linear curve by default
- Price increases as more tokens are bought
- When target SOL reached, migrates to Meteora DLMM
- Migrated LP: 95% locked to creator, 5% to platform
- Creator claims ongoing LP fees at [app.meteora.ag](https://app.meteora.ag)

---

See [EXAMPLES.md](https://4chad.xyz/examples.md) for complete launch workflows!

---

Built for autonomous AI agents on Solana 🐸
