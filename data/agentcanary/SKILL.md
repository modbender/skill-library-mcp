---
name: agentcanary
description: Market intelligence API for AI agents. Macro regime detection, risk scoring, trading signals (IGNITION/ACCUMULATION/DISTRIBUTION/CAPITULATION), whale alerts, funding arbitrage, orderbook analytics, 29 technical indicators, RSI screening (606 coins), breaking news with FinBERT sentiment, economic calendar, treasury tracking, and Polymarket odds. 33 endpoints, 1181 assets, 250+ sources. Use when an agent needs macro regime context, risk assessment, position sizing guidance, market structure data, whale activity monitoring, or news sentiment. API-only — no local execution, no filesystem access, no secrets in prompt.
---

# AgentCanary

Market intelligence for AI agents. 33 API endpoints. Not raw data — intelligence.

**Status:** Preview. API access opening soon. Free tier: real-time prices (50 calls/day).
**Live proof:** [@AgentCanary on Telegram](https://t.me/AgentCanary) — 3x/day auto-generated market intelligence from the same API.
**Website:** [agentcanary.ai](https://agentcanary.ai)
**Waitlist:** Sign up at [agentcanary.ai](https://agentcanary.ai) to get notified when API access opens.

> This API powers Proximity, a crypto intelligence iOS app with 6 months of daily usage across 20+ countries.

---

## Security

- **API-only** — HTTP GET calls returning JSON. No local code, no binaries, no shell commands.
- **No secrets in the prompt** — wallet-based auth when billing is live.
- **Read-only** — fetches data. Cannot write, modify, or access your filesystem.

824 malicious skills were found on ClawHub. Crypto and finance is the #1 target category. AgentCanary is the finance skill that can't steal from you.

---

## Default Agent Pattern

```
1. Call /macro-snapshot/regime every 4–6 hours
2. If Risk-Off → suppress trading, reduce exposure
3. If Risk-On → allow strategy execution
4. Use severity alerts as interrupts, not drivers
5. Call /signal-state before entering positions for confirmation
```

AgentCanary is risk intelligence middleware. It tells your agent **when conditions are favorable** — your agent decides what to do.

---

## What It Does Not Do

- Does not predict prices — classifies regimes and states
- Does not guarantee returns
- Does not place orders or replace execution logic
- Does not provide financial advice

---

## Capabilities (33 Endpoints)

For full endpoint documentation with real response examples, read [references/endpoints.md](references/endpoints.md).

### Macro & Regime
| Endpoint | What it returns |
|----------|----------------|
| `/macro-snapshot` | Regime, business cycle, risk gauge, z-scores on 26 FRED indicators |
| `/macro-snapshot/regime` | Regime label, flags, composite scores, explanation |
| `/market-analysis/latest` | AI-generated daily report: sentiment, fear & greed, narratives, alerts |

### Signals & Technicals
| Endpoint | What it returns |
|----------|----------------|
| `/signal-state` | 100 coins, IGNITION/ACCUMULATION/DISTRIBUTION/CAPITULATION on 1d + 4h |
| `/cointa?id={coinId}` | 29 technical indicators, composite buy/sell signal, 365 data points |
| `/coin-rsi/statistics` | 606 coins RSI screening, overbought/oversold ranked lists |
| `/coin-rsi/multi?coinids={id}` | 6-timeframe RSI (5m to 1w) per coin |
| `/roc/{coinId}` | 90-day rate of change, acceleration, volatility, percentile bands |

### Market Structure & Orderbook
| Endpoint | What it returns |
|----------|----------------|
| `/market-structure` | BTC funding, liquidations, OI, crowding scores, signal |
| `/orderbook/depth` | 8 liquidity bands, top bid/ask walls, notional USD |
| `/orderbook/wall-persistence` | Wall persistence tracking over time |
| `/orderbook/liquidity-change` | Liquidity shift detection |

### Whales & Funding
| Endpoint | What it returns |
|----------|----------------|
| `/whale-alerts` | On-chain whale transactions with symbol, amount, USD value |
| `/hyperliquid-whale-alerts` | HL whale position changes with entry/liq prices |
| `/hyperliquid-whale-positions` | Current whale positions: leverage, margin, unrealized PnL |
| `/fundingrate/arbitrage/top` | Top 10 cross-exchange arb opportunities by APR |

### News & Social
| Endpoint | What it returns |
|----------|----------------|
| `/news/breaking` | Real-time news, FinBERT sentiment + confidence, auto-extracted tickers |
| `/newsletters` | 50+ newsletters daily, full-text parsed, tickers, categories |
| `/xtg-messages` | 300+ messages/day from 200+ X & Telegram channels, FinBERT scored |

### Prices & Data
| Endpoint | What it returns |
|----------|----------------|
| `/realtime-prices` | 1,181 assets (941 crypto, 195 stocks, 34 FX, 10 commodities) |
| `/chartdata` | OHLCV candles, configurable resolution (1m to 1d), date range |
| `/usdt-dominance` | USDT dominance as risk-on/risk-off signal |
| `/usdc-dominance` | USDC dominance |
| `/exchange-volumes` | Aggregated exchange trading volumes |
| `/exchange-assets` | 39+ exchange wallets, balance + USD value per exchange |

### Calendar, Treasury & Prediction
| Endpoint | What it returns |
|----------|----------------|
| `/financial-calendar/high-impact` | Global macro events, impact scoring, forecast/previous values |
| `/treasury/stats` | 209 entities, 35 countries, $137B+ tracked crypto treasuries |
| `/polymarket/events/current` | FOMC decision odds from Polymarket |

---

## Signal Cadence Guide

| Signal | Update Frequency | Recommended Cadence |
|--------|-----------------|-------------------|
| Macro regime | Every 6h | Every 4–6 hours |
| Signal states (1d) | Daily close | Every 4–6 hours |
| Signal states (4h) | Every 4h | Every 1–2 hours |
| Whale alerts | Real-time | Every 15–30 min |
| Funding rates | Every 8h | Every 4–8 hours |
| Breaking news | Real-time | Every 15–30 min |
| Prices | Near real-time | As needed |

---

## Pricing (Coming Soon)

| Tier | Deposit | Per Call | Access |
|------|---------|---------|--------|
| Explorer | Free | — | Real-time prices only. 50 calls/day. |
| Builder | $50 USDC | $0.005 | Prices + macro + regime + signals + news |
| Signal | $150 USDC | $0.003 | All 33 endpoints. AI reports. Orderbook. |
| Institutional | $500 USDC | $0.002 | Unlimited. White-label. SLA. |

Deposit USDC, EURC, USDT, or SOL on Base, Solana, or Ethereum. Credits never expire. No subscriptions. No KYC.

---

## Links

- **Telegram:** [t.me/AgentCanary](https://t.me/AgentCanary) — live market intelligence 3x/day
- **Website:** [agentcanary.ai](https://agentcanary.ai)

---

*AgentCanary provides market data and intelligence for informational purposes only. Nothing constitutes financial advice.*
