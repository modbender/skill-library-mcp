# Alpaca Markets API Reference

## Overview
Alpaca provides REST APIs for trading stocks, options, and cryptocurrencies with live and paper accounts.

Trading API base URLs:
- Paper: `https://paper-api.alpaca.markets`
- Live: `https://api.alpaca.markets`

Market Data API base URL:
- `https://data.alpaca.markets`

## Authentication
Use HTTP headers:
- APCA-API-KEY-ID: Your API key
- APCA-API-SECRET-KEY: Your API secret

## Trading API

### Account
- GET /v2/account - Get account information (buying power, cash, etc.)
- GET /v2/account/portfolio/history - Portfolio equity history

### Orders (Stocks, Options, Crypto)
- GET /v2/orders - List orders (params: status, after, until, limit, nested, symbols)
- POST /v2/orders - Place order
  - Body: {"symbol": "AAPL", "qty": "10", "side": "buy", "type": "market", "time_in_force": "gtc"}
  - Crypto example: {"symbol": "BTC/USD", "notional": "100", "side": "buy", "type": "market", "time_in_force": "gtc"}
- GET /v2/orders/{order_id} - Get specific order
- PATCH /v2/orders/{order_id} - Replace an order (qty, time_in_force, limit_price, stop_price, trail)
- DELETE /v2/orders/{order_id} - Cancel order
- DELETE /v2/orders - Cancel all open orders

### Positions
- GET /v2/positions - List all positions
- GET /v2/positions/{symbol} - Get position for symbol
- DELETE /v2/positions/{symbol} - Close position
- DELETE /v2/positions - Close all positions

### Assets
- GET /v2/assets - List assets (params: status=active)
- GET /v2/assets/{symbol} - Get asset info

## Market Data API (Crypto)

The crypto trading lifecycle uses Trading API `/v2/orders` and `/v2/positions`.

Representative data endpoints:
- GET /v1beta3/crypto/us/latest/quotes?symbols=BTC/USD,ETH/USD - Latest quotes
- GET /v1beta3/crypto/us/bars?symbols=BTC/USD&timeframe=1Min&start=...&end=... - Historical bars

## Error Codes
- 200: Success
- 400: Bad request
- 401: Unauthorized
- 403: Forbidden
- 404: Not found
- 422: Unprocessable entity

Rate limits vary by endpoint and plan.

Full docs: https://docs.alpaca.markets/
