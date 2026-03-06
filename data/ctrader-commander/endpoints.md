# cTrader Proxy — Full Endpoint Reference

Base URL: `http://localhost:9009`  
No token or API key is needed by callers. All credentials live in `.env` on the server.

---

## REST Endpoints

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/set-account` | Switch active account (optional — auto-set from `.env` on startup) |
| `POST` | `/api/trendbars` | OHLC candle data |
| `POST` | `/api/live-quote` | Recent tick/quote data |
| `POST` | `/api/market-order` | Place market, limit, or stop order |
| `GET` | `/get-data?command=...` | Generic passthrough for any cTrader command |

---

## POST /api/set-account

Sending no body (or `{}`) uses `CTRADER_ACCOUNTID` from `.env`.

```
POST /api/set-account
Content-Type: application/json

{}
```

To switch to a different account:
```json
{ "accountId": 12345678 }
```

**Normal response when already authorised (not an error):**
```json
{
  "ctidTraderAccountId": "12345678",
  "errorCode": "ALREADY_LOGGED_IN",
  "description": "Trading account is already authorized in this channel"
}
```

---

## POST /api/trendbars

```
POST /api/trendbars
Content-Type: application/json

{
  "fromTimestamp": 1700000000000,
  "toTimestamp":   1700086400000,
  "period":        "M5",
  "symbolId":      158
}
```

- Timestamps in **milliseconds** since Unix epoch.
- `period` values: `M1 M2 M3 M4 M5 M10 M15 M30 H1 H4 H12 D1 W1 MN1`
- `symbolId` is broker-specific — use `ProtoOASymbolsListReq` to look it up.

---

## POST /api/live-quote

```
POST /api/live-quote
Content-Type: application/json

{
  "symbolId":           158,
  "quoteType":          "BID",
  "timeDeltaInSeconds": 60
}
```

- `quoteType`: `"BID"` or `"ASK"`
- Returns tick data for the last N seconds.

---

## POST /api/market-order

```
POST /api/market-order
Content-Type: application/json

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

| Field | Required | Notes |
|---|---|---|
| `symbolId` | ✓ | Broker-specific integer |
| `orderType` | ✓ | `"MARKET"` `"LIMIT"` `"STOP"` |
| `tradeSide` | ✓ | `"BUY"` `"SELL"` |
| `volume` | ✓ | Units (not lots). 1000 = 0.01 lot |
| `price` | For LIMIT/STOP | e.g. `0.62500` |
| `comment` | Optional | Order label |
| `relativeStopLoss` | Optional | Pips from entry, MARKET only |
| `relativeTakeProfit` | Optional | Pips from entry, MARKET only |

Volume reference:
| `volume` | Lots |
|---|---|
| `1000` | 0.01 (micro — typical minimum) |
| `10000` | 0.1 (mini) |
| `100000` | 1.0 (standard) |

---

## GET /get-data?command=...

### All supported commands

| Command | Args | Description |
|---|---|---|
| `setAccount` | `accountId` | Switch active account |
| `ProtoOAVersionReq` | — | Get API version |
| `ProtoOAGetAccountListByAccessTokenReq` | — | List all accounts on this token |
| `ProtoOASymbolsListReq` | — | **List all tradeable symbols with their IDs** |
| `ProtoOAAssetListReq` | — | List all assets (currencies, etc.) |
| `ProtoOAAssetClassListReq` | — | List asset classes |
| `ProtoOASymbolCategoryListReq` | — | List symbol categories |
| `ProtoOATraderReq` | — | Account details (balance, equity, leverage) |
| `ProtoOAReconcileReq` | — | Open positions and pending orders |
| `ProtoOAGetTrendbarsReq` | `fromTs toTs period symbolId` | OHLC candle data |
| `ProtoOAGetTickDataReq` | `seconds quoteType symbolId` | Tick/quote data |
| `NewMarketOrder` | `symbolId tradeSide volume comment [sl] [tp]` | Place market order |
| `NewLimitOrder` | `symbolId tradeSide volume price` | Place limit order |
| `NewStopOrder` | `symbolId tradeSide volume price` | Place stop order |
| `ClosePosition` | `positionId volumeInUnits` | Close an open position |
| `CancelOrder` | `orderId` | Cancel a pending order |
| `OrderDetails` | `orderId` | Details of a specific order |
| `OrderListByPositionId` | `positionId` | Order history for a position |
| `DealOffsetList` | `dealId` | Offset deals for a deal |
| `GetPositionUnrealizedPnL` | — | Unrealised P&L for all open positions |
| `ProtoOAExpectedMarginReq` | `symbolId volumeInUnits` | Expected margin for a trade |

### Usage examples

```bash
# Get API version
curl -s "http://localhost:9009/get-data?command=ProtoOAVersionReq"

# List all symbols (find symbolIds)
curl -s "http://localhost:9009/get-data?command=ProtoOASymbolsListReq"

# Account details (balance, equity)
curl -s "http://localhost:9009/get-data?command=ProtoOATraderReq"

# Open positions + pending orders
curl -s "http://localhost:9009/get-data?command=ProtoOAReconcileReq"

# Close position 123456 (1000 units = 0.01 lot)
curl -s "http://localhost:9009/get-data?command=ClosePosition%20123456%201000"

# Cancel pending order 789
curl -s "http://localhost:9009/get-data?command=CancelOrder%20789"

# Unrealised P&L
curl -s "http://localhost:9009/get-data?command=GetPositionUnrealizedPnL"

# Expected margin for 1 lot of symbol 158
curl -s "http://localhost:9009/get-data?command=ProtoOAExpectedMarginReq%20158%20100000"
```
