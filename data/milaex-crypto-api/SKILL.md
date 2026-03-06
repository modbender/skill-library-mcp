---
name: milaex
description: Unified crypto market data API and scripts for exchanges, markets, tickers, OHLCV, and orderbooks.
homepage: https://api.milaex.com/api-docs/index.html
metadata: {"clawdbot":{"emoji":"📈","requires":{"bins":["python3"],"env":["MILAEX_API_KEY"]}}}
---

# Milaex skill (crypto market data)

Use this skill for **crypto data-related searches** that need real-time or normalized market data across multiple exchanges using the **Milaex unified REST API**.

## What this gives an agent
- One place to query exchanges, markets/pairs, tickers, OHLCV/candles, and orderbooks.
- Normalized request/response shapes across exchanges.
- Consistent JSON output for piping into other tools.
- Friendly error output (HTTP code + Milaex error payload) and optional rate-limit header printing.

## Service facts (from milaex.com)
- Milaex is a unified crypto market data SaaS with a REST API across many exchanges.
- Data types include markets, tickers, OHLCV, and order books.
- API access is via an API key from the dashboard.
- Milaex is data-only (no custody, no trade execution).
- Docs: https://api.milaex.com/api-docs/index.html

## Setup (get an API key)

1. Go to https://milaex.com and sign up or log in.
2. In the Milaex dashboard, generate an API key for the market data API.

## Configuration

Required env vars:
- `MILAEX_API_KEY` (sent as `x-api-key`)

### Recommended (Clawdbot): store the key in openclaw config

This lets Clawdbot inject the env var when running the skill.

Edit `~/.clawdbot/openclaw.json`:
```json
{
  "skills": {
    "entries": {
      "milaex": {
        "enabled": true,
        "env": {
          "MILAEX_API_KEY": "..."
        }
      }
    }
  }
}
```

### Manual shell usage (export env vars)

```bash
export MILAEX_API_KEY="..."
```

## Endpoints (from public OpenAPI v1)
These scripts map to the following Milaex endpoints:
- `GET /api/v1/exchange`
- `GET /api/v1/exchange/markets?exchange=`
- `GET /api/v1/exchange/ticker?exchange=&base_name=&quote_name=`
- `GET /api/v1/exchange/tickers?exchange=&symbols=`
- `GET /api/v1/exchange/ohlcv?exchange=&base_name=&quote_name=`
- `GET /api/v1/exchange/orderbook?exchange=&base_name=&quote_name=`
- `GET /api/v1/exchange/orderbook/complete?exchange=&base_name=&quote_name=`

## Mapping common search questions to endpoints
- Which exchanges are supported? -> `GET /api/v1/exchange`
- What markets does exchange X support? -> `GET /api/v1/exchange/markets?exchange=`
- Current price for BTC/USDT on exchange X? -> `GET /api/v1/exchange/ticker?exchange=&base_name=&quote_name=`
- Multiple symbols on exchange X? -> `GET /api/v1/exchange/tickers?exchange=&symbols=`
- Candle data for a pair? -> `GET /api/v1/exchange/ohlcv?exchange=&base_name=&quote_name=`
- Orderbook snapshot? -> `GET /api/v1/exchange/orderbook?exchange=&base_name=&quote_name=`

## Quick commands

All commands print JSON to **stdout**. Rate limit headers (when present) print to **stderr**.

### List exchanges
```bash
python3 skills/milaex/scripts/list_exchanges.py
# or
bash skills/milaex/bin/list_exchanges.sh
```

### List markets for an exchange
```bash
python3 skills/milaex/scripts/list_markets.py --exchange binance
```

### Get a single ticker
```bash
python3 skills/milaex/scripts/get_ticker.py --exchange binance --symbol BTC/USDT
```

### Get tickers (optionally filtered by symbols)
```bash
python3 skills/milaex/scripts/get_tickers.py --exchange binance
python3 skills/milaex/scripts/get_tickers.py --exchange binance --symbols "BTC/USDT,ETH/USDT"
```

### Get OHLCV
Note: Milaex v1 OpenAPI exposes OHLCV by `exchange/base_name/quote_name`. The script accepts `--timeframe` for forward-compat but does not send it (to avoid 400s).
```bash
python3 skills/milaex/scripts/get_ohlcv.py --exchange binance --symbol BTC/USDT --limit 200
```

### Get orderbook
```bash
python3 skills/milaex/scripts/get_orderbook.py --exchange binance --symbol BTC/USDT --limit 50
python3 skills/milaex/scripts/get_orderbook.py --exchange binance --symbol BTC/USDT --complete
```

## Common use cases

### For traders
- Monitor best bid/ask spreads across venues
- Build simple cross-exchange arb screens
- Detect volatility regime changes via OHLCV
- Alerting: “price moved X% in Y minutes”

### For data engineers / analysts
- Pull normalized tick data for dashboards
- Build research datasets (candles + orderbook snapshots)
- Run periodic ETL without maintaining exchange adapters

### For product and support teams
- Answer coverage questions (exchanges, pairs, availability)
- Validate pricing/latency assumptions with real data

## Notes
- Keep within endpoint RPM limits (Milaex also returns standard rate-limit headers when enabled for your plan).
- Scripts require Python 3 and `requests`.

Install dependency if needed:
```bash
python3 -m pip install --user requests
```

## Test (expected unauthorized)
This is a small smoke test that verifies unauthorized handling using a dummy key. Some deployments return **401**, others return **404** with an "Api Key not found" message.
```bash
MILAEX_API_KEY=dummy python3 skills/milaex/scripts/test_unauthorized.py
```
