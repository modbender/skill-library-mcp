---
name: token-profiler
description: "One API call replaces CoinGecko + DexScreener + GoPlus + on-chain queries. Enriched token data from 5 sources, clean JSON, under 3 seconds. Free, no key needed."
triggers:
  - token data
  - token info
  - token profile
  - crypto data
  - token lookup
  - what is this token
  - token price
  - token holders
  - token security
requires:
  - network: "https://verdictswarm-production-7460.up.railway.app"
---

# Token Profiler — 5 Sources. One Call. Under 3 Seconds.

**Stop making 5 API calls to get complete token data.** Token Profiler aggregates CoinGecko, DexScreener, GoPlus, and on-chain data into one clean JSON response.

Price. Market cap. Security checks. Holder distribution. Social links. DEX info. All of it, one call.

**No API key needed for free tier.** Install and query immediately.

## The Problem

To get full token intelligence today, your agent needs to:
1. Call CoinGecko for price and socials
2. Call DexScreener for liquidity and DEX data  
3. Call GoPlus for security checks
4. Query on-chain for holders and concentration
5. Merge everything together and hope the formats match

That's 4+ API keys, 4+ rate limits, 4+ failure points. Token Profiler does it in one call.

## Quick Start

```bash
# No API key needed
curl -s "https://verdictswarm-production-7460.up.railway.app/v1/token?address=JUPyiwrYJFskUPiHa7hkeR8VUtAeFoSYbKedZNsDvCN" | python3 -m json.tool
```

## What You Get Back

```json
{
  "name": "Jupiter",
  "symbol": "JUP",
  "chain": "solana",
  "price": 0.82,
  "price_change_24h": -2.3,
  "mcap": 577000000,
  "fdv": 1400000000,
  "holders": 245000,
  "top10_concentration": 34.2,
  "age_days": 760,
  "liquidity": 12500000,
  "volume_24h": 8900000,
  "security": {
    "mint_authority": "revoked",
    "freeze_authority": "revoked",
    "honeypot": false,
    "is_proxy": false,
    "has_blacklist": false
  },
  "socials": {
    "twitter": "@JupiterExchange",
    "website": "jup.ag",
    "discord": "...",
    "telegram": "..."
  },
  "dex": {
    "pairs": 47,
    "top_dex": "Raydium",
    "top_pair_address": "..."
  },
  "sources": ["coingecko", "dexscreener", "goplus", "onchain"],
  "fetched_at": "2026-03-02T04:40:00Z"
}
```

## Every Field, Every Source

| Data | Source | Why It Matters |
|------|--------|---------------|
| Price, MCap, FDV | CoinGecko + DexScreener | Real-time valuation |
| Volume, Liquidity | DexScreener | Is there actual trading activity? |
| Security Checks | GoPlus | Can the dev rug you? (mint, freeze, honeypot) |
| Holders & Concentration | On-chain | Is this 10 whales or 100K real users? |
| Age | On-chain | 2 days old = high risk. 2 years = more established. |
| Socials | CoinGecko | Does this project even have a website? |
| DEX Info | DexScreener | Where is it actually trading? |

## Pricing

| Tier | Cost | Limit |
|------|------|-------|
| **Free** | $0 / no key | 100 lookups/day |
| **Paid** | Paid plans available | Unlimited |

## When to Use This vs VerdictSwarm

- **Token Profiler** → "What IS this token?" — raw data, fast, cheap
- **VerdictSwarm** → "Should I BUY this token?" — 6 AI agents debate the risk

Install both: `token-profiler` for data, `verdictswarm` for analysis.

## Supported Chains

Solana · Ethereum · Base — more coming.

## Agent Instructions

When the user asks about a token's price, holders, security, market cap, or general data — use this skill. Pass the contract address or common name (SOL, ETH, JUP) to the endpoint. Return the relevant fields based on what the user asked. For risk analysis or "should I buy" questions, suggest the `verdictswarm` skill instead.
