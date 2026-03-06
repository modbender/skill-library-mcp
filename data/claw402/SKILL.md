---
name: claw402
description: >
  Professional market data and AI APIs via x402 micropayments — no API key,
  no signup, no subscription. Pay per call with USDC on Base. 200+ endpoints
  across 9 provider groups: crypto market data (fund flow, liquidations, OI,
  funding rates, whale tracking, ETF flows, AI signals), US stocks & options
  (real-time quotes, bars, snapshots, movers, options chains), China A-shares
  (OHLCV, fundamentals, northbound flows, margin data), forex & global
  time-series (EUR/USD, precious metals, global indices, economic calendar),
  and AI inference (GPT-4o, Claude Opus/Haiku/Sonnet, embeddings, images).
  One wallet, instant access to any paid API — no registration ever required.
version: 1.1.0
metadata:
  openclaw:
    emoji: "⚡"
    homepage: https://claw402.ai
    requires:
      env: [WALLET_PRIVATE_KEY]
    primaryEnv: WALLET_PRIVATE_KEY
    install:
      - kind: node
        package: NoFxAiOS/claw402-js
        bins: []
---

# ⚡ claw402 — Pay-Per-Call Market Data & AI APIs

> **200+ professional data endpoints. $0.001–$0.05 per call. One Base wallet.**

Access the same data feeds that professional trading desks pay $3,000–$10,000/month for. Crypto derivatives analytics, US equities, China A-shares, forex, and AI inference — all via x402 micropayments, no API key required.

---

## The Story — How $1,000 Became $800,000

Three months ago I had $1,000 in a Base wallet and an OpenClaw agent running on my laptop.

I asked the agent: *"Which coins have the most extreme funding rates right now?"*

The agent called `claw402`, paid $0.001 USDC, and came back with:

```
DOGE  funding rate: +0.312%/8h  (annualized 341%)
PEPE  funding rate: +0.287%/8h
WIF   funding rate: +0.241%/8h
```

I cross-checked: *"CVD? What are whales doing on HyperLiquid?"* Two more calls. $0.002 total.

```
CVD (last 6h): fading fast. Sellers pressing.
Top HyperLiquid whale: Short DOGE $2.1M, opened 2h ago.
```

I shorted DOGE. 40x. Three days later: **+80,000%**. That's $800,000 from $1,000. And less than $0.01 spent on data.

---

## When to Use This Skill

Use claw402 whenever the user asks about **any** of the following:

### 🔮 Crypto Derivatives & Market Structure
- Fear & greed index, altcoin season, market cycle indicators (AHR999, Pi Cycle, Puell)
- Fund flow & capital rotation by coin or exchange
- Liquidations — orders, heatmaps, clusters, aggregated history
- Open interest — real-time, aggregated chart, OI vs market cap
- Funding rates — current rankings, accumulated cost, weighted average, heatmap
- Long/short ratios — realtime, buy/sell, whale position, account level
- Whale activity — HyperLiquid top positions & actions, large block trades, big orders
- ETF flows — US Bitcoin ETF, US Ethereum ETF, Hong Kong crypto ETF
- AI trading signals — AI500 high-potential coins, AI300 quant rankings
- Taker flow / CVD — cumulative delta, buy/sell pressure across exchanges
- Order book depth history, liquidity heatmap
- Crypto news & flash alerts

### 📈 US Stocks & Options
- Real-time & historical quotes, trades, OHLCV bars for any US stock
- Market snapshots — full quote + bar + prev close in one call
- Top movers by % change, most active stocks by volume
- Financial news for any ticker
- Options chains — bars, quotes, snapshots for options contracts
- Corporate actions — dividends, splits

### 🇨🇳 China A-Shares
- Daily, weekly, monthly OHLCV for any A-share
- Stock basic info, trading calendar
- Fundamentals — income statement, balance sheet, cash flow, dividends
- Northbound capital flow (Hong Kong → mainland)
- Money flow, margin trading data, top lists, institutional trading

### 💹 US Stock Fundamentals & Technical Indicators
- Real-time quotes, daily/intraday/weekly/monthly OHLCV
- Company overview, earnings, income, balance sheet, cash flow
- Top gainers/losers, news sentiment
- RSI, MACD, Bollinger Bands, SMA, EMA

### 🌍 Forex, Metals & Global Time-Series
- EUR/USD, GBP/USD and any forex pair — tick or time-series
- Precious metals price and history — XAU/USD (gold), XAG/USD (silver)
- Global indices — list and real-time quotes
- Exchange rates, forex pairs reference, economic calendar
- Technical indicators — RSI, MACD, SMA, EMA, Bollinger Bands, ATR

### 🤖 AI Inference (GPT-4o, Claude, Embeddings, Images)
- OpenAI GPT-4o chat, GPT-4o-mini, embeddings (small + large), DALL-E images
- Anthropic Claude messages (standard, Haiku, Opus)
- Use to analyze market data your agent just fetched — chain calls in one session

---

## Cost & Privacy

| Item | Detail |
|------|--------|
| Crypto / stock data | **$0.001–$0.003 USDC** per call |
| Twelvedata complex POST | **$0.005 USDC** per call |
| OpenAI GPT-4o chat | **$0.01 USDC** per call |
| OpenAI mini / embeddings | **$0.001–$0.005 USDC** per call |
| Claude messages | **$0.01–$0.015 USDC** per call |
| Payment chain | Base mainnet (Coinbase L2) |
| Payment method | EIP-3009 USDC transfer, signed locally |
| Key security | Private key **never transmitted** — signs locally only |
| API key required | **No** — wallet is your credential |
| Registration | **Never** |

