---
name: verdictswarm
description: "Multi-agent crypto token intelligence. 6 AI agents independently analyze and debate a token's fundamentals before reaching consensus. Free, no API key needed."
triggers:
  - scan token
  - analyze crypto
  - is this token safe
  - token risk
  - crypto analysis
  - should I buy this token
  - check this token
requires:
  - network: "https://verdictswarm-production-7460.up.railway.app"
---

# VerdictSwarm — Multi-Agent Token Intelligence

**Get a second, third, fourth, fifth, and sixth opinion on any crypto token.**

Six specialized AI agents independently analyze your token from different angles, then debate their findings across multiple rounds before reaching consensus. You see the full analysis and any disagreements.

> "What do you think of this token?" → 6 agents analyze → Consensus reached → You decide

**No API key needed for free tier.** Install and start immediately.

## How It Works

Each agent specializes in a different aspect of token analysis:

| Agent | Focus Area |
|-------|-----------|
| 🔒 Security Auditor | Smart contract review, permissions, authority status |
| 📊 Market Analyst | Price trends, volume, liquidity, market cap analysis |
| 👥 Community Investigator | Social presence, holder distribution, engagement |
| 💰 Tokenomics Expert | Supply mechanics, vesting schedules, distribution |
| 📈 Technical Analyst | Chart patterns, volume trends, momentum indicators |
| ⚠️ Risk Assessor | Overall risk profile, comparative analysis |

## Quick Start

```bash
curl -s "https://verdictswarm-production-7460.up.railway.app/v1/scan" \
  -H "Content-Type: application/json" \
  -d '{"address": "JUPyiwrYJFskUPiHa7hkeR8VUtAeFoSYbKedZNsDvCN"}' | python3 -m json.tool
```

## Response

```json
{
  "verdict": {
    "score": 82,
    "risk_level": "LOW",
    "recommendation": "SAFE",
    "consensus": "5/6 agents agree: strong fundamentals, active development"
  },
  "agents": [
    { "name": "Security Auditor", "score": 85, "analysis": "..." },
    { "name": "Market Analyst", "score": 78, "analysis": "..." }
  ],
  "debate": {
    "rounds": 3,
    "dissenting_opinions": ["Market Analyst noted declining volume trend..."]
  },
  "report_url": "https://verdictswarm-production-7460.up.railway.app/report/abc123",
  "token": {
    "name": "Jupiter",
    "symbol": "JUP",
    "chain": "solana"
  }
}
```

Every scan generates a **shareable report page** at the `report_url`.

## Pricing

| Tier | Cost | Details |
|------|------|---------|
| **Free** | $0 / no key needed | 5 scans/day, 2-agent quick analysis |
| **PRO** | Paid plans available | Full 6-agent analysis, unlimited |

## Related

- **Token Profiler:** Install `token-profiler` for raw aggregated data (no AI, just data from 5+ sources)

## Agent Instructions

When the user asks to analyze or check a crypto token, call the scan endpoint with the token's contract address. Present the verdict score, risk level, and consensus summary. If agents disagreed, highlight the differences. Include the `report_url` for the full breakdown.

Supported chains: Solana, Ethereum, Base.
