---
name: twelve-data
description: Use Twelve Data REST/WebSocket APIs for market quotes, latest prices, historical time series, symbol discovery, and technical indicators. Trigger when users need live or historical multi-asset market data.
metadata:
  openclaw:
    emoji: "📊"
    requires:
      env:
        - TWELVEDATA_API_KEY
    primaryEnv: TWELVEDATA_API_KEY
---

# Twelve Data

This skill provides practical request patterns for Twelve Data based on official docs.

Official docs:
- https://twelvedata.com/docs
- https://support.twelvedata.com/en/articles/5620512-how-to-create-a-request
- https://support.twelvedata.com/en/articles/5335783-trial

## Base URLs

- REST API: `https://api.twelvedata.com`
- WebSocket: `wss://ws.twelvedata.com`

## Authentication

Twelve Data supports two auth methods:

1. Query parameter

```bash
curl "https://api.twelvedata.com/price?symbol=AAPL&apikey=${TWELVEDATA_API_KEY}"
```

2. HTTP header (recommended by docs)

```bash
curl -H "Authorization: apikey ${TWELVEDATA_API_KEY}" \
  "https://api.twelvedata.com/price?symbol=AAPL"
```

Notes:
- `apikey=demo` can be used for limited trial/demo requests.
- Premium endpoints require higher-tier plans.

## Quick Setup

Configure in OpenClaw:

```json5
{
  skills: {
    entries: {
      "twelve-data": {
        enabled: true,
        apiKey: "your-twelvedata-api-key",
        env: {
          TWELVEDATA_API_KEY: "your-twelvedata-api-key"
        }
      }
    }
  }
}
```

Or in `~/.openclaw/.env`:

```bash
TWELVEDATA_API_KEY=your-api-key-here
```

## Core Endpoints (Practical)

### 1) Latest price (`/price`, 1 credit/symbol)

```bash
curl "https://api.twelvedata.com/price?symbol=AAPL&apikey=${TWELVEDATA_API_KEY}"
```

### 2) Real-time quote (`/quote`, 1 credit/symbol)

```bash
curl "https://api.twelvedata.com/quote?symbol=AAPL&apikey=${TWELVEDATA_API_KEY}"
```

### 3) Historical OHLCV (`/time_series`, 1 credit/symbol)

```bash
curl "https://api.twelvedata.com/time_series?symbol=AAPL&interval=1day&outputsize=100&apikey=${TWELVEDATA_API_KEY}"
```

Common `interval` values: `1min`, `5min`, `15min`, `30min`, `1h`, `2h`, `4h`, `1day`, `1week`, `1month`

Useful params:
- `outputsize=1..5000`
- `start_date=YYYY-MM-DD` or datetime
- `end_date=YYYY-MM-DD` or datetime
- `timezone=Exchange|UTC|IANA_TZ`
- `format=JSON|CSV`

### 4) Symbol discovery (`/symbol_search`, 1 credit/request)

```bash
curl "https://api.twelvedata.com/symbol_search?symbol=apple&apikey=${TWELVEDATA_API_KEY}"
```

### 5) Technical indicators (typically 1 credit/symbol)

RSI:

```bash
curl "https://api.twelvedata.com/rsi?symbol=AAPL&interval=1day&time_period=14&series_type=close&apikey=${TWELVEDATA_API_KEY}"
```

MACD:

```bash
curl "https://api.twelvedata.com/macd?symbol=AAPL&interval=1day&series_type=close&apikey=${TWELVEDATA_API_KEY}"
```

### 6) Fundamentals (plan-gated, higher credits)

Earnings (`/earnings`, Grow+):

```bash
curl "https://api.twelvedata.com/earnings?symbol=AAPL&apikey=${TWELVEDATA_API_KEY}"
```

Statistics (`/statistics`, Pro+):

```bash
curl "https://api.twelvedata.com/statistics?symbol=AAPL&apikey=${TWELVEDATA_API_KEY}"
```

Income statement (`/income_statement`, Pro+):

```bash
curl "https://api.twelvedata.com/income_statement?symbol=AAPL&apikey=${TWELVEDATA_API_KEY}"
```

Balance sheet (`/balance_sheet`, Pro+):

```bash
curl "https://api.twelvedata.com/balance_sheet?symbol=AAPL&apikey=${TWELVEDATA_API_KEY}"
```

Cash flow (`/cash_flow`, Pro+):

```bash
curl "https://api.twelvedata.com/cash_flow?symbol=AAPL&apikey=${TWELVEDATA_API_KEY}"
```

Dividends:

```bash
curl "https://api.twelvedata.com/dividends?symbol=AAPL&start_date=1970-01-01&apikey=${TWELVEDATA_API_KEY}"
```

## Batch and Multi-Asset Examples

Batch symbols on supported endpoints:

```bash
curl "https://api.twelvedata.com/time_series?symbol=AAPL,EUR/USD,ETH/BTC:Huobi&interval=1min&apikey=${TWELVEDATA_API_KEY}"
```

Asset symbol patterns:
- Stocks: `AAPL`
- Forex: `EUR/USD`
- Crypto: `BTC/USD` or exchange-scoped pair like `ETH/BTC:Huobi`

## WebSocket (Streaming)

Connect:

```text
wss://ws.twelvedata.com/v1/quotes/price?apikey=YOUR_API_KEY
```

Subscribe message:

```json
{
  "action": "subscribe",
  "params": {
    "symbols": "AAPL,MSFT"
  }
}
```

## Reliability Guidance

- Always handle `null` values in responses.
- Implement retry/backoff for transient failures and `429` rate limits.
- Cache frequent reads to reduce credit usage.
- Check your current credit/rate limits in Twelve Data dashboard (plan-dependent).

## Skill Usage Workflow

When user asks for market data analysis:

1. Resolve symbol with `/symbol_search` if ambiguous.
2. Pull latest context with `/price` or `/quote`.
3. Pull history with `/time_series` for selected interval/date range.
4. Add indicators (`/rsi`, `/macd`, etc.) if technical analysis is requested.
5. Add fundamentals endpoints only when user asks for financial statements or valuation context.
6. Report endpoint, parameters, and plan limits clearly in output.
