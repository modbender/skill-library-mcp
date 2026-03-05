---
name: finam
description: Execute trades, manage portfolios, access real-time market data, browse market assets, scan volatility, and answer questions about Finam Trade API
metadata: '{"openclaw": {"emoji": "📈", "homepage": "https://tradeapi.finam.ru/", "requires": {"bins": ["curl", "jq", "python3"], "env": ["FINAM_API_KEY", "FINAM_ACCOUNT_ID"]}}}'
---

# Finam Trade API Skill

## Setup

**Prerequisites:** `$FINAM_API_KEY` and `$FINAM_ACCOUNT_ID` must be set in your environment.

If not configured by environment, follow these steps:
1. Register and obtain your API Key from [tokens page](https://tradeapi.finam.ru/docs/tokens)
2. Obtain your Account ID from your [Finam account dashboard](https://lk.finam.ru/)
3. Set environment variables:
```shell
export FINAM_API_KEY="your_api_key_here"
export FINAM_ACCOUNT_ID="your_account_id_here"
```

Obtain JWT token before using the API:

```shell
export FINAM_JWT_TOKEN=$(curl -sL "https://api.finam.ru/v1/sessions" \
--header "Content-Type: application/json" \
--data '{"secret": "'"$FINAM_API_KEY"'"}' | jq -r '.token')
```

**Note:** Token expires after 15 minutes. Re-run this command if you receive authentication errors.

## Market assets

### List Available Exchanges and Equities

**Symbol Format:** All symbols must be in `ticker@mic` format (e.g., `SBER@MISX`)
**Base MIC Codes:**
- `MISX` - Moscow Exchange
- `RUSX` - RTS
- `XNGS` - NASDAQ/NGS
- `XNMS` - NASDAQ/NNS
- `XNYS` - New York Stock Exchange

View all supported exchanges with their MIC codes:

```shell
jq -r '.exchanges[] | "\(.mic) - \(.name)"' assets/exchanges.json
```

List stocks available on a specific exchange:

```shell
MIC="MISX"
LIMIT=20
jq -r ".$MIC[:$LIMIT] | .[] | \"\(.symbol) - \(.name)\"" assets/equities.json
```

### Search Assets by Name

Find a stock by name (case-insensitive) across all exchanges:

```shell
QUERY="apple"
jq -r --arg q "$QUERY" 'to_entries[] | .value[] | select(.name | ascii_downcase | contains($q)) | "\(.symbol) - \(.name)"' assets/equities.json
```

### Get Top N Stocks by Volume

Pre-ranked lists of the 100 most liquid equities for each market, ordered by trading volume descending:

```shell
N=10
jq -r ".[:$N] | .[] | \"\(.ticker) - \(.name)\"" assets/top_ru_equities.json
```

```shell
N=10
jq -r ".[:$N] | .[] | \"\(.ticker) - \(.name)\"" assets/top_us_equities.json
```

## Account Management

### Get Account Portfolio

Retrieve portfolio information including positions, balances, and P&L:

```shell
curl -sL "https://api.finam.ru/v1/accounts/$FINAM_ACCOUNT_ID" \
  --header "Authorization: $FINAM_JWT_TOKEN" | jq
```

## Market Data

### Get Latest Quote

Retrieve current bid/ask prices and last trade:

```shell
SYMBOL="SBER@MISX"
curl -sL "https://api.finam.ru/v1/instruments/$SYMBOL/quotes/latest" \
  --header "Authorization: $FINAM_JWT_TOKEN" | jq
```

### Get Order Book (Depth)

View current market depth with bid/ask levels:

```shell
SYMBOL="SBER@MISX"
curl -sL "https://api.finam.ru/v1/instruments/$SYMBOL/orderbook" \
  --header "Authorization: $FINAM_JWT_TOKEN" | jq
```

### Get Recent Trades

List the most recent executed trades:

```shell
SYMBOL="SBER@MISX"
curl -sL "https://api.finam.ru/v1/instruments/$SYMBOL/trades/latest" \
  --header "Authorization: $FINAM_JWT_TOKEN" | jq
```

### Get Historical Candles (OHLCV)

Retrieve historical price data with specified timeframe:

```shell
SYMBOL="SBER@MISX"
TIMEFRAME="TIME_FRAME_D"
START_TIME="2024-01-01T00:00:00Z"
END_TIME="2024-04-01T00:00:00Z"
curl -sL "https://api.finam.ru/v1/instruments/$SYMBOL/bars?timeframe=$TIMEFRAME&interval.startTime=$START_TIME&interval.endTime=$END_TIME" \
  --header "Authorization: $FINAM_JWT_TOKEN" | jq
```

**Available Timeframes:**
- `TIME_FRAME_M1`, `M5`, `M15`, `M30` - Minutes (1, 5, 15, 30)
- `TIME_FRAME_H1`, `H2`, `H4`, `H8` - Hours (1, 2, 4, 8)
- `TIME_FRAME_D` - Daily
- `TIME_FRAME_W` - Weekly
- `TIME_FRAME_MN` - Monthly
- `TIME_FRAME_QR` - Quarterly

**Date Format (RFC 3339):**
- Format: `YYYY-MM-DDTHH:MM:SSZ` or `YYYY-MM-DDTHH:MM:SS+HH:MM`
- `startTime` - Inclusive (interval start, included in results)
- `endTime` - Exclusive (interval end, NOT included in results)
- Examples:
  - `2024-01-15T10:30:00Z` (UTC)
  - `2024-01-15T10:30:00+03:00` (Moscow time, UTC+3)


## News

### Get Latest Market News

Fetch and display the latest news headlines. No JWT token required.

Russian market news
```shell
curl -sL "https://www.finam.ru/analysis/conews/rsspoint/" | python3 -c "
import sys, xml.etree.ElementTree as ET
root = ET.parse(sys.stdin).getroot()
for item in reversed(root.findall('.//item')):
    print(f'* {item.findtext('title','')}. {item.findtext('description','').split('...')[0]}')
"
```

US market news
```shell
curl -sL "https://www.finam.ru/international/advanced/rsspoint/" | python3 -c "
import sys, xml.etree.ElementTree as ET
root = ET.parse(sys.stdin).getroot()
for item in reversed(root.findall('.//item')):
    print(f'* {item.findtext('title','')}. {item.findtext('description','').split('...')[0]}')
"
```

**Parameters:**
- Change `[:10]` to any number to control how many headlines to display

## Order Management

> **IMPORTANT:** Before placing or cancelling any order, you MUST explicitly confirm the details with the user and receive their approval. State the full order parameters (symbol, side, quantity, type, price) and wait for confirmation before executing.

### Place Order

**Order Types:**
- `ORDER_TYPE_MARKET` - Market order (executes immediately, no `limitPrice` required)
- `ORDER_TYPE_LIMIT` - Limit order (requires `limitPrice`)

```shell
curl -sL "https://api.finam.ru/v1/accounts/$FINAM_ACCOUNT_ID/orders" \
  --header "Authorization: $FINAM_JWT_TOKEN" \
  --header "Content-Type: application/json" \
  --data "$(jq -n \
    --arg symbol   "SBER@MISX" \
    --arg quantity "10" \
    --arg side     "SIDE_BUY" \
    --arg type     "ORDER_TYPE_LIMIT" \
    --arg price    "310.50" \
    '{symbol: $symbol, quantity: {value: $quantity}, side: $side, type: $type, limitPrice: {value: $price}}')" \
  | jq
```

**Parameters:**
- `symbol` - Instrument (e.g., `SBER@MISX`)
- `quantity.value` - Number of shares/contracts
- `side` - `SIDE_BUY` or `SIDE_SELL`
- `type` - `ORDER_TYPE_MARKET` or `ORDER_TYPE_LIMIT`
- `limitPrice` - Only for `ORDER_TYPE_LIMIT` (omit for market orders)

### Get Order Status

Check the status of a specific order:

```shell
ORDER_ID="12345678"
curl -sL "https://api.finam.ru/v1/accounts/$FINAM_ACCOUNT_ID/orders/$ORDER_ID" \
  --header "Authorization: $FINAM_JWT_TOKEN" | jq
```

### Cancel Order

Cancel a pending order:

```shell
ORDER_ID="12345678"
curl -sL --request DELETE "https://api.finam.ru/v1/accounts/$FINAM_ACCOUNT_ID/orders/$ORDER_ID" \
  --header "Authorization: $FINAM_JWT_TOKEN" | jq
```

## Scripts

### Volatility Scanner

Scans the top-100 stocks for a given market and prints the most volatile ones based on annualized historical volatility (close-to-close, last 60 days).

**Usage:**
```shell
python3 scripts/volatility.py [ru|us] [N]
```

**Arguments:**
- `ru` / `us` — market to scan (default: `ru`)
- `N` — number of top results to display (default: `10`)

**Examples:**
```shell
# Top 10 most volatile Russian stocks
python3 scripts/volatility.py ru 10

# Top 5 most volatile US stocks
python3 scripts/volatility.py us 5
```

See [API Reference](assets/openapi.json) for full Finam Trade API details.