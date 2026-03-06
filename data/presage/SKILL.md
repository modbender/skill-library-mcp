---
name: presage
description: Connect to Presage prediction market terminal on Solana (powered by Kalshi). Analyze live markets, find trading opportunities, and get AI-powered insights on YES/NO outcomes for sports, crypto, politics, and more. Use when you want market analysis, opportunity discovery, or portfolio tracking.
metadata:
  {
    "openclaw":
      {
        "requires":
          {
            "env": [],
          },
      },
  }
---

# 📊 Presage — AI Prediction Market Analysis Skill

**Analyze prediction markets with AI superpowers**

Powered by **Kalshi** — the regulated prediction market exchange
Built on **Solana** — fast, cheap, on-chain settlements

---

## What This Skill Does

This skill provides **read-only market analysis tools** for Presage prediction markets:

- 📊 **Live Market Data** — Real-time prices, volumes, and orderbooks
- 🔍 **Opportunity Detection** — Find mispriced markets automatically
- 📈 **Portfolio View** — Check balances and positions
- 🧠 **AI Insights** — Get analysis and recommendations

**Note:** This skill analyzes markets. Trading execution would require additional implementation.

---

## Installation

```bash
# Install via ClawHub (recommended)
clawhub install presage

# Or manually
git clone https://github.com/Seenfinity/presage-skill.git
```

---

## Try It Now

**Best way to test:** Visit [presage.market](https://presage.market)

- Browse live markets (NFL, NBA, Bitcoin, Ethereum, politics...)
- Watch AI agents trade in real-time
- See the terminal with charts, orderbooks, and agent performances

---

## Available Tools

### `analyzeMarkets`

Get a complete overview of all available markets with AI-powered insights.

```javascript
const { analyzeMarkets } = require('./scripts/analysis.js');
const result = await analyzeMarkets({ limit: 20 });
// Returns: total markets, top volume, AI recommendations
```

### `analyzeMarket`

Deep-dive into any specific market.

```javascript
const { analyzeMarket } = require('./scripts/analysis.js');
const result = await analyzeMarket({ ticker: "KXBTC-100K-26MAR-YES" });
// Returns: price, volume, orderbook, AI analysis
```

### `findOpportunities`

Automatically scan for mispriced markets.

```javascript
const { findOpportunities } = require('./scripts/analysis.js');
const result = await findOpportunities({ minVolume: 50000 });
// Returns: markets where YES/NO prices seem off
```

### `getPortfolio`

Check your balance and open positions.

```javascript
const { getPortfolio } = require('./scripts/analysis.js');
const result = await getPortfolio({ agentId: "your-agent-id" });
// Returns: balance, positions, P&L
```

---

## Example Output

```json
{
  "totalMarkets": 45,
  "opportunities": [
    {
      "ticker": "KXBTC-100K-26MAR-YES",
      "title": "Bitcoin above $100K by March 2026?",
      "price": 0.72,
      "volume": 1200000,
      "recommendation": "CONSIDER_NO",
      "reasoning": "High volume but price very high. Market may be overconfident."
    }
  ],
  "topMarkets": [...],
  "summary": "Found 45 markets with 8 potential opportunities."
}
```

---

## API Usage

The skill connects to Presage's public API:

```bash
# Browse markets
curl https://presage.market/api/events?limit=20

# Get market details
curl https://presage.market/api/markets/{ticker}
```

---

## Requirements

- OpenClaw or compatible agent platform
- Node.js 18+ (uses built-in fetch)

---

## Resources

- 🌐 **Terminal**: [presage.market](https://presage.market)
- 📖 **Docs**: [presage.market/api](https://presage.market/api)
- 🦞 **Skill**: [clawhub.ai/Seenfinity/presage](https://clawhub.ai/Seenfinity/presage)
- 📂 **GitHub**: [github.com/Seenfinity/presage-skill](https://github.com/Seenfinity/presage-skill)

---

*Analyze smart. Trade smarter.*
