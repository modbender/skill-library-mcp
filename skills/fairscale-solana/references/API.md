# FairScale API Reference

## Base URL

```
https://api2.fairscale.xyz
```

## Authentication

All requests require a `fairkey` header:

```
fairkey: your_api_key_here
```

Get your API key at: https://sales.fairscale.xyz

---

## Endpoints

### GET /score

Full wallet reputation score with badges, features, and improvement actions.

**Request:**
```bash
curl "https://api2.fairscale.xyz/score?wallet=WALLET_ADDRESS" \
  -H "accept: application/json" \
  -H "fairkey: YOUR_API_KEY"
```

**Response:**
```json
{
  "fairscore": 43.2,
  "fairscore_base": 43.2,
  "social_score": 0.0,
  "tier": "silver",
  "badges": [
    {"id": "lst_staker", "label": "LST Staker", "description": "Holds Liquid Staking Tokens"},
    {"id": "diamond_hands", "label": "Diamond Hands", "description": "Long-term holder"}
  ],
  "actions": [
    {"id": "increase_lst", "label": "Increase LST Holdings", "description": "Top scorers hold 50%+ in LST"}
  ],
  "features": {
    "tx_count": 74.8,
    "active_days": 81.1,
    "platform_diversity": 97.4,
    "conviction_ratio": 45.5,
    "burst_ratio": 10.2,
    "no_instant_dumps": 25,
    "stable_percentile_score": 76.5,
    "wallet_age_percentile": 99.2
  }
}
```

### GET /fairScore

Just the score number.

**Request:**
```bash
curl "https://api2.fairscale.xyz/fairScore?wallet=WALLET_ADDRESS" \
  -H "fairkey: YOUR_API_KEY"
```

**Response:**
```json
{"fairscore": 43.2}
```

### GET /walletScore

Wallet behavior score only (excludes social).

**Request:**
```bash
curl "https://api2.fairscale.xyz/walletScore?wallet=WALLET_ADDRESS" \
  -H "fairkey: YOUR_API_KEY"
```

---

## Tiers

| Score Range | Tier |
|-------------|------|
| 0-19 | Bronze |
| 20-39 | Bronze |
| 40-59 | Silver |
| 60-79 | Gold |
| 80-100 | Diamond |

---

## Feature Definitions

| Feature | Description |
|---------|-------------|
| `tx_count` | Percentile of transaction count |
| `active_days` | Percentile of days with on-chain activity |
| `platform_diversity` | Percentile of unique DeFi protocols used |
| `conviction_ratio` | % of holdings held through volatility |
| `burst_ratio` | Bot detection: high = suspicious |
| `no_instant_dumps` | % of positions NOT sold within 24h |
| `stable_percentile_score` | Stablecoin holdings percentile |
| `wallet_age_percentile` | Account age percentile |

---

## Rate Limits

- 100 requests per minute per API key
- Contact team@fairscale.xyz for higher limits

---

## Links

- API Docs: https://api2.fairscale.xyz/docs
- Get API Key: https://sales.fairscale.xyz
- Twitter: @FairScaleXYZ