Get USDC on Base: [bridge.base.org](https://bridge.base.org) · Testnet USDC: [faucet.circle.com](https://faucet.circle.com)

---

## Quick Start

### 1. Set your wallet key
```
WALLET_PRIVATE_KEY=0xYourBaseWalletPrivateKey
```
Your wallet must hold USDC on **Base mainnet**.

### 2. Query any GET endpoint
```bash
node scripts/query.mjs <endpoint-path> [key=value ...]
```

### 3. Call POST endpoints (AI / Twelvedata complex)
```bash
node scripts/query.mjs <endpoint-path> --post '<json-body>'
```

### 4. Read the result
The script prints `{ status, url, data }` as formatted JSON. Parse `data` for the actual payload.

---

## Query Examples

### Crypto Market Data

```bash
# --- Market Cycle & Sentiment ---
node scripts/query.mjs /api/v1/coinank/indicator/fear-greed
node scripts/query.mjs /api/v1/coinank/indicator/altcoin-season
node scripts/query.mjs /api/v1/coinank/indicator/btc-multiplier
node scripts/query.mjs /api/v1/coinank/indicator/ahr999

# --- Fund Flow ---
node scripts/query.mjs /api/v1/nofx/netflow/top-ranking limit=20 duration=1h
node scripts/query.mjs /api/v1/coinank/fund/realtime sortBy=h1net productType=SWAP

# --- Liquidations ---
node scripts/query.mjs /api/v1/coinank/liquidation/orders baseCoin=BTC
node scripts/query.mjs /api/v1/coinank/liquidation/liq-map symbol=BTCUSDT exchange=Binance interval=1d

# --- Open Interest ---
node scripts/query.mjs /api/v1/coinank/oi/all baseCoin=BTC
node scripts/query.mjs /api/v1/nofx/oi/top-ranking limit=20 duration=1h

# --- Funding Rates ---
node scripts/query.mjs /api/v1/coinank/funding-rate/current type=current
node scripts/query.mjs /api/v1/nofx/funding-rate/top limit=20

# --- Whale Tracking ---
node scripts/query.mjs /api/v1/coinank/hyper/top-position sortBy=pnl sortType=desc
node scripts/query.mjs /api/v1/coinank/hyper/top-action

# --- ETF Flows ---
node scripts/query.mjs /api/v1/coinank/etf/us-btc-inflow
node scripts/query.mjs /api/v1/coinank/etf/us-eth-inflow

# --- AI Signals ---
node scripts/query.mjs /api/v1/nofx/ai500/list limit=20
node scripts/query.mjs /api/v1/nofx/ai300/list limit=20

# --- CVD / Taker Flow ---
node scripts/query.mjs /api/v1/coinank/market-order/agg-cvd exchanges= symbol=BTCUSDT interval=1h size=24

# --- Price & Candles ---
node scripts/query.mjs /api/v1/coinank/price/last symbol=BTCUSDT exchange=Binance productType=SWAP
node scripts/query.mjs /api/v1/coinank/kline/lists symbol=BTCUSDT exchange=Binance interval=1h size=100

# --- News ---
node scripts/query.mjs /api/v1/coinank/news/list type=2 lang=en page=1 pageSize=10
```

### US Stocks — Alpaca

```bash
# Real-time quote
node scripts/query.mjs /api/v1/alpaca/quotes/latest symbols=AAPL,TSLA,MSFT

# Historical bars
node scripts/query.mjs /api/v1/alpaca/bars symbols=AAPL timeframe=1Day start=2024-01-01 limit=30

# Market snapshot (quote + bar + prev close)
node scripts/query.mjs /api/v1/alpaca/snapshots symbols=AAPL,TSLA

# Top movers
node scripts/query.mjs /api/v1/alpaca/movers top=10 market_type=stocks

# Most active stocks
node scripts/query.mjs /api/v1/alpaca/most-actives top=10

# Latest trade
node scripts/query.mjs /api/v1/alpaca/trades/latest symbols=AAPL

# Financial news
node scripts/query.mjs /api/v1/alpaca/news symbols=AAPL limit=10

# Options chain snapshot
node scripts/query.mjs /api/v1/alpaca/options/snapshots symbols=AAPL240119C00150000
```

### US Stocks — Polygon

```bash
# OHLCV bars
node scripts/query.mjs /api/v1/polygon/aggs/ticker stocks_ticker=AAPL multiplier=1 timespan=day from=2024-01-01 to=2024-01-31

# Previous close
node scripts/query.mjs /api/v1/polygon/prev-close stocks_ticker=AAPL

# Snapshot (full quote + bar)
node scripts/query.mjs /api/v1/polygon/snapshot/ticker stocks_ticker=AAPL

# Top gainers/losers
node scripts/query.mjs /api/v1/polygon/snapshot/gainers
node scripts/query.mjs /api/v1/polygon/snapshot/losers

# Company details
node scripts/query.mjs /api/v1/polygon/ticker-details ticker=AAPL

# Market status
node scripts/query.mjs /api/v1/polygon/market-status

# Technical indicators
node scripts/query.mjs /api/v1/polygon/rsi stock_ticker=AAPL timespan=day window=14
node scripts/query.mjs /api/v1/polygon/macd stocks_ticker=AAPL timespan=day

# Options chain
node scripts/query.mjs /api/v1/polygon/options/snapshot underlying_asset=AAPL

# News
node scripts/query.mjs /api/v1/polygon/ticker-news ticker=AAPL
```

### US Stocks — Alpha Vantage Fundamentals

```bash
# Real-time quote
node scripts/query.mjs /api/v1/stocks/us/quote symbol=AAPL

# Daily OHLCV
node scripts/query.mjs /api/v1/stocks/us/daily symbol=AAPL outputsize=compact

# Intraday
node scripts/query.mjs /api/v1/stocks/us/intraday symbol=AAPL interval=5min

# Company overview
node scripts/query.mjs /api/v1/stocks/us/overview symbol=AAPL

# Earnings history
node scripts/query.mjs /api/v1/stocks/us/earnings symbol=AAPL

# Financial statements
node scripts/query.mjs /api/v1/stocks/us/income symbol=AAPL
node scripts/query.mjs /api/v1/stocks/us/balance-sheet symbol=AAPL
node scripts/query.mjs /api/v1/stocks/us/cash-flow symbol=AAPL

# Top gainers/losers/most active
node scripts/query.mjs /api/v1/stocks/us/movers

# News & sentiment
node scripts/query.mjs /api/v1/stocks/us/news tickers=AAPL

# Technical indicators
node scripts/query.mjs /api/v1/stocks/us/rsi symbol=AAPL interval=daily time_period=14
node scripts/query.mjs /api/v1/stocks/us/macd symbol=AAPL interval=daily
node scripts/query.mjs /api/v1/stocks/us/bbands symbol=AAPL interval=daily time_period=20
```

### China A-Shares — Tushare

```bash
# Stock list (all listed stocks)
node scripts/query.mjs /api/v1/stocks/cn/stock-basic list_status=L

# Daily OHLCV
node scripts/query.mjs /api/v1/stocks/cn/daily ts_code=000001.SZ start_date=20240101 end_date=20240131

# Trading calendar
node scripts/query.mjs /api/v1/stocks/cn/trade-cal start_date=20240101 end_date=20240131

# Northbound capital flow
node scripts/query.mjs /api/v1/stocks/cn/northbound trade_date=20240315

# Money flow
node scripts/query.mjs /api/v1/stocks/cn/moneyflow ts_code=000001.SZ start_date=20240101

# Margin trading data
node scripts/query.mjs /api/v1/stocks/cn/margin ts_code=000001.SZ start_date=20240101

# Top list (dragon tiger list)
node scripts/query.mjs /api/v1/stocks/cn/top-list trade_date=20240315

# Fundamentals
node scripts/query.mjs /api/v1/stocks/cn/income ts_code=000001.SZ period=20231231
node scripts/query.mjs /api/v1/stocks/cn/balance-sheet ts_code=000001.SZ period=20231231
```

### Forex & Global Time-Series — Twelve Data

```bash
# Time series — EUR/USD hourly
node scripts/query.mjs /api/v1/twelvedata/time-series symbol=EUR/USD interval=1h outputsize=50

# Real-time price
node scripts/query.mjs /api/v1/twelvedata/price symbol=BTC/USD
node scripts/query.mjs /api/v1/twelvedata/price symbol=XAU/USD

# Exchange rate
node scripts/query.mjs /api/v1/twelvedata/exchange-rate symbol=USD/JPY

# Technical indicators
node scripts/query.mjs /api/v1/twelvedata/indicator/rsi symbol=AAPL interval=1day time_period=14 outputsize=10
node scripts/query.mjs /api/v1/twelvedata/indicator/macd symbol=EUR/USD interval=1h
node scripts/query.mjs /api/v1/twelvedata/indicator/bbands symbol=AAPL interval=1day

# Precious metals
node scripts/query.mjs /api/v1/twelvedata/metals/price symbol=XAU/USD
node scripts/query.mjs /api/v1/twelvedata/metals/time-series symbol=XAU/USD interval=1day

# Global indices
node scripts/query.mjs /api/v1/twelvedata/indices/list
node scripts/query.mjs /api/v1/twelvedata/indices/quote symbol=SPX

# Economic calendar
node scripts/query.mjs /api/v1/twelvedata/economic-calendar

# Available forex pairs
node scripts/query.mjs /api/v1/twelvedata/forex-pairs
```

### AI Inference — OpenAI & Anthropic (POST)

```bash
# GPT-4o chat
node scripts/query.mjs /api/v1/ai/openai/chat --post '{"model":"gpt-4o","messages":[{"role":"user","content":"Analyze: BTC funding rate is extreme positive, CVD fading, whale just shorted. What does this mean?"}]}'

# GPT-4o-mini (cheaper)
node scripts/query.mjs /api/v1/ai/openai/chat/mini --post '{"messages":[{"role":"user","content":"Summarize AAPL earnings in 3 bullet points."}]}'

# Embeddings
node scripts/query.mjs /api/v1/ai/openai/embeddings --post '{"input":"crypto market sentiment","model":"text-embedding-3-small"}'

# List available OpenAI models
node scripts/query.mjs /api/v1/ai/openai/models

# Claude Sonnet (standard, balanced)
node scripts/query.mjs /api/v1/ai/anthropic/messages --post '{"model":"claude-sonnet-4-6","max_tokens":1024,"messages":[{"role":"user","content":"What trading setup does extreme funding + CVD divergence suggest?"}]}'

# Claude Haiku (fast, cheap)
node scripts/query.mjs /api/v1/ai/anthropic/messages/haiku --post '{"max_tokens":256,"messages":[{"role":"user","content":"One-sentence summary of BTC ETF flows today."}]}'

# Claude Opus (deepest reasoning)
node scripts/query.mjs /api/v1/ai/anthropic/messages/opus --post '{"max_tokens":2048,"messages":[{"role":"user","content":"Full macro analysis: ETF inflows strong, funding extreme, CVD diverging..."}]}'
```

**Always** run the command, then format the `data` field clearly for the user — tables, bullet points, or a brief narrative summary.

---

## Power Pattern: Chain Multiple Calls

The real power of claw402 is combining data sources in one agent session:

```bash
# Step 1: Find crowded trades ($0.001)
node scripts/query.mjs /api/v1/nofx/funding-rate/top limit=20

# Step 2: Confirm with CVD ($0.001)
node scripts/query.mjs /api/v1/coinank/market-order/agg-cvd exchanges= symbol=DOGEUSDT interval=1h size=6

# Step 3: Check whale positioning ($0.001)
node scripts/query.mjs /api/v1/coinank/hyper/top-position sortBy=value sortType=desc

# Step 4: Cross-reference with US macro ($0.001)
node scripts/query.mjs /api/v1/alpaca/movers top=10 market_type=stocks

# Step 5: Let AI synthesize the analysis ($0.010)
node scripts/query.mjs /api/v1/ai/anthropic/messages/haiku --post '{"max_tokens":512,"messages":[{"role":"user","content":"[paste data from steps 1-4] — what is the high-conviction trade?"}]}'
```

**Total cost: ~$0.014 USDC.** Bloomberg Terminal equivalent: $2,000/month.

---

## Natural Language → Command Mapping

### Crypto

| User says | Command |
|-----------|---------|
| "Fear & greed index?" | `/api/v1/coinank/indicator/fear-greed` |
| "Altcoin season?" | `/api/v1/coinank/indicator/altcoin-season` |
| "Bitcoin cycle position?" | `/api/v1/coinank/indicator/btc-multiplier`, `ahr999` |
| "Which coins have extreme funding rates?" | `/api/v1/coinank/funding-rate/current type=current` |
| "Most negative funding rates?" | `/api/v1/nofx/funding-rate/low limit=20` |
| "Which coins have the most capital inflows?" | `/api/v1/nofx/netflow/top-ranking limit=20 duration=1h` |
| "Fund flow for BTC?" | `/api/v1/coinank/fund/realtime sortBy=h1net productType=SWAP` |
| "Recent large liquidations?" | `/api/v1/coinank/liquidation/orders baseCoin=BTC` |
| "BTC liquidation map / price clusters?" | `/api/v1/coinank/liquidation/liq-map symbol=BTCUSDT exchange=Binance interval=1d` |
| "BTC open interest?" | `/api/v1/coinank/oi/all baseCoin=BTC` |
| "Biggest OI increases?" | `/api/v1/nofx/oi/top-ranking limit=20 duration=1h` |
| "BTC long/short ratio?" | `/api/v1/coinank/longshort/realtime baseCoin=BTC interval=1h` |
| "Whale positions on HyperLiquid?" | `/api/v1/coinank/hyper/top-position sortBy=pnl sortType=desc` |
| "Recent whale trades?" | `/api/v1/coinank/hyper/top-action` |
| "Bitcoin ETF inflows today?" | `/api/v1/coinank/etf/us-btc-inflow` |
| "Ethereum ETF flows?" | `/api/v1/coinank/etf/us-eth-inflow` |
| "Top AI-picked coins?" | `/api/v1/nofx/ai500/list limit=20` |
| "CVD for BTC?" | `/api/v1/coinank/market-order/agg-cvd exchanges= symbol=BTCUSDT interval=1h size=24` |
| "Is buying pressure real?" | `/api/v1/coinank/market-order/agg-cvd` |
| "BTC price?" | `/api/v1/coinank/price/last symbol=BTCUSDT exchange=Binance productType=SWAP` |
| "Top gainers today?" | `/api/v1/nofx/price/ranking duration=24h` |
| "Trending on Upbit?" | `/api/v1/nofx/upbit/hot limit=20` |
| "Latest crypto news?" | `/api/v1/coinank/news/list type=2 lang=en page=1 pageSize=10` |

### US Stocks

| User says | Command |
|-----------|---------|
| "AAPL stock price right now?" | `/api/v1/alpaca/quotes/latest symbols=AAPL` |
| "AAPL daily chart last month?" | `/api/v1/alpaca/bars symbols=AAPL timeframe=1Day start=2024-01-01` |
| "Full AAPL snapshot?" | `/api/v1/alpaca/snapshots symbols=AAPL` |
| "Top movers today?" | `/api/v1/alpaca/movers top=10 market_type=stocks` |
| "Most traded stocks?" | `/api/v1/alpaca/most-actives top=10` |
| "AAPL OHLCV bars (Polygon)?" | `/api/v1/polygon/aggs/ticker stocks_ticker=AAPL multiplier=1 timespan=day from=... to=...` |
| "Market open today?" | `/api/v1/polygon/market-status` |
| "AAPL RSI?" | `/api/v1/polygon/rsi stock_ticker=AAPL timespan=day window=14` |
| "AAPL options chain?" | `/api/v1/polygon/options/snapshot underlying_asset=AAPL` |
| "AAPL stock overview/fundamentals?" | `/api/v1/stocks/us/overview symbol=AAPL` |
| "AAPL earnings history?" | `/api/v1/stocks/us/earnings symbol=AAPL` |
| "AAPL income statement?" | `/api/v1/stocks/us/income symbol=AAPL` |
| "AAPL MACD?" | `/api/v1/stocks/us/macd symbol=AAPL interval=daily` |
| "Top gainers/losers today?" | `/api/v1/stocks/us/movers` |
| "AAPL news sentiment?" | `/api/v1/stocks/us/news tickers=AAPL` |

### China A-Shares

| User says | Command |
|-----------|---------|
| "List all A-share stocks?" | `/api/v1/stocks/cn/stock-basic list_status=L` |
| "000001.SZ daily chart?" | `/api/v1/stocks/cn/daily ts_code=000001.SZ start_date=20240101 end_date=20240131` |
| "Trading calendar for January?" | `/api/v1/stocks/cn/trade-cal start_date=20240101 end_date=20240131` |
| "Northbound flows today?" | `/api/v1/stocks/cn/northbound trade_date=20240315` |
| "Money flow for 000001?" | `/api/v1/stocks/cn/moneyflow ts_code=000001.SZ start_date=20240101` |
| "Dragon tiger list?" | `/api/v1/stocks/cn/top-list trade_date=20240315` |
| "Margin data?" | `/api/v1/stocks/cn/margin ts_code=000001.SZ start_date=20240101` |

### Forex & Global

| User says | Command |
|-----------|---------|
| "EUR/USD rate?" | `/api/v1/twelvedata/price symbol=EUR/USD` |
| "EUR/USD hourly chart?" | `/api/v1/twelvedata/time-series symbol=EUR/USD interval=1h outputsize=50` |
| "Gold price?" | `/api/v1/twelvedata/metals/price symbol=XAU/USD` |
| "Gold daily chart?" | `/api/v1/twelvedata/metals/time-series symbol=XAU/USD interval=1day` |
| "S&P 500 index level?" | `/api/v1/twelvedata/indices/quote symbol=SPX` |
| "What global indices are available?" | `/api/v1/twelvedata/indices/list` |
| "Economic calendar this week?" | `/api/v1/twelvedata/economic-calendar` |
| "EUR/USD RSI?" | `/api/v1/twelvedata/indicator/rsi symbol=EUR/USD interval=1h time_period=14` |
| "Available forex pairs?" | `/api/v1/twelvedata/forex-pairs` |

### AI Inference

| User says | Command |
|-----------|---------|
| "Analyze this market data with AI" | `POST /api/v1/ai/openai/chat` with `gpt-4o` |
| "Quick AI summary (cheap)" | `POST /api/v1/ai/openai/chat/mini` or `POST /api/v1/ai/anthropic/messages/haiku` |
| "Deep AI analysis" | `POST /api/v1/ai/anthropic/messages/opus` |
| "Embed this text" | `POST /api/v1/ai/openai/embeddings` |
| "Generate an image" | `POST /api/v1/ai/openai/images` |
| "List OpenAI models" | `/api/v1/ai/openai/models` |

---

## Complete Endpoint Reference

### 🤖 AI Trading Signals (Nofxos) — $0.001/call

| Endpoint | Description | Key Params |
|----------|-------------|------------|
| `/api/v1/nofx/ai500/list` | AI500 high-potential coins (score > 70) | `limit` |
| `/api/v1/nofx/ai500/stats` | AI500 index statistics | — |
| `/api/v1/nofx/ai300/list` | AI300 quant model rankings | `limit` |
| `/api/v1/nofx/ai300/stats` | AI300 statistics | — |
| `/api/v1/nofx/netflow/top-ranking` | Top net capital inflow coins | `limit`, `duration`, `type` |
| `/api/v1/nofx/netflow/low-ranking` | Top net capital outflow coins | `limit`, `duration`, `type` |
| `/api/v1/nofx/oi/top-ranking` | Biggest OI increase coins | `limit`, `duration` |
| `/api/v1/nofx/oi/low-ranking` | Biggest OI decrease coins | `limit`, `duration` |
| `/api/v1/nofx/price/ranking` | Price change rankings | `duration` |
| `/api/v1/nofx/funding-rate/top` | Highest funding rate coins | `limit` |
| `/api/v1/nofx/funding-rate/low` | Most negative funding rate coins | `limit` |
| `/api/v1/nofx/upbit/hot` | Upbit hot coins by volume | `limit` |
| `/api/v1/nofx/upbit/netflow/top-ranking` | Upbit net inflow rankings | `limit`, `duration` |
| `/api/v1/nofx/upbit/netflow/low-ranking` | Upbit net outflow rankings | `limit`, `duration` |
| `/api/v1/nofx/query-rank/list` | Most searched coin rankings | `limit` |

**`duration` values:** `5m` `15m` `1h` `4h` `24h`

---

### 📈 Crypto Market Data (Coinank) — $0.001–$0.003/call

#### Price & Candlesticks
| Endpoint | Description | Key Params |
|----------|-------------|------------|
| `/api/v1/coinank/price/last` | Real-time latest price | `symbol`, `exchange`, `productType` |
| `/api/v1/coinank/kline/lists` | OHLCV candlestick data | `symbol`, `exchange`, `interval`, `size`, `endTime` |

#### ETF Flows
| Endpoint | Description |
|----------|-------------|
| `/api/v1/coinank/etf/us-btc` | US Bitcoin ETF list (IBIT, FBTC, ARKB, etc.) |
| `/api/v1/coinank/etf/us-eth` | US Ethereum ETF list |
| `/api/v1/coinank/etf/us-btc-inflow` | US BTC ETF historical net inflow |
| `/api/v1/coinank/etf/us-eth-inflow` | US ETH ETF historical net inflow |
| `/api/v1/coinank/etf/hk-inflow` | Hong Kong crypto ETF net inflow |

#### Fund Flow
| Endpoint | Description | Key Params |
|----------|-------------|------------|
| `/api/v1/coinank/fund/realtime` | Real-time fund flow rankings | `sortBy` (h1net/h4net/h24net), `productType`, `size` |
| `/api/v1/coinank/fund/history` | Historical fund flow by coin | `baseCoin`, `interval`, `size`, `endTime` |

#### Open Interest
| Endpoint | Description | Key Params |
|----------|-------------|------------|
| `/api/v1/coinank/oi/all` | Real-time OI by exchange | `baseCoin` |
| `/api/v1/coinank/oi/agg-chart` | Aggregated OI history | `baseCoin`, `exchange`, `interval`, `size`, `endTime` |
| `/api/v1/coinank/oi/symbol-chart` | OI history by trading pair | `exchange`, `symbol`, `interval`, `size`, `endTime` |
| `/api/v1/coinank/oi/kline` | OI candlestick | `exchange`, `symbol`, `interval`, `size`, `endTime` |
| `/api/v1/coinank/oi/vs-market-cap-hist` | OI / market cap ratio history | `baseCoin`, `interval`, `size`, `endTime` |

#### Liquidations
| Endpoint | Description | Key Params |
|----------|-------------|------------|
| `/api/v1/coinank/liquidation/orders` | Recent liquidation orders | `baseCoin`, `exchange`, `side`, `amount`, `endTime` |
| `/api/v1/coinank/liquidation/intervals` | Liquidation stats by period | `baseCoin` |
| `/api/v1/coinank/liquidation/agg-history` | Aggregated liquidation history | `baseCoin`, `interval`, `size`, `endTime` |
| `/api/v1/coinank/liquidation/liq-map` | Liquidation price-level clusters | `symbol`, `exchange`, `interval` |
| `/api/v1/coinank/liquidation/heat-map` | Liquidation heatmap | `exchange`, `symbol`, `interval` |

#### Long/Short Ratios
| Endpoint | Description | Key Params |
|----------|-------------|------------|
| `/api/v1/coinank/longshort/realtime` | Real-time L/S ratio by exchange | `baseCoin`, `interval` |
| `/api/v1/coinank/longshort/buy-sell` | Global buy-sell L/S history | `baseCoin`, `interval`, `size`, `endTime` |
| `/api/v1/coinank/longshort/person` | Account-level L/S ratio | `exchange`, `symbol`, `interval`, `size`, `endTime` |
| `/api/v1/coinank/longshort/position` | Whale position-level L/S | `exchange`, `symbol`, `interval`, `size`, `endTime` |

#### Funding Rates
| Endpoint | Description | Key Params |
|----------|-------------|------------|
| `/api/v1/coinank/funding-rate/current` | Real-time funding rate rankings | `type` (current/day/week/month/year) |
| `/api/v1/coinank/funding-rate/accumulated` | Accumulated funding cost | `type` |
| `/api/v1/coinank/funding-rate/hist` | Historical funding rates | `baseCoin`, `exchangeType`, `size`, `endTime` |
| `/api/v1/coinank/funding-rate/weighted` | Weighted average funding rate | `baseCoin`, `interval`, `size`, `endTime` |
| `/api/v1/coinank/funding-rate/heatmap` | Funding rate heatmap | `type` (openInterest/marketCap), `interval` |

#### Whale Activity
| Endpoint | Description | Key Params |
|----------|-------------|------------|
| `/api/v1/coinank/hyper/top-position` | HyperLiquid whale positions | `sortBy`, `sortType`, `page`, `size` |
| `/api/v1/coinank/hyper/top-action` | HyperLiquid whale trade actions | — |
| `/api/v1/coinank/trades/large` | Large block trades | `symbol`, `productType`, `amount`, `size`, `endTime` |
| `/api/v1/coinank/big-order/list` | Large limit orders | `symbol`, `exchangeType`, `size`, `amount`, `side` |

#### Taker Flow / CVD
| Endpoint | Description | Key Params |
|----------|-------------|------------|
| `/api/v1/coinank/market-order/cvd` | CVD for single pair | `exchange`, `symbol`, `interval`, `size`, `endTime` |
| `/api/v1/coinank/market-order/agg-cvd` | Aggregated CVD cross-exchange | `exchanges` (empty=all), `symbol`, `interval`, `size`, `endTime` |
| `/api/v1/coinank/market-order/buy-sell-value` | Taker buy/sell value USD | `exchange`, `symbol`, `interval`, `size`, `endTime` |
| `/api/v1/coinank/market-order/agg-buy-sell-value` | Aggregated buy/sell value | `exchanges`, `symbol`, `interval`, `size`, `endTime` |

#### Rankings & Screeners
| Endpoint | Description | Key Params |
|----------|-------------|------------|
| `/api/v1/coinank/rank/screener` | Multi-dimensional screener | `interval` |
| `/api/v1/coinank/rank/oi` | OI rankings | `sortBy`, `sortType`, `size` |
| `/api/v1/coinank/rank/liquidation` | Liquidation rankings | `sortBy`, `sortType`, `size` |
| `/api/v1/coinank/rank/volume` | Volume rankings | `sortBy`, `sortType` |
| `/api/v1/coinank/rank/price` | Price change rankings | `sortBy`, `sortType` |
| `/api/v1/coinank/rsi/list` | RSI screener | `interval` (1H/4H/1D — uppercase) |

#### Market Cycle Indicators
| Endpoint | Description |
|----------|-------------|
| `/api/v1/coinank/indicator/fear-greed` | Crypto fear & greed index |
| `/api/v1/coinank/indicator/altcoin-season` | Altcoin Season Index |
| `/api/v1/coinank/indicator/btc-multiplier` | BTC 2-year MA multiplier |
| `/api/v1/coinank/indicator/ahr999` | AHR999 accumulation indicator |
| `/api/v1/coinank/indicator/puell-multiple` | Puell Multiple |
| `/api/v1/coinank/indicator/ma-heatmap` | 200-week MA heatmap |
| `/api/v1/coinank/indicator/market-cap-rank` | Coin market cap share |

#### News
| Endpoint | Description | Key Params |
|----------|-------------|------------|
| `/api/v1/coinank/news/list` | News & flash alerts | `type` (1=flash, 2=news), `lang` (zh/en), `page`, `pageSize` |
| `/api/v1/coinank/news/detail` | Full article by ID | `id` |

---

### 📊 US Stocks — Alpaca Markets — $0.001–$0.003/call

| Endpoint | Description | Key Params |
|----------|-------------|------------|
| `/api/v1/alpaca/quotes/latest` | Real-time quotes | `symbols`, `feed`, `currency` |
| `/api/v1/alpaca/quotes/history` | Historical tick quotes | `symbols`, `start`, `end`, `limit`, `feed` |
| `/api/v1/alpaca/bars/latest` | Latest OHLCV bar | `symbols`, `feed`, `currency` |
| `/api/v1/alpaca/bars` | Historical OHLCV bars | `symbols`, `timeframe`, `start`, `end`, `limit`, `adjustment` |
| `/api/v1/alpaca/trades/latest` | Real-time latest trade | `symbols`, `feed` |
| `/api/v1/alpaca/trades/history` | Historical trades | `symbols`, `start`, `end`, `limit`, `feed` |
| `/api/v1/alpaca/snapshots` | Full snapshot (multi-symbol) | `symbols`, `feed` |
| `/api/v1/alpaca/snapshot` | Full snapshot (single symbol) | `symbols`, `feed` |
| `/api/v1/alpaca/movers` | Top movers by % change | `top`, `market_type` |
| `/api/v1/alpaca/most-actives` | Most active by volume | `top`, `market_type` |
| `/api/v1/alpaca/news` | Financial news | `symbols`, `start`, `end`, `limit` |
| `/api/v1/alpaca/corporate-actions` | Dividends, splits, etc. | `symbols`, `types`, `start`, `end` |
| `/api/v1/alpaca/options/bars` | Options OHLCV bars | `symbols`, `timeframe`, `start`, `end` |
| `/api/v1/alpaca/options/quotes/latest` | Options latest quotes | `symbols`, `feed` |
| `/api/v1/alpaca/options/snapshots` | Options chain snapshots | `symbols`, `feed` |

**`timeframe` values:** `1Min` `5Min` `15Min` `1Hour` `1Day`
**`market_type` values:** `stocks` `crypto`

---

### 📉 US Stocks — Polygon — $0.001–$0.003/call

| Endpoint | Description | Key Params |
|----------|-------------|------------|
| `/api/v1/polygon/aggs/ticker` | OHLCV bars | `stocks_ticker`, `multiplier`, `timespan`, `from`, `to` |
| `/api/v1/polygon/aggs/grouped` | Grouped daily bars | `date`, `adjusted` |
| `/api/v1/polygon/prev-close` | Previous session close | `stocks_ticker` |
| `/api/v1/polygon/snapshot/ticker` | Full ticker snapshot | `stocks_ticker` |
| `/api/v1/polygon/snapshot/all` | All tickers snapshot | `tickers` |
| `/api/v1/polygon/snapshot/gainers` | Top daily gainers | — |
| `/api/v1/polygon/snapshot/losers` | Top daily losers | — |
| `/api/v1/polygon/trades` | Recent trades | `stocks_ticker` |
| `/api/v1/polygon/last-trade` | Last trade | `stocks_ticker` |
| `/api/v1/polygon/quotes` | Recent quotes | `stocks_ticker` |
| `/api/v1/polygon/last-quote` | Last NBBO quote | `stocks_ticker` |
| `/api/v1/polygon/ticker-details` | Company details | `ticker` |
| `/api/v1/polygon/ticker-news` | Company news | `ticker` |
| `/api/v1/polygon/tickers` | Ticker search | `ticker`, `type`, `market` |
| `/api/v1/polygon/market-status` | US market open/closed | — |
| `/api/v1/polygon/market-holidays` | Market holidays | — |
| `/api/v1/polygon/exchanges` | Exchange list | — |
| `/api/v1/polygon/sma` | SMA indicator | `stocks_ticker`, `timespan`, `window` |
| `/api/v1/polygon/ema` | EMA indicator | `stocks_ticker`, `timespan`, `window` |
| `/api/v1/polygon/rsi` | RSI indicator | `stock_ticker`, `timespan`, `window` |
| `/api/v1/polygon/macd` | MACD indicator | `stocks_ticker`, `timespan` |
| `/api/v1/polygon/options/contracts` | Options contracts list | `underlying_asset`, `contract_type`, `expiration_date` |
| `/api/v1/polygon/options/contract-details` | Single contract details | `options_ticker` |
| `/api/v1/polygon/options/snapshot` | Options chain snapshot | `underlying_asset` |
| `/api/v1/polygon/options/snapshot/contract` | Single option snapshot | `options_ticker` |

**`timespan` values:** `minute` `hour` `day` `week` `month` `quarter` `year`

---

### 🏢 US Fundamentals — Alpha Vantage — $0.001–$0.003/call

| Endpoint | Description | Key Params |
|----------|-------------|------------|
| `/api/v1/stocks/us/quote` | Real-time quote | `symbol` |
| `/api/v1/stocks/us/search` | Symbol search | `keywords` |
| `/api/v1/stocks/us/daily` | Daily OHLCV | `symbol`, `outputsize` (compact/full) |
| `/api/v1/stocks/us/daily-adjusted` | Adjusted daily OHLCV | `symbol`, `outputsize` |
| `/api/v1/stocks/us/intraday` | Intraday OHLCV | `symbol`, `interval` (1min/5min/15min/30min/60min), `outputsize` |
| `/api/v1/stocks/us/weekly` | Weekly OHLCV | `symbol` |
| `/api/v1/stocks/us/monthly` | Monthly OHLCV | `symbol` |
| `/api/v1/stocks/us/overview` | Company fundamentals | `symbol` |
| `/api/v1/stocks/us/earnings` | Quarterly & annual earnings | `symbol` |
| `/api/v1/stocks/us/income` | Income statement | `symbol` |
| `/api/v1/stocks/us/balance-sheet` | Balance sheet | `symbol` |
| `/api/v1/stocks/us/cash-flow` | Cash flow statement | `symbol` |
| `/api/v1/stocks/us/movers` | Top gainers/losers/most active | — |
| `/api/v1/stocks/us/news` | News & sentiment | `tickers`, `topics` |
| `/api/v1/stocks/us/rsi` | RSI | `symbol`, `interval`, `time_period` |
| `/api/v1/stocks/us/macd` | MACD | `symbol`, `interval` |
| `/api/v1/stocks/us/bbands` | Bollinger Bands | `symbol`, `interval`, `time_period` |
| `/api/v1/stocks/us/sma` | SMA | `symbol`, `interval`, `time_period` |
| `/api/v1/stocks/us/ema` | EMA | `symbol`, `interval`, `time_period` |

---

### 🇨🇳 China A-Shares — Tushare — $0.001–$0.003/call

| Endpoint | Description | Key Params |
|----------|-------------|------------|
| `/api/v1/stocks/cn/stock-basic` | Listed stock directory | `list_status` (L/D/P), `ts_code` |
| `/api/v1/stocks/cn/daily` | Daily OHLCV | `ts_code`, `start_date`, `end_date` |
| `/api/v1/stocks/cn/weekly` | Weekly OHLCV | `ts_code`, `start_date`, `end_date` |
| `/api/v1/stocks/cn/monthly` | Monthly OHLCV | `ts_code`, `start_date`, `end_date` |
| `/api/v1/stocks/cn/daily-basic` | Daily valuation metrics | `ts_code`, `trade_date` |
| `/api/v1/stocks/cn/trade-cal` | Trading calendar | `start_date`, `end_date`, `is_open` |
| `/api/v1/stocks/cn/income` | Income statement | `ts_code`, `period` |
| `/api/v1/stocks/cn/balance-sheet` | Balance sheet | `ts_code`, `period` |
| `/api/v1/stocks/cn/cash-flow` | Cash flow statement | `ts_code`, `period` |
| `/api/v1/stocks/cn/dividend` | Dividend history | `ts_code` |
| `/api/v1/stocks/cn/northbound` | Northbound capital flow | `trade_date` |
| `/api/v1/stocks/cn/moneyflow` | Money flow (net in/out) | `ts_code`, `start_date` |
| `/api/v1/stocks/cn/margin` | Margin trading summary | `ts_code`, `start_date`, `end_date` |
| `/api/v1/stocks/cn/margin-detail` | Margin trading detail | `ts_code`, `trade_date` |
| `/api/v1/stocks/cn/top-list` | Dragon Tiger List (top traders) | `trade_date` |
| `/api/v1/stocks/cn/top-inst` | Institutional top list | `trade_date`, `ts_code` |

**Date format:** `YYYYMMDD` (e.g., `20240315`)
**Stock code format:** `000001.SZ` (Shenzhen) · `600000.SH` (Shanghai)

---

### 🌍 Forex & Global — Twelve Data — $0.001–$0.005/call

| Endpoint | Description | Key Params |
|----------|-------------|------------|
| `/api/v1/twelvedata/time-series` | Time series (OHLCV) | `symbol`, `interval`, `outputsize` |
| `/api/v1/twelvedata/price` | Real-time price | `symbol` |
| `/api/v1/twelvedata/quote` | Full quote | `symbol` |
| `/api/v1/twelvedata/eod` | End-of-day price | `symbol` |
| `/api/v1/twelvedata/exchange-rate` | Currency exchange rate | `symbol` (e.g., `USD/JPY`) |
| `/api/v1/twelvedata/forex-pairs` | Available forex pairs | — |
| `/api/v1/twelvedata/economic-calendar` | Economic events calendar | — |
| `/api/v1/twelvedata/metals/price` | Precious metals real-time | `symbol` (XAU/USD, XAG/USD) |
| `/api/v1/twelvedata/metals/time-series` | Metals OHLCV history | `symbol`, `interval` |
| `/api/v1/twelvedata/indices/list` | Global indices directory | — |
| `/api/v1/twelvedata/indices/quote` | Index quote | `symbol` (SPX, NDX, DJI) |
| `/api/v1/twelvedata/indicator/sma` | SMA | `symbol`, `interval`, `time_period`, `outputsize` |
| `/api/v1/twelvedata/indicator/ema` | EMA | `symbol`, `interval`, `time_period`, `outputsize` |
| `/api/v1/twelvedata/indicator/rsi` | RSI | `symbol`, `interval`, `time_period`, `outputsize` |
| `/api/v1/twelvedata/indicator/macd` | MACD | `symbol`, `interval` |
| `/api/v1/twelvedata/indicator/bbands` | Bollinger Bands | `symbol`, `interval`, `time_period` |
| `/api/v1/twelvedata/indicator/atr` | ATR (volatility) | `symbol`, `interval`, `time_period` |
| `/api/v1/twelvedata/time-series/complex` | Complex multi-indicator POST | JSON body |

**`interval` values:** `1min` `5min` `15min` `30min` `1h` `2h` `4h` `1day` `1week` `1month`
**Symbol examples:** `EUR/USD` `GBP/JPY` `BTC/USD` `AAPL` `XAU/USD` `SPX`

---

### 🤖 AI Inference — OpenAI & Anthropic — $0.001–$0.015/call

#### OpenAI (all POST except models)
| Endpoint | Description | Cost | Body |
|----------|-------------|------|------|
| `/api/v1/ai/openai/chat` | GPT-4o chat | $0.010 | `{model, messages, max_tokens}` |
| `/api/v1/ai/openai/chat/mini` | GPT-4o-mini chat | $0.001 | `{messages, max_tokens}` |
| `/api/v1/ai/openai/embeddings` | text-embedding-3-small | $0.001 | `{input, model}` |
| `/api/v1/ai/openai/embeddings/large` | text-embedding-3-large | $0.005 | `{input, model}` |
| `/api/v1/ai/openai/images` | DALL-E image generation | $0.050 | `{prompt, n, size}` |
| `/api/v1/ai/openai/models` | List available models (GET) | $0.001 | — |

#### Anthropic (all POST)
| Endpoint | Description | Cost | Body |
|----------|-------------|------|------|
| `/api/v1/ai/anthropic/messages` | Claude Sonnet (balanced) | $0.010 | `{model, max_tokens, messages}` |
| `/api/v1/ai/anthropic/messages/haiku` | Claude Haiku (fast, cheap) | $0.005 | `{max_tokens, messages}` |
| `/api/v1/ai/anthropic/messages/opus` | Claude Opus (best reasoning) | $0.015 | `{max_tokens, messages}` |

---

## Parameter Reference

### Crypto (Coinank / Nofxos)
| Parameter | Values / Format |
|-----------|-----------------|
| `exchange` | `Binance` `OKX` `Bybit` `Bitget` `dYdX` |
| `productType` | `SWAP` (perpetual futures) · `SPOT` |
| `interval` (crypto) | `1m` `5m` `15m` `1h` `4h` `1d` |
| `duration` (nofx) | `5m` `15m` `1h` `4h` `24h` |
| `endTime` | Unix timestamp in **milliseconds** — use `Date.now()` if omitted |
| `size` | Number of data points (default varies, max ~500) |
| `sortType` | `asc` or `desc` |
| `lang` (news) | `en` (English) · `zh` (Chinese) |
| RSI `interval` | **Uppercase**: `1H` `4H` `1D` |

### US Stocks
| Parameter | Values / Format |
|-----------|-----------------|
| `symbols` (Alpaca) | Comma-separated: `AAPL,TSLA,MSFT` |
| `timeframe` (Alpaca) | `1Min` `5Min` `15Min` `1Hour` `1Day` |
| `start` / `end` (Alpaca) | ISO date: `2024-01-01` |
| `timespan` (Polygon) | `minute` `hour` `day` `week` `month` `year` |
| `from` / `to` (Polygon) | ISO date: `2024-01-01` |
| `interval` (Alpha Vantage) | `1min` `5min` `15min` `30min` `60min` `daily` `weekly` `monthly` |

### China A-Shares
| Parameter | Values / Format |
|-----------|-----------------|
| `ts_code` | `000001.SZ` (Shenzhen) · `600000.SH` (Shanghai) |
| `start_date` / `end_date` | `YYYYMMDD`: `20240101` |
| `trade_date` | `YYYYMMDD`: `20240315` |
| `list_status` | `L` (listed) · `D` (delisted) · `P` (paused) |

---

## Tips for Best Results

- **Chain data calls** for richer analysis: fetch crypto signals → US stocks → run AI synthesis in one session
- **Use `Date.now()` for `endTime`** when fetching real-time crypto data
- **`exchanges=""` (empty string)** in Coinank market-order agg endpoints means all exchanges
- **POST endpoints** (AI, Twelvedata complex): use `node scripts/query.mjs <path> --post '<json>'`
- **VIP1/2/3/4 crypto endpoints** are accessible through claw402 like all others — no extra config
- **Free catalog**: `https://claw402.ai/api/v1/catalog` — always up to date, no payment required
- **Present results clearly**: use tables or bullet points, not raw JSON. Highlight the most actionable numbers
- **Cost check**: total for a full market analysis session (5–10 calls) is typically < $0.02 USDC

---

*Powered by [claw402.ai](https://claw402.ai) — x402 micropayment gateway for AI agents.*
