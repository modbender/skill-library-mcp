---
name: ctrader-commander
description: Place and manage cTrader orders (market, limit, stop), check open positions, fetch live quotes and OHLC candles, and query account balance and equity via a local HTTP proxy. No credentials or token required at call time.
homepage: https://github.com/LogicalSapien/ctrader-openapi-proxy
metadata: {"openclaw": {"emoji": "\ud83d\udcc8", "requires": {"bins": ["curl"]}, "homepage": "https://github.com/LogicalSapien/ctrader-openapi-proxy"}}
---

# cTrader Commander

Use when the user wants to place trades, check positions or balance, get live prices, fetch candles, or manage orders on a cTrader account.

All calls go to `http://localhost:9009` — credentials live in `.env` on the server, never passed by callers.

> **Proxy repo:** https://github.com/LogicalSapien/ctrader-openapi-proxy
> Clone it, add your `.env`, and run `make run` to start the proxy before using this skill.

Full reference: `{baseDir}/endpoints.md`

## Check proxy is running

```bash
curl -s "http://localhost:9009/get-data?command=ProtoOAVersionReq"
```

If it fails, start the proxy: `cd ~/ctrader-openapi-proxy && make run`

## Find symbol IDs (do this first)

Symbol IDs are broker-specific — look them up before placing orders or fetching data:

```bash
curl -s "http://localhost:9009/get-data?command=ProtoOASymbolsListReq"
```

Returns `symbol[]` with `symbolId` and `symbolName`. Note the ID for your instrument.

## Place a market order

```bash
curl -s -X POST http://localhost:9009/api/market-order \
  -H "Content-Type: application/json" \
  -d '{"symbolId": 158, "orderType": "MARKET", "tradeSide": "BUY", "volume": 1000}'
```

Volume is in **units**: `1000` = 0.01 lot · `10000` = 0.1 lot · `100000` = 1 lot.
Add `"relativeStopLoss": 200, "relativeTakeProfit": 350` (pips, market orders only).

## Place a limit or stop order

```bash
curl -s -X POST http://localhost:9009/api/market-order \
  -H "Content-Type: application/json" \
  -d '{"symbolId": 158, "orderType": "LIMIT", "tradeSide": "BUY", "volume": 1000, "price": 0.62500}'
```

`orderType`: `MARKET` · `LIMIT` · `STOP` — `tradeSide`: `BUY` · `SELL`

## Get OHLC candles

```bash
NOW_MS=$(python3 -c "import time; print(int(time.time()*1000))")
FROM_MS=$(python3 -c "import time; print(int(time.time()*1000) - 3600000)")
curl -s -X POST http://localhost:9009/api/trendbars \
  -H "Content-Type: application/json" \
  -d "{\"fromTimestamp\": $FROM_MS, \"toTimestamp\": $NOW_MS, \"period\": \"M5\", \"symbolId\": 158}"
```

Periods: `M1 M2 M3 M4 M5 M10 M15 M30 H1 H4 H12 D1 W1 MN1`

## Get live quote (tick data)

```bash
curl -s -X POST http://localhost:9009/api/live-quote \
  -H "Content-Type: application/json" \
  -d '{"symbolId": 158, "quoteType": "BID", "timeDeltaInSeconds": 60}'
```

`quoteType`: `BID` or `ASK`

## Open positions and pending orders

```bash
curl -s "http://localhost:9009/get-data?command=ProtoOAReconcileReq"
```

## Close a position

```bash
curl -s "http://localhost:9009/get-data?command=ClosePosition%20123456%201000"
# ClosePosition <positionId> <volumeInUnits>
```

## Cancel a pending order

```bash
curl -s "http://localhost:9009/get-data?command=CancelOrder%20789"
```

## Account info (balance, equity, leverage)

```bash
curl -s "http://localhost:9009/get-data?command=ProtoOATraderReq"
```


A local HTTP proxy (`localhost:9009`) that wraps the cTrader OpenAPI Protobuf connection and exposes it as a REST API. No credentials are passed at call time — they are loaded from `.env` on the server.

Full endpoint reference: `{baseDir}/endpoints.md`
Python usage examples: `{baseDir}/examples.md`

---

## Prerequisites

The proxy must be running before any call. If unsure, check:
```bash
curl -s "http://localhost:9009/get-data?command=ProtoOAVersionReq"
```
If it returns JSON, the proxy is up. If it fails, start it:
```bash
cd ~/ctrader-openapi-proxy && make run
```

