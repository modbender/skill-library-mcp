# Bitstamp API Reference (via CCXT)

## Authentication

Environment variables (never in code):
- `BITSTAMP_API_KEY` — API key from Bitstamp
- `BITSTAMP_API_SECRET` — API secret

### Recommended API Key Permissions

Create keys at: https://www.bitstamp.net/settings/api/

| Permission | Read-only | Trading | Full |
|---|---|---|---|
| Account Balance | ✅ | ✅ | ✅ |
| User Transactions | ✅ | ✅ | ✅ |
| Open Orders | ✅ | ✅ | ✅ |
| Orders | ❌ | ✅ | ✅ |
| Withdrawals | ❌ | ❌ | ✅ |
| Deposits | ❌ | ❌ | ✅ |

**Recommended: Trading profile** — enable Orders but NOT Withdrawals.
**Always enable IP whitelisting** on the API key.

## Rate Limits

- 400 requests/second, 10,000 per 10 minutes
- CCXT handles rate limiting automatically (`enableRateLimit: True`)

## Key Endpoints (via CCXT)

### Public (no auth)
- `fetch_ticker(symbol)` — current price
- `fetch_order_book(symbol, limit)` — order book
- `fetch_trades(symbol, limit)` — recent public trades
- `fetch_ohlcv(symbol, timeframe, since, limit)` — candlestick data
- `fetch_currencies()` — available currencies
- `load_markets()` — all trading pairs

### Private (auth required)
- `fetch_balance()` — account balances
- `fetch_open_orders(symbol)` — open orders
- `fetch_my_trades(symbol, since, limit)` — trade history
- `create_limit_buy_order(symbol, amount, price)` — limit buy
- `create_limit_sell_order(symbol, amount, price)` — limit sell
- `create_market_buy_order(symbol, amount)` — market buy
- `create_market_sell_order(symbol, amount)` — market sell
- `cancel_order(id, symbol)` — cancel specific order
- `fetch_trading_fee(symbol)` — current fee tier

## Bitstamp-Specific Notes

- Minimum order: varies by pair (BTC/USD min ~$10 equivalent)
- Trading fees: 0.0-0.4% based on 30-day volume
- No margin/futures — spot only
- WebSocket: `wss://ws.bitstamp.net` for live data
- Sub-accounts available via `X-Auth-Subaccount-Id` header

## Error Codes

| Code | Meaning |
|---|---|
| 400.067 | Client rate limit exceeded |
| 400.068 | Market rate limit exceeded |
| 403 | IP not whitelisted / permission denied |
| 404 | Invalid market pair |
