---
name: p0-for-agents
description: Deploy tokens on Solana, trade on pump.fun & Jupiter, earn creator fees
metadata: {"openclaw":{"emoji":"🚀","requires":{"env":["P0_API_KEY"]}}}
homepage: https://agents.p0.systems
---

# P0 for Agents — ClawHub Skill

Deploy tokens on Solana. Trade on pump.fun & Jupiter. Earn creator fees. Pay your own rent.

## Setup

Set `P0_API_KEY` in your environment. Get one by registering:

```bash
curl -X POST https://api.p0.systems/api/x402/register \
  -H "Content-Type: application/json" \
  -d '{"walletAddress": "YOUR_SOLANA_WALLET", "signature": "BASE58_ED25519_SIGNATURE", "message": "THE_MESSAGE_YOU_SIGNED"}'
```

Or register with email:
```bash
curl -X POST https://api.p0.systems/api/x402/register \
  -H "Content-Type: application/json" \
  -d '{"email": "agent@example.com"}'
```

Returns `{ apiKey: "p0_live_...", credits: 1000 }`.

## Base URL

`https://api.p0.systems/api/x402`

All authenticated endpoints use `x-api-key: $P0_API_KEY` header. Rate limit: 60 req/min.

## Token Deployment

### Create project
```
POST /projects
Content-Type: application/json
x-api-key: $P0_API_KEY

{"tokenName": "AgentCoin", "tokenTicker": "AGENT", "textDescription": "An AI agent token", "templateId": "cyber-punk"}
→ { project: { id, domain } }
```

### Deploy token
```
POST /projects/{id}/deploy
x-api-key: $P0_API_KEY

{"platform": "pump_fun", "initialBuySol": 0.01}
→ { deployment: { tokenAddress, signature } }
```

Platform options: `pump_fun`, `bags`. Free campaign deploy is pump.fun only (gas only, no initial buy covered).

### Batch deploy (Pro only)
```
POST /batch
x-api-key: $P0_API_KEY

{"tokens": [{"tokenName": "...", "tokenTicker": "...", "textDescription": "...", "platform": "pump_fun"}]}
→ { batchId }

GET /batch/{batchId} → poll status
GET /batches → list all batches
```

## Fee Claiming

```
GET /projects/{id}/earnings → { pending, claimed, currency: "SOL" }
POST /projects/{id}/claim-fees → { claimed, currency, signatures }
GET /earnings → total earnings across all tokens
POST /claim-all-fees → claim from all tokens at once
```

## Terminal Trading

### Token data
```
GET /tokens/recent → recently deployed tokens
GET /tokens/trending → trending tokens by volume
GET /tokens/almost-bonded → tokens near bonding curve graduation
GET /tokens/{address} → token details, price, metadata
```

### Swap / Trade
```
GET /swap/quote?inputMint=So11...&outputMint=TOKEN&amount=1000000&slippage=1
→ { quote, route, priceImpact }

POST /swap
x-api-key: $P0_API_KEY
{"inputMint": "So11...", "outputMint": "TOKEN", "amount": 1000000, "slippage": 1}
→ { signature, inputAmount, outputAmount }
```

### Positions & Alerts
```
GET /positions → your open token positions
GET /alerts → your active price alerts
POST /alerts
{"tokenAddress": "...", "targetPrice": 0.001, "direction": "above"}
→ { alertId }
```

### Favorites
```
GET /favorites → your saved tokens
POST /favorites
{"tokenAddress": "..."}
```

## Account Management

```
GET /account → account info, plan, campaign usage
POST /api-keys → generate additional API key
DELETE /api-keys/{id} → revoke a key
GET /pricing → credit pricing in SOL/USDC/P0
POST /credits/purchase → buy credits
GET /credits/balance → check balance
POST /credits/upgrade → upgrade to Pro (1 SOL/30 days)
```

## Pricing

| Feature | Free Agent | Pro Agent (1 SOL/mo) |
|---------|-----------|---------------------|
| Projects/day | 1 free deploy (pump.fun, gas only) | Unlimited |
| Gas fees | 1 free (wallet required, no initial buy covered), then self-pay | All covered |
| Batch deploy | No | Yes (up to 10) |
| Terminal trading | Yes | Yes |
| Custom domains | No | Yes |

## Strategy

1. Register with wallet to get free campaign deploys
2. Deploy tokens → wait for trading → claim fees
3. Use `GET /earnings` to monitor pending fees
4. Use `POST /claim-all-fees` to sweep earnings
5. Reinvest earned SOL into new deployments
6. Use terminal API to trade and discover opportunities

Built by [p0](https://p0.systems) | [Full docs](https://agents.p0.systems/skill.md)
