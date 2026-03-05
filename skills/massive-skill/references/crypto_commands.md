# Crypto Commands Reference

This document provides details on the parameters and enums used in the Polygon/Massive Crypto CLI commands.

## Enums

### Timespans
Used in `crypto-aggs`, `crypto-sma`, `crypto-ema`, `crypto-rsi`, `crypto-macd`:
- **GetCryptoAggregatesTimespanEnum**: `second`, `minute`, `hour`, `day`, `week`, `month`, `quarter`, `year`
- **GetCryptoSMATimespanEnum**: `minute`, `hour`, `day`, `week`, `month`, `quarter`, `year`
- **GetCryptoEMATimespanEnum**: `minute`, `hour`, `day`, `week`, `month`, `quarter`, `year`
- **GetCryptoRSITimespanEnum**: `minute`, `hour`, `day`, `week`, `month`, `quarter`, `year`
- **GetCryptoMACDTimespanEnum**: `minute`, `hour`, `day`, `week`, `month`, `quarter`, `year`

### Series Type
Used in technical indicators (`crypto-sma`, `crypto-ema`, `crypto-rsi`, `crypto-macd`) to specify which price to use:
- `open`, `high`, `low`, `close`

### Order / Sort
- **Sort**: `asc` (ascending), `desc` (descending)
- **Order**: `asc`, `desc`
- **Crypto Trades Sort**: `timestamp`

### Snapshot Direction
- `gainers`, `losers`

## Commands and Parameters

### `crypto-aggs`
- `ticker` (string, required): Crypto ticker (e.g., X:BTCUSD)
- `multiplier` (number): Timespan multiplier (default 1)
- `timespan` (enum): See Timespans above (default 'day')
- `from` (string, required): Start date (YYYY-MM-DD)
- `to` (string, required): End date (YYYY-MM-DD)
- `adjusted` (boolean): Adjust for splits (default true)
- `sort` (enum): Sort order (default 'asc')
- `limit` (number): Max results (default 120)

**Example**:
```bash
npx --yes massive crypto-aggs --ticker X:BTCUSD --from 2023-01-01 --to 2023-01-31 --timespan day
```

### `crypto-trades`
- `ticker` (string, required): Crypto ticker
- `timestamp` (string): Specific timestamp
- `timestamp-gte`, `timestamp-gt`, `timestamp-lte`, `timestamp-lt`: Timestamp range filters
- `order` (enum): Order of results
- `limit` (number): Max results
- `sort` (enum): Sort field

**Example**:
```bash
npx --yes massive crypto-trades --ticker X:BTCUSD --limit 5
```

### `crypto-snapshot`
- `ticker` (string, required): Crypto ticker

**Example**:
```bash
npx --yes massive crypto-snapshot --ticker X:BTCUSD
```

### `crypto-snapshot-direction`
- `direction` (enum, required): `gainers` or `losers`

**Example**:
```bash
npx --yes massive crypto-snapshot-direction --direction gainers
```

### `crypto-snapshot-tickers`
- `tickers` (comma-separated strings): List of tickers

**Example**:
```bash
npx --yes massive crypto-snapshot-tickers --tickers X:BTCUSD,X:ETHUSD
```

### `crypto-open-close`
- `from` (string, required): From symbol (e.g., BTC)
- `to` (string, required): To symbol (e.g., USD)
- `date` (string, required): Date (YYYY-MM-DD)
- `adjusted` (boolean): Adjust for splits

**Example**:
```bash
npx --yes massive crypto-open-close --from BTC --to USD --date 2023-01-01
```

### `crypto-previous`
- `ticker` (string, required): Crypto ticker
- `adjusted` (boolean): Adjust for splits

**Example**:
```bash
npx --yes massive crypto-previous --ticker X:BTCUSD
```

### `crypto-grouped`
- `date` (string, required): Date (YYYY-MM-DD)
- `adjusted` (boolean): Adjust for splits

**Example**:
```bash
npx --yes massive crypto-grouped --date 2023-01-01
```

### Technical Indicators (`crypto-sma`, `crypto-ema`, `crypto-rsi`, `crypto-macd`)
Common parameters:
- `ticker` (string, required)
- `timespan` (enum)
- `window` (number)
- `series-type` (enum)
- `expand-underlying` (boolean)
- `order` (enum)
- `limit` (number)
- Timestamp filters: `timestamp`, `timestamp-gte`, `timestamp-gt`, `timestamp-lte`, `timestamp-lt`

Specific to `crypto-macd`:
- `short-window` (number)
- `long-window` (number)
- `signal-window` (number)

**Example**:
```bash
# SMA
npx --yes massive crypto-sma --ticker X:BTCUSD --timespan day --window 50

# MACD
npx --yes massive crypto-macd --ticker X:BTCUSD --timespan day --short-window 12 --long-window 26 --signal-window 9
```

### `last-crypto-trade`
- `from` (string, required)
- `to` (string, required)

**Example**:
```bash
npx --yes massive last-crypto-trade --from BTC --to USD
```
