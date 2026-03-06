---
name: prismapi-sdk
description: Elite Agentic Finance SDK for OpenClaw, Claude & Autonomous Trading Bots. Real-time market data, canonical asset resolution, 100+ endpoints for crypto, DeFi, stocks. Sub-50ms latency.
homepage: https://prismapi.ai
metadata: {"clawdbot":{"emoji":"💎","requires":{"bins":["node"],"env":[]}}}
---

# PRISM API SDK

The elite agentic finance toolkit. Drop-in market intelligence for AI agents, Claude Code, Cursor, or autonomous trading bots.

## Quick Start

```bash
npm install prismapi-sdk
```

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
```

## Key Features

| Feature | Description |
|---------|-------------|
| **Canonical Resolution** | Resolve any ticker, contract, or symbol to single source of truth |
| **Sub-50ms Latency** | Cache-first architecture with 4-layer resolution |
| **100+ Endpoints** | Crypto, DeFi, stocks, forex, macro, predictions |
| **Family Grouping** | BTC → WBTC, cbBTC, tBTC in one query |
| **MCP-Native** | Built for OpenClaw, Claude, function calling |

## API Categories

- **Resolution** (12 endpoints) - Symbol disambiguation, batch resolve, family grouping
- **Crypto** (35+ endpoints) - Prices, markets, OHLCV, metadata
- **TradFi** (30+ endpoints) - Stocks, ETFs, forex, financials
- **DEX** (25+ endpoints) - Pairs, pools, trending tokens
- **DeFi** - Yields, protocols, TVL
- **Predictions** - Polymarket, Kalshi, sports odds

## Security Notes

- **Read-only API** — fetches public market data only
- **No wallet access** — does not interact with wallets or private keys
- **No trading** — cannot execute trades
- **Data only** — returns JSON market data

## Links

- **Docs:** https://prismapi.ai/docs
- **npm:** https://www.npmjs.com/package/prismapi-sdk
- **GitHub:** https://github.com/Strykr-Prism/PRISM-OS-SDK
