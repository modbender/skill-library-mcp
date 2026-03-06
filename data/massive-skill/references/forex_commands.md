# Forex Commands Reference

This document provides a reference for the forex-related commands available in the Polygon CLI.

## Commands

### forex-aggs
Get aggregate bars (OHLCV) for a forex pair over a given date range.

**Usage:**
```bash
npx --yes massive forex-aggs --ticker <ticker> --from <YYYY-MM-DD> --to <YYYY-MM-DD> [options]
```

**Parameters:**
- `--ticker` (required): Forex ticker symbol (e.g., C:EURUSD).
- `--from` (required): Start date (YYYY-MM-DD).
- `--to` (required): End date (YYYY-MM-DD).
- `--multiplier` (number): Timespan multiplier (default: 1).
- `--timespan` (string): Timespan unit (default: 'day'). Values: `second`, `minute`, `hour`, `day`, `week`, `month`, `quarter`, `year`.
- `--adjusted` (boolean): Whether to adjust for splits (default: true).
- `--sort` (string): Sort order (default: 'asc'). Values: `asc`, `desc`.
- `--limit` (number): Max results (default: 120).

**Example:**
```bash
npx --yes massive forex-aggs --ticker C:EURUSD --from 2025-01-01 --to 2025-01-31 --timespan day --limit 10
```

### forex-quotes
Get quotes for a forex pair.

**Usage:**
```bash
npx --yes massive forex-quotes --ticker <ticker> [options]
```

**Parameters:**
- `--ticker` (required): Forex ticker symbol.
- `--timestamp` (string): Query by specific timestamp.
- `--timestamp-gte`, `--timestamp-gt`, `--timestamp-lte`, `--timestamp-lt` (string): Timestamp range filters.
- `--limit` (number): Max results (default: 10).
- `--sort` (string): Sort field (default: 'timestamp'). Values: `timestamp`.
- `--order` (string): Sort order (default: 'asc'). Values: `asc`, `desc`.

**Example:**
```bash
npx --yes massive forex-quotes --ticker C:EURUSD --limit 5
```

### forex-snapshot
Get the most recent snapshot for a forex pair.

**Usage:**
```bash
npx --yes massive forex-snapshot --ticker <ticker>
```

**Parameters:**
- `--ticker` (required): Forex ticker symbol.

**Example:**
```bash
npx --yes massive forex-snapshot --ticker C:EURUSD
```

### forex-previous
Get the previous day's open, high, low, and close (OHLC) for a forex pair.

**Usage:**
```bash
npx --yes massive forex-previous --ticker <ticker> [options]
```

**Parameters:**
- `--ticker` (required): Forex ticker symbol.
- `--adjusted` (boolean): Whether to adjust for splits (default: true).

**Example:**
```bash
npx --yes massive forex-previous --ticker C:EURUSD
```

### forex-grouped
Get the daily open, high, low, and close (OHLC) for the entire forex market.

**Usage:**
```bash
npx --yes massive forex-grouped --date <YYYY-MM-DD> [options]
```

**Parameters:**
- `--date` (required): Date of the requested aggregates (YYYY-MM-DD).
- `--adjusted` (boolean): Whether to adjust for splits (default: true).

**Example:**
```bash
npx --yes massive forex-grouped --date 2025-01-15
```

### forex-sma
Get Simple Moving Average (SMA) for a forex pair.

**Usage:**
```bash
npx --yes massive forex-sma --ticker <ticker> [options]
```

**Parameters:**
- `--ticker` (required): Forex ticker symbol.
- `--timestamp` (string): Query by specific timestamp.
- `--timestamp-gte`, `--timestamp-gt`, `--timestamp-lte`, `--timestamp-lt` (string): Timestamp range filters.
- `--timespan` (string): Timespan unit (default: 'day'). Values: `minute`, `hour`, `day`, `week`, `month`, `quarter`, `year`.
- `--adjusted` (boolean): Whether to adjust for splits (default: true).
- `--window` (number): Window size (default: 50).
- `--series-type` (string): Price type to use. Values: `open`, `high`, `low`, `close`.
- `--expand-underlying` (boolean): Include underlying aggregates.
- `--order` (string): Sort order. Values: `asc`, `desc`.
- `--limit` (number): Max results (default: 10).

