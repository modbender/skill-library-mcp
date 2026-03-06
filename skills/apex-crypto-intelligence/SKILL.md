---
name: APEX Crypto Intelligence — Multi-Exchange Trading Analysis Skill
description: APEX Crypto Intelligence is a multi-exchange cryptocurrency
  analysis tool that fetches live market data from CoinGecko, Binance, Bybit,
  KuCoin, MEXC, and Gate.io, performs cross-exchange arbitrage ...
---

# APEX Crypto Intelligence — Multi-Exchange Trading Analysis Skill

> Institutional-grade crypto market analysis across 5 exchanges with AI-powered Hyper-Council verdicts and hedge fund-quality PDF reports.

**Source Code**: [github.com/contrario/aetherlang](https://github.com/contrario/aetherlang/tree/main/skills/apex-crypto-intelligence)
**Homepage**: [neurodoc.app](https://neurodoc.app)
**Author**: NeuroAether (info@neurodoc.app)
**License**: MIT
**Version**: 0.1.0

## Summary

APEX Crypto Intelligence is a multi-exchange cryptocurrency analysis tool that fetches live market data from CoinGecko, Binance, Bybit, KuCoin, MEXC, and Gate.io, performs cross-exchange arbitrage detection, and provides AI-powered institutional trading analysis through a Hyper-Council of 5 specialized agents.

---

## Privacy & Data Handling

⚠️ **BYOK (Bring Your Own Keys)**: Exchange API keys are used **locally** to fetch data from exchanges. Keys are **never transmitted** to NeuroAether.

⚠️ **External API Notice**: Only market data (prices, volumes) and query text are sent to `api.neurodoc.app` for AI analysis.

**Auditable Code**: See [`client.py`](https://github.com/contrario/aetherlang/blob/main/skills/apex-crypto-intelligence/client.py) — the `build_api_request()` function on line 109 shows the **exact payload** sent to the API. Run `python client.py` to inspect the payload before sending.

- **What is sent**: Aggregated market prices and natural language queries only ([verify in client.py line 109](https://github.com/contrario/aetherlang/blob/main/skills/apex-crypto-intelligence/client.py#L109))
- **What is NOT sent**: Exchange API keys, credentials, personal data, wallet addresses
- **Data retention**: Queries are processed in real-time and not stored
- **Hosting**: Hetzner EU servers (GDPR compliant)

**CRITICAL**: Users should configure exchange API keys with **READ-ONLY permissions**. Never enable withdrawal or trading permissions.

---

## Architecture
```
User's Machine (local)              NeuroAether API
┌──────────────────────┐            ┌─────────────────┐
│                      │            │                  │
│  Exchange API Keys   │            │  api.neurodoc.app│
│  (never leave here)  │            │                  │
│         │            │            │  Receives ONLY:  │
│         ▼            │            │  - prices        │
│  Fetch from          │  prices +  │  - volumes       │
│  Binance/Bybit/etc   │──query──▶ │  - query text    │
│  (locally)           │            │                  │
│         │            │            │  Returns:        │
│         ▼            │  ◀──────── │  - AI analysis   │
│  Aggregate prices    │  analysis  │  - verdicts      │
│  (no keys in payload)│            │  - PDF data      │
│                      │            │                  │
└──────────────────────┘            └─────────────────┘
```

---

## Overview

### Key Features

1. **Cross-Exchange Scanner** — Live bid/ask from Binance, Bybit, KuCoin, MEXC, Gate.io
2. **Arbitrage Detection** — Automatic spread analysis across all 5 exchanges
3. **APEX Hyper-Council Analysis** — 5 AI agents (Macro CIO, Quant Research, Risk Officer Damocles, Execution Architect, Regime Classifier)
4. **Trading Blueprint PDF** — Hedge fund-grade reports with SWOT, Radar charts, PnL projections, Implementation Roadmap
5. **Multi-coin Support** — BTC, ETH, SOL, XRP, DOGE, ADA, DOT, AVAX, MATIC, BNB, LTC, LINK, TRX, SHIB, SUI, APT, TON, NEAR, UNI, PEPE

---

## Configuration (BYOK)

Users provide their own API keys via environment variables. All keys are optional — the skill works with CoinGecko free data by default, and each exchange is additive.

### Required Environment Variables

None required. The skill works without any keys using CoinGecko free tier.

### Optional Environment Variables

| Variable | Exchange | Purpose |
|----------|----------|---------|
| `BINANCE_API_KEY` | Binance | Market data (read-only) |
| `BINANCE_API_SECRET` | Binance | API authentication |
| `BYBIT_API_KEY` | Bybit | Market data (read-only) |
| `BYBIT_API_SECRET` | Bybit | API authentication |
| `KUCOIN_API_KEY` | KuCoin | Market data (read-only) |
| `KUCOIN_API_SECRET` | KuCoin | API authentication |
| `MEXC_API_KEY` | MEXC | Market data (read-only) |
| `MEXC_API_SECRET` | MEXC | API authentication |
| `GATEIO_API_KEY` | Gate.io | Market data (read-only) |
| `GATEIO_API_SECRET` | Gate.io | API authentication |

---

## API Endpoints

### 1. Live Market Data + Cross-Exchange Scanner
```
POST https://api.neurodoc.app/aetherlang/execute
Content-Type: application/json
```
```json
{
  "code": "flow CryptoScan {\n  using target \"neuroaether\" version \">=0.3\";\n  input text query;\n  node Scanner: crypto exchanges=\"all\", language=\"en\";\n  output text result from Scanner;\n}",
  "query": "BTC ETH SOL"
}
```

### 2. APEX Hyper-Council Analysis
```json
{
  "code": "flow ApexAnalysis {\n  using target \"neuroaether\" version \">=0.3\";\n  input text query;\n  node Apex: crypto mode=\"analysis\", language=\"en\";\n  output text result from Apex;\n}",
  "query": "Full APEX analysis for BTC ETH SOL"
}
```

### 3. Trading Blueprint PDF
```json
{
  "code": "flow Blueprint {\n  using target \"neuroaether\" version \">=0.3\";\n  input text query;\n  node Report: crypto mode=\"blueprint\", language=\"en\";\n  output text result from Report;\n}",
  "query": "Generate trading blueprint for BTC"
}
```

---

## Supported Exchanges

| Exchange | Data Available | Auth Required |
|----------|---------------|---------------|
| CoinGecko | Price, MCap, Volume, ATH | No (free tier) |
| Binance | Bid/Ask, Spread, Volume | Optional |
| Bybit | Bid/Ask, Spread, Volume | Optional |
| KuCoin | Bid/Ask, Spread | Optional |
| MEXC | Bid/Ask, Spread, Volume | Optional |
| Gate.io | Bid/Ask, Spread, Volume | Optional |

---

## Hyper-Council Agents

| Agent | Role | Weight Range | Can Veto |
|-------|------|-------------|----------|
| MACRO | Global Macro CIO | -100 to +100 | No |
| QUANT | Head of Quant Research | -100 to +100 | No |
| STATS | Chief Statistician | -100 to +100 | No |
| RISK (Damocles) | Chief Risk Officer | -100 to +100 | **Yes** |
| EXECUTION | Execution Architect | 0 (INFO) | No |

---

## Security Architecture

**Auditable source**: [`client.py`](https://github.com/contrario/aetherlang/blob/main/skills/apex-crypto-intelligence/client.py) — inspect `build_api_request()` to verify exact payload.

- **BYOK**: User keys stay local, never transmitted to NeuroAether
- **Read-only**: Skill only reads market data, never executes trades
- **No storage**: API keys used per-request, never persisted
- **Input validation**: All queries sanitized, max 5000 chars
- **Rate limiting**: 100 req/hour free tier

### What This Skill Does NOT Do
- ❌ Execute trades or place orders
- ❌ Transfer funds or make withdrawals
- ❌ Store or log API keys
- ❌ Provide financial advice (analysis only)

---

## Languages

- **English** (default)
- **Greek** (Ελληνικά) — add `language="el"`

## Technology

- **Backend**: FastAPI + Python 3.12 ([source](https://github.com/contrario/aetherlang))
- **AI Models**: GPT-4o via OpenAI
- **Data Sources**: CoinGecko, Binance, Bybit, KuCoin, MEXC, Gate.io
- **PDF Engine**: WeasyPrint + Matplotlib
- **Hosting**: Hetzner EU (GDPR compliant)

---

## Disclaimer

⚠️ This skill provides AI-generated market analysis for educational and informational purposes only. It is NOT financial advice. Cryptocurrency trading involves significant risk. Always conduct your own research and consult a qualified financial advisor before making investment decisions.

---
*Built by NeuroAether — Institutional Intelligence for Everyone* 🧠📊
