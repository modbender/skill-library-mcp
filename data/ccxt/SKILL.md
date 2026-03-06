---
name: ccxt
description: Interact with 100+ cryptocurrency exchanges — fetch markets, order books, tickers, place orders, check balances, and more using the CCXT CLI.
homepage: https://docs.ccxt.com
user-invocable: true
metadata: {"openclaw":{"emoji":"📊","requires":{"bins":["ccxt"]},"install":[{"id":"node","kind":"node","package":"ccxt-cli","bins":["ccxt"]}]}}
---

# CCXT — Cryptocurrency Exchange Trading

You have access to the `ccxt` CLI tool which lets you interact with 100+ cryptocurrency exchanges (Binance, Bybit, OKX, Kraken, Coinbase, and many more). You can fetch market data, place orders, check balances, and stream live data.

## Core Syntax

```bash
ccxt <exchange_id> <methodName> [args...] [options]
```

## Before Calling Any Method

If you're unsure about the required arguments for a method, run:

```bash
ccxt explain <methodName>
```

This will show you the required and optional arguments with descriptions.

## Available Options

| Flag | Purpose |
|------|---------|
| `--verbose` | Show raw request/response data |
| `--sandbox` | Use testnet/sandbox environment |
| `--raw` | Output clean JSON without formatting |
| `--swap` | Target swap/perpetuals account |
| `--future` | Target futures account |
| `--spot` | Target spot account |
| `--option` | Target options account |
| `--param key=value` | Pass extra exchange-specific params (repeatable) |
| `--no-keys` | Skip API key loading |

## Common Operations

### Market Data (Public — No API Keys Required)

**Fetch markets (list all trading pairs on an exchange):**
```bash
ccxt <exchange> fetchMarkets --raw
```

**Fetch a single ticker:**
```bash
ccxt <exchange> fetchTicker "BTC/USDT" --raw
```

**Fetch multiple tickers:**
```bash
ccxt <exchange> fetchTickers --raw
```

**Fetch order book:**
```bash
ccxt <exchange> fetchOrderBook "BTC/USDT" --raw
```

**Fetch OHLCV candles:**
```bash
ccxt <exchange> fetchOHLCV "BTC/USDT" 1h undefined 10 --raw
```

**Fetch recent trades:**
```bash
ccxt <exchange> fetchTrades "BTC/USDT" --raw
```

**Fetch exchange status:**
```bash
ccxt <exchange> fetchStatus --raw
```

**Fetch currencies:**
```bash
ccxt <exchange> fetchCurrencies --raw
```

### Trading (Private — Requires API Keys)

**Create an order:**
```bash
ccxt <exchange> createOrder "BTC/USDT" limit buy 0.001 50000 --raw
ccxt <exchange> createOrder "BTC/USDT" market buy 0.001 --raw
```

**Create order with extra params:**
```bash
ccxt <exchange> createOrder "BTC/USDT" limit buy 0.001 50000 --param stopPrice=49000 --raw
```

**Cancel an order:**
```bash
ccxt <exchange> cancelOrder "<order_id>" "BTC/USDT" --raw
```

**Fetch open orders:**
```bash
ccxt <exchange> fetchOpenOrders "BTC/USDT" --raw
```

**Fetch closed orders:**
```bash
ccxt <exchange> fetchClosedOrders "BTC/USDT" --raw
```

**Fetch a specific order:**
```bash
ccxt <exchange> fetchOrder "<order_id>" "BTC/USDT" --raw
```

### Account (Private — Requires API Keys)

**Fetch balance:**
```bash
ccxt <exchange> fetchBalance --raw
```

**Fetch balance for derivatives:**
```bash
ccxt <exchange> fetchBalance --swap --raw
```

**Fetch my trades:**
```bash
ccxt <exchange> fetchMyTrades "BTC/USDT" --raw
```

**Fetch positions (derivatives):**
```bash
ccxt <exchange> fetchPositions --swap --raw
```

**Fetch deposit address:**
```bash
ccxt <exchange> fetchDepositAddress "BTC" --raw
```

### Derivatives

**Fetch funding rate:**
```bash
ccxt <exchange> fetchFundingRate "BTC/USDT:USDT" --raw
```

**Fetch funding rate history:**
```bash
ccxt <exchange> fetchFundingRateHistory "BTC/USDT:USDT" --raw
```

**Fetch mark price / index price:**
```bash
ccxt <exchange> fetchMarkOHLCV "BTC/USDT:USDT" 1h --raw
ccxt <exchange> fetchIndexOHLCV "BTC/USDT:USDT" 1h --raw
```

## Important Rules

1. **Always quote symbols** that contain `/` or `:` — e.g., `"BTC/USDT"`, `"BTC/USDT:USDT"`.
2. **Use `undefined`** as a positional placeholder to skip optional arguments while providing later ones. For example: `ccxt binance fetchOHLCV "BTC/USDT" 1h undefined 10` skips `since` but provides `limit`.
3. **Use `--raw`** when you need to parse the output programmatically or when the user needs clean JSON.
4. **Use `--sandbox`** for testing with testnet environments. Always recommend sandbox mode when the user is experimenting with orders.
5. **ISO8601 datetimes** (e.g., `"2025-01-01T00:00:00Z"`) are auto-converted to milliseconds.
6. **API keys** must be configured via environment variables (e.g., `BINANCE_APIKEY`, `BINANCE_SECRET`) or the config file. If a private method fails due to missing credentials, instruct the user to set them up.
7. **Derivatives symbols** use the format `"BASE/QUOTE:SETTLE"` — e.g., `"BTC/USDT:USDT"` for USDT-margined perpetuals.
8. **Be careful with order methods** — always confirm amounts and prices with the user before executing `createOrder`. The CLI executes immediately with no confirmation prompt.
9. When the output is large (e.g., `fetchMarkets` returns hundreds of entries), consider piping through `| head` or filtering, or suggest the user narrows their query.
10. For the list of supported exchanges, you can check: `ccxt exchanges` or refer to https://docs.ccxt.com.

## Authentication Setup

Tell users to configure credentials in one of two ways:

**Option 1 — Environment variables:**
```bash
export BINANCE_APIKEY=your_api_key
export BINANCE_SECRET=your_secret
```

**Option 2 — Config file** (path shown in `ccxt --help`):
```json
{
  "binance": {
    "apiKey": "your_api_key",
    "secret": "your_secret"
  }
}
```

## Error Handling

- If you get an `AuthenticationError`, the API keys are missing or invalid.
- If you get an `ExchangeNotAvailable` or `NetworkError`, the exchange may be down or rate-limiting.
- If you get an `BadSymbol`, the trading pair doesn't exist on that exchange — use `fetchMarkets` to check available pairs.
- If you get an `InsufficientFunds`, the account doesn't have enough balance for the operation.
