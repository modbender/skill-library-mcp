# Alpaca API Reference

## Endpoints

### Base URLs
- Paper Trading: `https://paper-api.alpaca.markets`
- Live Trading: `https://api.alpaca.markets`
- Market Data: `https://data.alpaca.markets`

## Authentication

All requests require headers:
```
APCA-API-KEY-ID: <api_key>
APCA-API-SECRET-KEY: <secret_key>
```

## Account

### GET /v2/account
Returns account info including buying power, equity, and status.

Response fields:
- `buying_power` - Available funds for trading
- `cash` - Cash balance
- `portfolio_value` - Total portfolio value
- `equity` - Account equity
- `pattern_day_trader` - PDT flag

## Positions

### GET /v2/positions
Returns all open positions.

### GET /v2/positions/{symbol}
Returns position for specific symbol.

Response fields:
- `symbol` - Stock symbol
- `qty` - Quantity held
- `avg_entry_price` - Average cost basis
- `current_price` - Current market price
- `unrealized_pl` - Unrealized profit/loss
- `unrealized_plpc` - P/L percentage

## Orders

### POST /v2/orders
Place a new order.

Request body:
```json
{
  "symbol": "AAPL",
  "qty": 10,
  "side": "buy",
  "type": "market|limit|stop|stop_limit",
  "time_in_force": "day|gtc|ioc|fok",
  "limit_price": 150.00,
  "stop_price": 145.00
}
```

### GET /v2/orders
List orders. Query params: `status`, `limit`, `after`, `until`.

### GET /v2/orders/{order_id}
Get order by ID.

### DELETE /v2/orders/{order_id}
Cancel order.

### DELETE /v2/orders
Cancel all orders.

## Order Types

| Type | Description |
|------|-------------|
| market | Execute immediately at market price |
| limit | Execute at limit price or better |
| stop | Trigger market order when stop price reached |
| stop_limit | Trigger limit order when stop price reached |

## Time in Force

| Value | Description |
|-------|-------------|
| day | Good for day (default) |
| gtc | Good til cancelled |
| ioc | Immediate or cancel |
| fok | Fill or kill |

## Market Data

### GET /v2/stocks/{symbol}/quotes/latest
Latest quote for symbol.

### GET /v2/stocks/{symbol}/bars
Historical bars. Query params:
- `timeframe` - 1Min, 5Min, 15Min, 1Hour, 1Day
- `start` - Start timestamp
- `end` - End timestamp
- `limit` - Max bars

### GET /v2/stocks/news
News articles. Query params:
- `symbols` - Comma-separated symbols
- `limit` - Max articles

## Watchlists

### GET /v2/watchlists
List all watchlists.

### POST /v2/watchlists
Create watchlist.

### POST /v2/watchlists/{watchlist_id}
Add symbol to watchlist.

### DELETE /v2/watchlists/{watchlist_id}
Delete watchlist.

## Rate Limits

- Trading API: 200 requests/minute
- Market Data: 200 requests/minute

## Error Codes

| Code | Description |
|------|-------------|
| 403 | Forbidden (check API keys) |
| 422 | Unprocessable (invalid order) |
| 429 | Rate limited |

## Market Hours

- Pre-market: 4:00 AM - 9:30 AM ET
- Regular: 9:30 AM - 4:00 PM ET
- After-hours: 4:00 PM - 8:00 PM ET

Extended hours require `extended_hours: true` in order request.

## Websocket Streaming

### Endpoint
`wss://stream.data.alpaca.markets/v2/iex` (IEX)
`wss://stream.data.alpaca.markets/v2/sip` (SIP - requires subscription)

### Data Types

| Type | Description |
|------|-------------|
| trades | Individual trade executions |
| quotes | Best bid/ask updates |
| bars | 1-minute OHLCV bars |

### Message Format

**Trade:**
```json
{"T":"t","S":"AAPL","p":150.25,"s":100,"t":"2026-02-07T14:30:00Z","x":"V"}
```

**Quote:**
```json
{"T":"q","S":"AAPL","bp":150.20,"bs":200,"ap":150.25,"as":100,"t":"2026-02-07T14:30:00Z"}
```

**Bar:**
```json
{"T":"b","S":"AAPL","o":150.00,"h":150.50,"l":149.80,"c":150.25,"v":10000,"t":"2026-02-07T14:30:00Z"}
```

### Subscription Limits

- Free tier: Real-time IEX data
- Algo Trader Plus: Real-time SIP data (all exchanges)
