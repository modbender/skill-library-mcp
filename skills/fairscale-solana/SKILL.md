---
name: FairScale Reputation Skill
description: Real-time wallet reputation scoring for Solana. Use this skill to
  check if a wallet is trustworthy before transacting.
---

# FairScale Reputation Skill

Real-time wallet reputation scoring for Solana. Use this skill to check if a wallet is trustworthy before transacting.

## What This Skill Does

- **Check wallet reputation** before any transaction
- **Assess risk level** for a given transaction amount
- **Apply custom rules** for your specific use case
- **Batch check** multiple wallets at once

## When To Use This Skill

Use FairScale when:
- An agent needs to decide whether to transact with a wallet
- Filtering wallets for airdrops, whitelists, or access control
- Assessing risk before accepting a trade or swap
- Verifying counterparty reputation in agent-to-agent transactions

## Endpoints

### GET /score
Get the FairScore (0-100) for any Solana wallet.

**Free tier:** 100 calls/day
**Pro tier:** 10,000 calls/day

```
GET https://api.fairscale.xyz/score?wallet=ADDRESS
```

**Response:**
```json
{
  "wallet": "7xK9...",
  "fairscore": 72,
  "tier": "gold",
  "vouch_boost": 1.5
}
```

### GET /check
Pre-transaction risk assessment. Returns risk level and recommended max transaction amount.

**Free tier:** 100 calls/day

```
GET https://api.fairscale.xyz/check?wallet=ADDRESS&amount=500
```

**Response:**
```json
{
  "wallet": "7xK9...",
  "fairscore": 72,
  "risk_level": "medium",
  "recommendation": "proceed_with_caution",
  "max_suggested_amount_usd": 1000,
  "amount_check": {
    "requested": 500,
    "max_suggested": 1000,
    "proceed": true
  }
}
```

### POST /score/custom
Apply custom scoring rules. Pro tier required.

```
POST https://api.fairscale.xyz/score/custom
Content-Type: application/json

{
  "wallet": "7xK9...",
  "rules": {
    "min_score": 60,
    "min_age_days": 180,
    "no_rug_history": true,
    "min_transaction_count": 100,
    "min_volume_usd": 10000,
    "max_burst_ratio": 0.5,
    "min_tier": "silver"
  }
}
```

**Response:**
```json
{
  "wallet": "7xK9...",
  "passes": true,
  "fairscore": 72,
  "rule_results": {
    "min_score": { "pass": true, "required": 60, "actual": 72 },
    "min_age_days": { "pass": true, "required": 180, "actual": 340 },
    "no_rug_history": { "pass": true, "actual": false },
    "min_transaction_count": { "pass": true, "required": 100, "actual": 523 }
  },
  "recommendation": "proceed"
}
```

### POST /batch
Score multiple wallets at once. Pro tier required.

```
POST https://api.fairscale.xyz/batch
Content-Type: application/json

{
  "wallets": ["address1", "address2", "address3"]
}
```

**Response:**
```json
{
  "count": 3,
  "results": [
    { "wallet": "address1", "fairscore": 72, "tier": "gold" },
    { "wallet": "address2", "fairscore": 45, "tier": "silver" },
    { "wallet": "address3", "fairscore": 23, "tier": "bronze" }
  ]
}
```

## Score Interpretation

| Score | Tier | Risk Level | Recommendation |
|-------|------|------------|----------------|
| 80-100 | Platinum | Low | Proceed |
| 60-79 | Gold | Medium | Proceed with caution |
| 40-59 | Silver | High | Small amounts only |
| 0-39 | Bronze | Very High | Avoid |

## Example Usage

### Basic Trust Check
```
User: "Should I accept a 500 USDC trade from wallet 7xK9...?"

Agent steps:
1. Call GET /check?wallet=7xK9...&amount=500
2. Response: score 34, risk "very_high", recommendation "avoid"
3. Respond: "This wallet has a very low reputation score (34/100). I recommend not proceeding with this trade."
```

### Filtering for Airdrop
```
User: "Filter this list of wallets for my airdrop - only 60+ score"

Agent steps:
1. Call POST /batch with wallet list
2. Filter results where fairscore >= 60
3. Return qualifying wallets
```

### Custom Agent Rules
```
Agent config: "Only trade with wallets that have score 70+, age 6+ months, no rug history"

Before each trade:
1. Call POST /score/custom with rules
2. Check if passes: true
3. Proceed only if passes
```

## Rate Limits

| Tier | Daily Limit | Rate Limit |
|------|-------------|------------|
| Free | 100 calls | 10/minute |
| Pro | 10,000 calls | 100/minute |
| Enterprise | Unlimited | 1000/minute |

## Authentication

**Free tier:** No authentication required. Rate limited by IP.

**Pro/Enterprise:** Include API key in header:
```
x-api-key: fs_your_api_key_here
```

Get an API key:
```
POST https://api.fairscale.xyz/register
{ "wallet": "your_solana_wallet" }
```

## Upgrade to Pro

For higher limits and custom scoring:

```
POST https://api.fairscale.xyz/upgrade
{
  "api_key": "fs_your_key",
  "tier": "pro",
  "signature": "payment_tx_signature"
}
```

Cost: $50 USDC/month

## Available Custom Rules

| Rule | Type | Description |
|------|------|-------------|
| min_score | number | Minimum FairScore (0-100) |
| min_age_days | number | Minimum wallet age in days |
| no_rug_history | boolean | Reject if wallet has rug history |
| min_transaction_count | number | Minimum number of transactions |
| min_volume_usd | number | Minimum total volume in USD |
| max_burst_ratio | number | Maximum burst ratio (0-1) |
| min_tier | string | Minimum tier (bronze/silver/gold/platinum) |

## Support

- Docs: https://docs.fairscale.xyz
- API Status: https://status.fairscale.xyz
- Contact: api@fairscale.xyz
