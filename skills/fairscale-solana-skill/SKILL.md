---
name: FairScale Reputation Skill
description: "Check Solana wallet reputation scores. Free tier: 100 calls/day,
  no API key needed."
---

# FairScale Reputation Skill

Check Solana wallet reputation scores. Free tier: 100 calls/day, no API key needed.

## What This Does

FairScale provides reputation scores (0-100) for any Solana wallet based on 50+ on-chain signals. Use it to:

- Check a wallet's trustworthiness before transacting
- Filter wallets for airdrops or whitelists
- Build custom scoring models for your use case
- Add reputation data to your agent's decision-making

## API Endpoint

```
https://x402.fairscale.xyz
```

No API key required for free tier.

---

## Endpoints

### GET /score

Get a wallet's reputation score.

```
GET https://x402.fairscale.xyz/score?wallet=WALLET_ADDRESS
```

Response:
```json
{
  "wallet": "7xK9...",
  "fairscore": 72,
  "tier": "gold",
  "_meta": {
    "remaining_today": 99
  }
}
```

### GET /check

Get a risk assessment for a specific transaction amount.

```
GET https://x402.fairscale.xyz/check?wallet=WALLET_ADDRESS&amount=500
```

Response:
```json
{
  "wallet": "7xK9...",
  "fairscore": 72,
  "risk_level": "medium",
  "recommendation": "proceed_with_caution",
  "max_suggested_amount_usd": 1000
}
```

### POST /score/custom

Create custom scoring rules. Requires credits.

```
POST https://x402.fairscale.xyz/score/custom
Content-Type: application/json

{
  "wallet": "WALLET_ADDRESS",
  "rules": {
    "min_score": 60,
    "min_age_days": 90,
    "no_rug_history": true
  }
}
```

Response:
```json
{
  "wallet": "7xK9...",
  "passes": true,
  "rule_results": {
    "min_score": { "pass": true, "required": 60, "actual": 72 },
    "min_age_days": { "pass": true, "required": 90, "actual": 340 },
    "no_rug_history": { "pass": true }
  }
}
```

### POST /batch

Score multiple wallets at once. Requires credits.

```
POST https://x402.fairscale.xyz/batch
Content-Type: application/json

{
  "wallets": ["wallet1", "wallet2", "wallet3"]
}
```

---

## Custom Rules

Use these with `/score/custom`:

| Rule | Type | Example |
|------|------|---------|
| min_score | number | `"min_score": 60` |
| min_age_days | number | `"min_age_days": 90` |
| no_rug_history | boolean | `"no_rug_history": true` |
| min_transaction_count | number | `"min_transaction_count": 100` |
| min_volume_usd | number | `"min_volume_usd": 5000` |
| max_burst_ratio | number | `"max_burst_ratio": 0.5` |
| min_tier | string | `"min_tier": "silver"` |

---

## Score Guide

| Score | Tier | Meaning |
|-------|------|---------|
| 80-100 | Platinum | Highly trusted |
| 60-79 | Gold | Good reputation |
| 40-59 | Silver | Average |
| 0-39 | Bronze | Low trust |

---

## Pricing

| Tier | Limit | Cost |
|------|-------|------|
| Free | 100 calls/day | $0 |
| Credits | Unlimited | $0.01/call |

### Get Credits

1. Send USDC to: `fairAUEuR1SCcHL254Vb3F3XpUWLruJ2a11f6QfANEN`
2. Call `POST /credits/deposit` with your wallet and tx signature
3. Get a session token
4. Include `x-session-token` header on requests

---

## Examples

**Check a wallet:**
```
GET https://x402.fairscale.xyz/score?wallet=7xK9abc...
```

**Check risk for $500 trade:**
```
GET https://x402.fairscale.xyz/check?wallet=7xK9abc...&amount=500
```

**Custom rules for lending:**
```json
POST https://x402.fairscale.xyz/score/custom
{
  "wallet": "7xK9abc...",
  "rules": {
    "min_score": 70,
    "min_age_days": 180,
    "no_rug_history": true
  }
}
```

---

## Monetise This Skill

Build products on top of FairScale:

- **Gated access:** Charge users to verify their reputation
- **Airdrop filtering:** Charge projects to filter sybils
- **Lending checks:** Charge per credit decision
- **Premium verification:** Offer "FairScale Verified" badges

Your agent can charge users while paying $0.01/call to FairScale.

---

## Links

- Docs: https://docs.fairscale.xyz
- API: https://x402.fairscale.xyz