---

## IMPORTANT: Symbol IDs are broker-specific

**Always look up the symbol ID before placing orders or fetching candle/tick data.**
Symbol IDs differ between brokers and between demo and live accounts.

```bash
curl -s "http://localhost:9009/get-data?command=ProtoOASymbolsListReq"
```

Response contains `symbol[]` with `symbolId` and `symbolName`. Find your instrument and note its `symbolId`.

---

## Endpoints

### Get OHLC Candles
```
POST /api/trendbars
```
```json
{
  "fromTimestamp": 1700000000000,
  "toTimestamp":   1700086400000,
  "period":        "M5",
  "symbolId":      158
}
```
`period` options: `M1 M2 M3 M4 M5 M10 M15 M30 H1 H4 H12 D1 W1 MN1`

For current time in ms (macOS):
```bash
NOW_MS=$(python3 -c "import time; print(int(time.time()*1000))")
FROM_MS=$(python3 -c "import time; print(int(time.time()*1000) - 3600000)")
```

---

### Get Live Quote / Tick Data
```
POST /api/live-quote
```
```json
{
  "symbolId":           158,
  "quoteType":          "BID",
  "timeDeltaInSeconds": 60
}
```
`quoteType`: `"BID"` or `"ASK"`

---

### Place a Market / Limit / Stop Order
```
POST /api/market-order
```
```json
{
  "symbolId":           158,
  "orderType":          "MARKET",
  "tradeSide":          "BUY",
  "volume":             1000,
  "comment":            "my trade",
  "relativeStopLoss":   200,
  "relativeTakeProfit": 350
}
```

**orderType** values: `"MARKET"` `"LIMIT"` `"STOP"`  
**tradeSide** values: `"BUY"` `"SELL"`

For `LIMIT` and `STOP` orders, include `"price": 0.62500`.  
`relativeStopLoss` / `relativeTakeProfit` are in **pips** and apply to `MARKET` orders only.

**Volume units (NOT lots):**
| `volume` | Lots | Notes |
|---|---|---|
| `1000` | 0.01 | Micro lot — typical minimum |
| `10000` | 0.1 | Mini lot |
| `100000` | 1 | Standard lot |

---

### Get Open Positions and Pending Orders
```
GET /get-data?command=ProtoOAReconcileReq
```
Returns `position[]` and `order[]`. Each position has `positionId`, `symbolId`, `tradeSide`, `volume`, `price`.

---

### Close an Open Position
```
GET /get-data?command=ClosePosition <positionId> <volumeInUnits>
```
Example — close position 123456 with 1000 units (0.01 lot):
```bash
curl -s "http://localhost:9009/get-data?command=ClosePosition%20123456%201000"
```

---

### Cancel a Pending Order
```
GET /get-data?command=CancelOrder <orderId>
```
```bash
curl -s "http://localhost:9009/get-data?command=CancelOrder%20789"
```

---

### Set Active Account *(optional)*
Account is auto-authorised from `.env` on startup. Only call this to switch accounts at runtime:
```bash
curl -s -X POST http://localhost:9009/api/set-account
```
To switch to a different account pass `{"accountId": 12345678}` as JSON body.

---

### Generic Command Passthrough
Any cTrader API command can be called via:
```
GET /get-data?command=COMMAND_NAME arg1 arg2
```
No token required — credentials are read from `.env` on the server.

Full list of supported commands: `{baseDir}/endpoints.md`

---

## Workflow: first trade

1. Look up your symbol ID:
   ```bash
   curl -s "http://localhost:9009/get-data?command=ProtoOASymbolsListReq" | python3 -c "
   import sys, json
   data = json.load(sys.stdin)
   [print(s['symbolId'], s['symbolName']) for s in data.get('symbol', []) if 'EURUSD' in s['symbolName']]
   "
   ```
2. Check your account details:
   ```bash
   curl -s "http://localhost:9009/get-data?command=ProtoOATraderReq"
   ```
3. Place a market buy:
   ```bash
   curl -s -X POST http://localhost:9009/api/market-order \
     -H "Content-Type: application/json" \
     -d '{"symbolId": 1, "orderType": "MARKET", "tradeSide": "BUY", "volume": 1000}'
   ```
4. Check open positions:
   ```bash
   curl -s "http://localhost:9009/get-data?command=ProtoOAReconcileReq"
   ```
