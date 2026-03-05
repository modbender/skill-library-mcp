# Indices Commands Reference

This document provides a reference for the indices-related commands available in the Polygon CLI.

## Commands

### indices-aggs
Get aggregate bars (OHLCV) for an index over a given date range.

**Usage:**
```bash
npx --yes massive indices-aggs --ticker <ticker> --from <YYYY-MM-DD> --to <YYYY-MM-DD> [options]
```

**Parameters:**
- `--ticker` (required): Index ticker symbol (e.g., I:SPX).
- `--from` (required): Start date (YYYY-MM-DD).
- `--to` (required): End date (YYYY-MM-DD).
- `--multiplier` (number): Timespan multiplier (default: 1).
- `--timespan` (string): Timespan unit (default: 'day'). Values: `second`, `minute`, `hour`, `day`, `week`, `month`, `quarter`, `year`.
- `--sort` (string): Sort order (default: 'asc'). Values: `asc`, `desc`.
- `--limit` (number): Max results (default: 120).

**Example:**
```bash
npx --yes massive indices-aggs --ticker I:SPX --from 2025-01-01 --to 2025-01-31 --timespan day --limit 10
```

### indices-open-close
Get the daily open, close, and after-hours prices for an index on a specific date.

**Usage:**
```bash
npx --yes massive indices-open-close --ticker <ticker> --date <YYYY-MM-DD>
```

**Parameters:**
- `--ticker` (required): Index ticker symbol.
- `--date` (required): Date of the requested open/close (YYYY-MM-DD).

**Example:**
```bash
npx --yes massive indices-open-close --ticker I:SPX --date 2025-01-15
```

### indices-snapshot
Get the most recent snapshot for an index.

**Usage:**
```bash
npx --yes massive indices-snapshot [--ticker <ticker>]
```

**Parameters:**
- `--ticker`: Index ticker symbol (e.g., I:SPX).

**Example:**
```bash
npx --yes massive indices-snapshot --ticker I:SPX
```

### indices-previous
Get the previous day's open, high, low, and close (OHLC) for an index.

**Usage:**
```bash
npx --yes massive indices-previous --ticker <ticker>
```

**Parameters:**
- `--ticker` (required): Index ticker symbol.

**Example:**
```bash
npx --yes massive indices-previous --ticker I:SPX
```

### indices-sma
Get Simple Moving Average (SMA) for an index.

**Usage:**
```bash
npx --yes massive indices-sma --ticker <ticker> [options]
```

**Parameters:**
- `--ticker` (required): Index ticker symbol.
- `--timestamp` (string): Query by specific timestamp.
- `--timespan` (string): Timespan unit (default: 'day'). Values: `minute`, `hour`, `day`, `week`, `month`, `quarter`, `year`.
- `--adjusted` (boolean): Whether to adjust for splits (default: true).
- `--window` (number): Window size (default: 50).
- `--series-type` (string): Price type to use. Values: `open`, `high`, `low`, `close`.
- `--expand-underlying` (boolean): Include underlying aggregates.
- `--order` (string): Sort order. Values: `asc`, `desc`.
- `--limit` (number): Max results (default: 10).

**Example:**
```bash
npx --yes massive indices-sma --ticker I:SPX --window 50
```

### indices-ema
Get Exponential Moving Average (EMA) for an index.

**Usage:**
```bash
npx --yes massive indices-ema --ticker <ticker> [options]
```

**Parameters:**
- `--ticker` (required): Index ticker symbol.
- `--timestamp` (string): Query by specific timestamp.
- `--timespan` (string): Timespan unit (default: 'day'). Values: `minute`, `hour`, `day`, `week`, `month`, `quarter`, `year`.
- `--adjusted` (boolean): Whether to adjust for splits (default: true).
- `--window` (number): Window size (default: 50).
- `--series-type` (string): Price type to use. Values: `open`, `high`, `low`, `close`.
- `--expand-underlying` (boolean): Include underlying aggregates.
- `--order` (string): Sort order. Values: `asc`, `desc`.
- `--limit` (number): Max results (default: 10).

**Example:**
```bash
npx --yes massive indices-ema --ticker I:SPX --window 50
```

### indices-rsi
Get Relative Strength Index (RSI) for an index.

**Usage:**
```bash
npx --yes massive indices-rsi --ticker <ticker> [options]
```

**Parameters:**
- `--ticker` (required): Index ticker symbol.
- `--timestamp` (string): Query by specific timestamp.
- `--timespan` (string): Timespan unit (default: 'day'). Values: `minute`, `hour`, `day`, `week`, `month`, `quarter`, `year`.
- `--adjusted` (boolean): Whether to adjust for splits (default: true).
- `--window` (number): Window size (default: 14).
- `--series-type` (string): Price type to use. Values: `open`, `high`, `low`, `close`.
- `--expand-underlying` (boolean): Include underlying aggregates.
- `--order` (string): Sort order. Values: `asc`, `desc`.
- `--limit` (number): Max results (default: 10).

**Example:**
```bash
npx --yes massive indices-rsi --ticker I:SPX --window 14
```

### indices-macd
Get Moving Average Convergence/Divergence (MACD) for an index.

**Usage:**
```bash
npx --yes massive indices-macd --ticker <ticker> [options]
```

**Parameters:**
- `--ticker` (required): Index ticker symbol.
- `--timestamp` (string): Query by specific timestamp.
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
npx --yes massive indices-macd --ticker I:SPX
```