**Example:**
```bash
npx --yes massive forex-sma --ticker C:EURUSD --window 50
```

### forex-ema
Get Exponential Moving Average (EMA) for a forex pair.

**Usage:**
```bash
npx --yes massive forex-ema --ticker <ticker> [options]
```

**Parameters:**
- `--ticker` (required): Forex ticker symbol.
- `--timestamp` (string): Query by specific timestamp.
- `--timestamp-gte`, `--timestamp-gt`, `--timestamp-lte`, `--timestamp-lt` (string): Timestamp range filters.
- `--timespan` (string): Timespan unit (default: 'day'). Values: `minute`, `hour`, `day`, `week`, `month`, `quarter`, `year`.
- `--adjusted` (boolean): Whether to adjust for splits (default: true).
- `--window` (number): Window size (default: 50).
- `--series-type` (string): Price type to use. Values: `open`, `high`, `low`, `close`.
- `--expand-underlying` (boolean): Include underlying aggregates.
- `--order` (string): Sort order. Values: `asc`, `desc`.
- `--limit` (number): Max results (default: 10).

**Example:**
```bash
npx --yes massive forex-ema --ticker C:EURUSD --window 50
```

### forex-rsi
Get Relative Strength Index (RSI) for a forex pair.

**Usage:**
```bash
npx --yes massive forex-rsi --ticker <ticker> [options]
```

**Parameters:**
- `--ticker` (required): Forex ticker symbol.
- `--timestamp` (string): Query by specific timestamp.
- `--timestamp-gte`, `--timestamp-gt`, `--timestamp-lte`, `--timestamp-lt` (string): Timestamp range filters.
- `--timespan` (string): Timespan unit (default: 'day'). Values: `minute`, `hour`, `day`, `week`, `month`, `quarter`, `year`.
- `--adjusted` (boolean): Whether to adjust for splits (default: true).
- `--window` (number): Window size (default: 14).
- `--series-type` (string): Price type to use. Values: `open`, `high`, `low`, `close`.
- `--expand-underlying` (boolean): Include underlying aggregates.
- `--order` (string): Sort order. Values: `asc`, `desc`.
- `--limit` (number): Max results (default: 10).

**Example:**
```bash
npx --yes massive forex-rsi --ticker C:EURUSD --window 14
```

### forex-macd
Get Moving Average Convergence/Divergence (MACD) for a forex pair.

**Usage:**
```bash
npx --yes massive forex-macd --ticker <ticker> [options]
```

**Parameters:**
- `--ticker` (required): Forex ticker symbol.
- `--timestamp` (string): Query by specific timestamp.
- `--timestamp-gte`, `--timestamp-gt`, `--timestamp-lte`, `--timestamp-lt` (string): Timestamp range filters.
- `--timespan` (string): Timespan unit (default: 'day'). Values: `minute`, `hour`, `day`, `week`, `month`, `quarter`, `year`.
- `--adjusted` (boolean): Whether to adjust for splits (default: true).
- `--short-window` (number): Short window size.
- `--long-window` (number): Long window size.
- `--signal-window` (number): Signal window size.
- `--series-type` (string): Price type to use. Values: `open`, `high`, `low`, `close`.
- `--expand-underlying` (boolean): Include underlying aggregates.
- `--order` (string): Sort order. Values: `asc`, `desc`.
- `--limit` (number): Max results (default: 10).

**Example:**
```bash
npx --yes massive forex-macd --ticker C:EURUSD
```

### currency-conversion
Get currency conversion.

**Usage:**
```bash
npx --yes massive currency-conversion --from <currency> --to <currency> [options]
```

**Parameters:**
- `--from` (required): From currency (e.g., USD).
- `--to` (required): To currency (e.g., EUR).
- `--amount` (number): Amount to convert.
- `--precision` (number): Decimal precision.

**Example:**
```bash
npx --yes massive currency-conversion --from USD --to EUR --amount 100
```

### last-forex-quote
Get the last quote for a forex pair.

**Usage:**
```bash
npx --yes massive last-forex-quote --from <currency> --to <currency>
```

**Parameters:**
- `--from` (required): From currency (e.g., EUR).
- `--to` (required): To currency (e.g., USD).

**Example:**
```bash
npx --yes massive last-forex-quote --from EUR --to USD
```
