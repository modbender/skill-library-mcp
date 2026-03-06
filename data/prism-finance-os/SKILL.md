---
name: prism-finance-os
description: Financial data SDK for AI Agents. 218+ read-only endpoints for market data, prices, fundamentals. Built for Cursor, Claude, OpenClaw. Data retrieval only.
homepage: https://api.prismapi.ai
repository: https://github.com/Strykr-Prism/PRISM-OS-SDK
metadata: {"clawdbot":{"emoji":"📊","requires":{"bins":[],"env":["PRISM_API_KEY"]},"primaryEnv":"PRISM_API_KEY"}}
---

# PRISM Finance OS

> **Financial Data SDK for AI Agents**

Read-only market data SDK. 218+ endpoints for prices, fundamentals, and analytics.

## Security Notes

- **Read-only API** — fetches public market data only
- **No wallet access** — does not interact with wallets or private keys
- **No trading execution** — execute modules are for quote simulation only, not live trades
- **Data only** — returns JSON market data for analysis
- **API key required** — set `PRISM_API_KEY` environment variable

## Quick Start

```bash
npm install prism-finance-os
```

```typescript
import PrismOS from 'prism-finance-os';

const prism = new PrismOS({ apiKey: process.env.PRISM_API_KEY });

// Get crypto price
const btc = await prism.crypto.getConsensusPrice('BTC');

// Get stock fundamentals  
const aapl = await prism.stocks.getFundamentals('AAPL');

// Get DeFi protocol TVL
const tvl = await prism.defi.getProtocolTVL('aave');
```

## Required Environment Variable

```bash
export PRISM_API_KEY=your_api_key_here
```

Get your free API key at [api.prismapi.ai](https://api.prismapi.ai)

## Data Categories

| Category | Examples |
|----------|----------|
| Crypto Prices | BTC, ETH, SOL prices across exchanges |
| Stock Data | Fundamentals, earnings, financials |
| DeFi Analytics | Protocol TVL, yields, stablecoin supply |
| Macro Data | Fed rates, inflation, GDP (via FRED) |
| Technical Analysis | RSI, MACD, moving averages |
| News & Sentiment | Market news with sentiment scores |

## Links

- [API Documentation](https://api.prismapi.ai/docs)
- [GitHub Repository](https://github.com/Strykr-Prism/PRISM-OS-SDK)
- [npm Package](https://www.npmjs.com/package/prism-finance-os)

## License

MIT License - see [LICENSE](https://github.com/Strykr-Prism/PRISM-OS-SDK/blob/main/LICENSE)
