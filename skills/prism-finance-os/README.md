# PRISM Finance OS

> **The Financial Operating System for AI Agents, Cursor, Claude, ChatGPT & Autonomous Trading Bots**

[![npm version](https://img.shields.io/npm/v/prism-finance-os.svg)](https://www.npmjs.com/package/prism-finance-os)
[![npm downloads](https://img.shields.io/npm/dm/prism-finance-os.svg)](https://www.npmjs.com/package/prism-finance-os)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**One SDK. All financial data. 218+ endpoints.**

Built for the vibe-coding era. Drop-in financial intelligence for any AI agent — Cursor, Claude, OpenClaw, ChatGPT, Copilot, or your custom autonomous trading bot.

## Why PRISM Finance OS?

| Problem | PRISM Solution |
|---------|---------------|
| Fragmented APIs | **One unified SDK** — crypto, stocks, DeFi, forex, macro, predictions |
| No canonical IDs | **Chronicle ID** — resolve any ticker/contract to single source of truth |
| Agent-unfriendly data | **Context injection** — get everything an AI needs in one call |
| Expensive data | **Free tier + affordable plans** — 70% of data sources are free |

## Installation

```bash
npm install prism-finance-os
```

## Quick Start (30 seconds)

```typescript
import PrismOS from 'prism-finance-os';

const prism = new PrismOS({ apiKey: 'your-api-key' });

// Get crypto price
const btc = await prism.crypto.getConsensusPrice('BTC');

// Get stock fundamentals
const aapl = await prism.stocks.getFundamentals('AAPL');

// Get DeFi yields
const yields = await prism.defi.getTopYields({ minTvl: 1_000_000 });

// Get prediction markets
const markets = await prism.predictions.getTrending();
```

## 24 Modules, 218+ Endpoints

| Module | Methods | What It Does |
|--------|---------|-------------|
| **Resolution** | 17 | Canonical ID resolution — the core of PRISM |
| **Crypto** | 26 | Prices, trending, market cap, NVT valuation |
| **DeFi** | 17 | Protocols, TVL, yields, stablecoins, bridges |
| **Onchain** | 9 | Whale movements, exchange flows, supply |
| **Stocks** | 20 | Quotes, fundamentals, earnings, DCF |
| **ETFs** | 3 | Holdings, sector weights |
| **Forex** | 2 | Live quotes |
| **Commodities** | 2 | Gold, oil, metals |
| **Macro** | 11 | Fed rate, inflation, GDP, treasury yields |
| **Historical** | 6 | OHLCV, returns, volatility |
| **News** | 3 | Crypto + stock news with sentiment |
| **Calendar** | 3 | Earnings, economic events |
| **Technicals** | 8 | RSI, MACD, MAs, support/resistance |
| **Signals** | 5 | Momentum, breakouts, divergence |
| **Risk** | 3 | VaR, Sharpe, portfolio risk |
| **Order Book** | 4 | Depth, spread, imbalance |
| **Trades** | 2 | Recent and large trades |
| **Social** | 5 | Sentiment, mentions, GitHub activity |
| **Analysis** | 7 | Fork/copycat/rebrand detection |
| **Predictions** | 10 | Polymarket, Kalshi, Manifold |
| **Sports** | 7 | Events, live scores |
| **Odds** | 5 | Arbitrage finder, odds history |
| **Developer** | 8 | API keys, usage, health |
| **Agent** | 3 | Context injection, endpoint discovery |

## Use Cases

### AI Trading Agent

```typescript
// Get all signals for a trading decision
const signals = await prism.signals.getAll('ETH');
const technicals = await prism.technicals.getAll('ETH');
const sentiment = await prism.social.getSentiment('ETH');

if (signals.momentum > 0.7 && sentiment.score > 0.6) {
  // Execute trade
}
```

### DeFi Yield Scanner

```typescript
const yields = await prism.defi.getTopYields({
  minTvl: 1_000_000,
  stablecoinOnly: true,
  minApy: 5,
});

// Returns sorted by risk-adjusted yield
for (const pool of yields) {
  console.log(`${pool.protocol}: ${pool.apy}% APY, $${pool.tvl} TVL`);
}
```

### Cross-Asset Portfolio Analysis

```typescript
const portfolio = ['BTC', 'ETH', 'AAPL', 'GLD', 'SPY'];

const risk = await prism.risk.getPortfolioRisk(portfolio);
const correlation = await prism.technicals.getCorrelation(portfolio);

console.log(`Portfolio VaR: ${risk.var95}%`);
console.log(`BTC-SPY Correlation: ${correlation['BTC-SPY']}`);
```

### Prediction Market Arbitrage

```typescript
const arb = await prism.odds.getArbitrage();

for (const opp of arb.opportunities) {
  console.log(`${opp.market}: ${opp.profit}% profit`);
  console.log(`Buy ${opp.yes.platform} YES @ ${opp.yes.price}`);
  console.log(`Buy ${opp.no.platform} NO @ ${opp.no.price}`);
}
```

### Agent Context Injection (For AI Agents)

```typescript
// Get everything an AI agent needs about an asset in ONE call
const context = await prism.agent.getContext('ETH');
// Returns: price, fundamentals, technicals, news, sentiment, signals

// Discover relevant endpoints for a task
const endpoints = await prism.agent.discoverEndpoints('find high yield stablecoin pools');
// Returns: prism.defi.getTopYields, prism.defi.getStablecoins, etc.
```

## Works With Everything

- ✅ **Cursor** — drop into any Cursor project
- ✅ **Claude** — use with Claude's tool calling
- ✅ **OpenClaw / Clawdbot** — native integration
- ✅ **ChatGPT** — GPT function calling compatible
- ✅ **Copilot** — works in any VS Code setup
- ✅ **LangChain** — use as a LangChain tool
- ✅ **AutoGPT / AgentGPT** — plug into any agent framework
- ✅ **Custom agents** — simple REST API under the hood

## Configuration

```typescript
const prism = new PrismOS({
  apiKey: 'your-api-key',          // Get from api.prismapi.ai
  baseUrl: 'https://api.prismapi.ai', // default
  timeout: 10_000,                    // ms, default
});
```

## Get Your API Key

1. Go to [api.prismapi.ai](https://api.prismapi.ai)
2. Sign up (free tier available)
3. Copy your API key
4. Start building

## Pricing

| Tier | Price | Calls/mo | Rate Limit |
|------|-------|----------|------------|
| **Free** | $0 | 5,000 | 10/min |
| **Hobby** | $9/mo | 25,000 | 20/min |
| **Dev** | $29/mo | 100,000 | 60/min |
| **Pro** | $99/mo | 500,000 | 120/min |

## Links

- 📚 [API Documentation](https://api.prismapi.ai/docs)
- 💬 [Discord](https://discord.gg/strykr)
- 🐦 [Twitter](https://twitter.com/strykrai)
- 🐙 [GitHub](https://github.com/Strykr-Prism/PRISM-OS-SDK)

## License

MIT — use it however you want.

---

**Built by [Strykr AI](https://strykr.ai)** — Market Intelligence for the Agentic Era.
