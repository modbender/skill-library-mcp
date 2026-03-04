# PRISM — Elite Agentic Finance SDK

> **The #1 Financial Data SDK for OpenClaw, Claude Code, Cursor & Autonomous Trading Bots**

[![npm version](https://img.shields.io/npm/v/prismapi-sdk.svg)](https://www.npmjs.com/package/prismapi-sdk)
[![npm downloads](https://img.shields.io/npm/dm/prismapi-sdk.svg)](https://www.npmjs.com/package/prismapi-sdk)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**One SDK. All financial data. Sub-50ms latency. 100+ endpoints.**

The elite agentic finance toolkit. Drop-in market intelligence for OpenClaw, Claude Code, Cursor, ChatGPT, Copilot, or your custom autonomous trading bot. Canonical asset resolution across crypto, stocks, and DeFi.

## Why Elite Agents Choose PRISM

| Problem | PRISM Solution |
|---------|---------------|
| Fragmented APIs | **One unified SDK** — crypto, stocks, DeFi, forex in a single call |
| Symbol collisions | **Canonical Resolution** — resolve BTC vs COIN vs any ticker/contract |
| Slow data feeds | **Sub-50ms P50 latency** — cache-first architecture |
| Agent-unfriendly data | **MCP-native** — built for OpenClaw, Claude, function calling |
| Wrapped token hell | **Family grouping** — BTC, WBTC, cbBTC, tBTC in one query |

## Installation

```bash
npm install prismapi-sdk
```

Or with yarn/pnpm:

```bash
yarn add prismapi-sdk
pnpm add prismapi-sdk
```

## Quick Start (30 seconds)

```typescript
import { PrismClient } from 'prismapi-sdk';

const prism = new PrismClient({ apiKey: 'your-api-key' });

// Resolve any symbol to canonical data (sub-50ms)
const btc = await prism.resolve('BTC');
// → { canonical: 'BTC', name: 'Bitcoin', price: 71514.84, confidence: 0.97 }

// Batch resolve for trading agents
const assets = await prism.resolveBatch(['BTC', 'ETH', 'AAPL', 'SOL']);

// Get family (wrapped tokens, derivatives)
const family = await prism.getFamily('BTC');
// → [BTC, WBTC, cbBTC, tBTC, renBTC]

// Get trading venues with direct URLs
const venues = await prism.getVenues('ETH');
// → { cex_spot: [...], cex_perp: [...], dex_spot: [...], dex_perp: [...] }

// Stock fundamentals
const aapl = await prism.tradfi.getStock('AAPL');
```

## 24 Modules, 218+ Endpoints

| Module | Methods | What It Does |
|--------|---------|-------------|
| **Resolution** | 17 | Canonical ID resolution — the core of PRISM |
| **Crypto** | 26 | Prices, trending, market cap, NVT valuation |
| **DeFi** | 17 | Protocols, TVL, yields, stablecoins, bridges, gas, wallets, DEX |
| **Onchain** | 10 | Whale movements, exchange flows, supply, holders |
| **Stocks** | 23 | Quotes, fundamentals, earnings, financials, DCF, insiders |
| **ETFs** | 3 | Holdings, sector weights |
| **Forex** | 2 | Live FX quotes |
| **Commodities** | 2 | Gold, oil, metals |
| **Macro** | 14 | Fed rate, inflation, GDP, treasury yields, FRED series |
| **Historical** | 6 | OHLCV, returns, volatility, comparison |
| **News** | 3 | Crypto + stock news with sentiment |
| **Calendar** | 3 | Earnings, economic events |
| **Technicals** | 9 | RSI, MACD, MAs, support/resistance, trend, correlations |
| **Signals** | 5 | Momentum, volume spikes, breakouts, divergence |
| **Risk** | 3 | VaR, Sharpe, portfolio risk |
| **Order Book** | 4 | Depth, spread, imbalance |
| **Trades** | 2 | Recent and large/block trades |
| **Social** | 5 | Sentiment, mentions, trending, GitHub activity |
| **Analysis** | 7 | Fork/copycat/rebrand/bridge detection |
| **Predictions** | 15 | Polymarket, Kalshi, Manifold — markets, odds, arbitrage |
| **Sports** | 7 | Events, odds, live scores |
| **Odds** | 6 | Arbitrage finder, odds comparison, history |
| **Developer** | 9 | API keys, usage, health, rate limits |
| **Agent** | 3 | Context injection, endpoint discovery, schemas |

## Use Cases

### AI Trading Agent

```typescript
// Get all signals + technicals + sentiment for a trading decision
const signals = await prism.signals.getSummary('ETH');
const ta = await prism.technicals.analyze('ETH');
const sentiment = await prism.social.getSentiment('ETH');

console.log(`Trend: ${ta.trend}, RSI: ${ta.rsi}`);
console.log(`Sentiment: ${sentiment.label} (${sentiment.bullish_pct}% bullish)`);
```

### DeFi Yield Scanner

```typescript
const yields = await prism.defi.getYields({
  min_tvl: 1_000_000,
  stablecoin: true,
  min_apy: 5,
});

for (const pool of yields) {
  console.log(`${pool.protocol}: ${pool.apy}% APY, $${pool.tvl} TVL`);
}
```

### Cross-Asset Portfolio Risk

```typescript
const risk = await prism.risk.analyzePortfolio([
  { symbol: 'BTC', weight: 0.3 },
  { symbol: 'ETH', weight: 0.2 },
  { symbol: 'AAPL', weight: 0.2, asset_type: 'stock' },
  { symbol: 'GLD', weight: 0.15, asset_type: 'etf' },
  { symbol: 'SPY', weight: 0.15, asset_type: 'etf' },
]);

console.log(`Portfolio VaR (95%): ${risk.total_var}%`);
console.log(`Sharpe Ratio: ${risk.sharpe}`);

const corr = await prism.technicals.getCorrelations(['BTC', 'ETH', 'SPY']);
console.log(`BTC-SPY Correlation: ${corr.matrix['BTC']['SPY']}`);
```

### Prediction Market Arbitrage

```typescript
const arbs = await prism.predictions.getArbitrage({ min_profit: 2 });

for (const opp of arbs) {
  console.log(`${opp.event}: ${opp.arbPct}% profit`);
  console.log(`  ${opp.venue1} vs ${opp.venue2}`);
}
```

### Resolve Any Asset

```typescript
// Ticker, name, contract address — PRISM resolves them all
const eth = await prism.resolve.resolve('ETH');
const byName = await prism.resolve.resolve('Ethereum');
const byContract = await prism.resolve.resolve('0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2');

// Batch resolve
const assets = await prism.resolve.resolveBatch(['BTC', 'SOL', 'AAPL', 'EUR/USD']);
```

### Agent Context Injection

```typescript
// Get everything an AI agent needs in ONE call
const context = await prism.agent.getContext();
// Returns: market_snapshot, macro_summary, trending, timestamp

// Discover all available endpoints (for dynamic tool generation)
const endpoints = await prism.agent.getEndpoints();
// Returns: path, method, tag, summary, parameters for each endpoint

// Get JSON schemas for type validation in pipelines
const schemas = await prism.agent.getSchemas();
```

### Whale Tracking

```typescript
const whales = await prism.onchain.getWhaleMovements('0x...address', {
  chain: 'ethereum',
  min_value_usd: 1_000_000,
  limit: 20,
});

for (const tx of whales) {
  console.log(`${tx.from} -> ${tx.to}: $${tx.value_usd}`);
}
```

### Macro Dashboard

```typescript
const macro = await prism.macro.getSummary();
console.log(`Fed Rate: ${macro.fed_rate}%`);
console.log(`Inflation: ${macro.inflation}%`);
console.log(`10Y Treasury: ${macro.treasury_10y}%`);
console.log(`Yield Curve Inverted: ${macro.yield_curve_inverted}`);

// Deep dive into any FRED series
const sofr = await prism.macro.getSeries('SOFR');
```

## MCP Server (Claude Desktop & Claude Code)

Use PRISM as 21 native tools inside Claude via the [PRISM MCP Server](https://github.com/Strykr-Prism/PRISM-MCP-Server):

```bash
git clone https://github.com/Strykr-Prism/PRISM-MCP-Server.git
cd PRISM-MCP-Server && npm install && npm run build
```

Then ask Claude things like:
- *"What's the price of Bitcoin?"*
- *"Show me DeFi yields above 10% on Arbitrum"*
- *"Run technical analysis on ETH"*
- *"What's the macro summary?"*

## Works With All Elite AI Agents

| Platform | Integration |
|----------|-------------|
| **OpenClaw / Clawdbot** | Native skill + MCP server |
| **Claude Code** | MCP tools + function calling |
| **Cursor** | Drop into any project |
| **ChatGPT** | GPT function calling |
| **LangChain / LlamaIndex** | Tool integration |
| **AutoGPT / CrewAI** | Agent framework compatible |
| **Custom bots** | REST API + TypeScript SDK |

## Configuration

```typescript
const prism = new PrismOS({
  apiKey: 'your-api-key',             // Required — get from api.prismapi.ai
  baseUrl: 'https://api.prismapi.ai', // Optional, default shown
  timeout: 10_000,                    // Optional, ms, default shown
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

- [API Documentation](https://api.prismapi.ai/docs)
- [MCP Server](https://github.com/Strykr-Prism/PRISM-MCP-Server)
- [Discord](https://discord.gg/strykr)
- [Twitter](https://twitter.com/strykrai)
- [GitHub](https://github.com/Strykr-Prism/PRISM-OS-SDK)

## License

MIT — use it however you want.

---

**Built by [Strykr AI](https://strykr.ai)** — Elite Market Intelligence for the Agentic Era.

### SEO Keywords
`agentic finance sdk` `openclaw finance` `ai agent market data` `claude trading tools` `mcp server finance` `autonomous trading api` `crypto api for llms` `defi sdk` `real-time market data` `asset resolution api` `unified finance api` `trading bot sdk`
