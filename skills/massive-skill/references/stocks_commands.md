# Stocks Commands Reference

This document provides a reference for the stock-related commands available in the Polygon CLI.

## Commands

### stocks-aggs
Get aggregate bars (OHLCV) for a stock over a given date range.

**Usage:**
```bash
npx --yes massive stocks-aggs --ticker <ticker> --from <YYYY-MM-DD> --to <YYYY-MM-DD> [options]
```

**Parameters:**
- `--ticker` (required): Stock ticker symbol (e.g., AAPL).
- `--from` (required): Start date (YYYY-MM-DD).
- `--to` (required): End date (YYYY-MM-DD).
- `--multiplier` (number): Timespan multiplier (default: 1).
- `--timespan` (string): Timespan unit (default: 'day'). Values: `second`, `minute`, `hour`, `day`, `week`, `month`, `quarter`, `year`.
- `--adjusted` (boolean): Whether to adjust for splits (default: true).
- `--sort` (string): Sort order (default: 'asc'). Values: `asc`, `desc`.
- `--limit` (number): Max results (default: 120).

**Example:**
```bash
npx --yes massive stocks-aggs --ticker AAPL --from 2023-01-01 --to 2023-01-31 --timespan day --limit 10
```

### stocks-trades
Get trades for a stock ticker.

**Usage:**
```bash
npx --yes massive stocks-trades --ticker <ticker> [options]
```

**Parameters:**
- `--ticker` (required): Stock ticker symbol.
- `--timestamp` (string): Query by specific timestamp.
- `--timestamp-gte`, `--timestamp-gt`, `--timestamp-lte`, `--timestamp-lt` (string): Timestamp range filters.
- `--limit` (number): Max results (default: 10).
- `--sort` (string): Sort field (default: 'timestamp'). Values: `timestamp`.
- `--order` (string): Sort order (default: 'asc'). Values: `asc`, `desc`.

**Example:**
```bash
npx --yes massive stocks-trades --ticker AAPL --limit 5
```

### stocks-quotes
Get NBBO quotes for a stock ticker.

**Usage:**
```bash
npx --yes massive stocks-quotes --ticker <ticker> [options]
```

**Parameters:**
- `--ticker` (required): Stock ticker symbol.
- `--timestamp` (string): Query by specific timestamp.
- `--timestamp-gte`, `--timestamp-gt`, `--timestamp-lte`, `--timestamp-lt` (string): Timestamp range filters.
- `--limit` (number): Max results (default: 10).
- `--sort` (string): Sort field (default: 'timestamp'). Values: `timestamp`.
- `--order` (string): Sort order (default: 'asc'). Values: `asc`, `desc`.

**Example:**
```bash
npx --yes massive stocks-quotes --ticker AAPL --limit 5
```

### stocks-snapshot
Get the most recent snapshot for a stock ticker.

**Usage:**
```bash
npx --yes massive stocks-snapshot --ticker <ticker>
```

**Parameters:**
- `--ticker` (required): Stock ticker symbol.

**Example:**
```bash
npx --yes massive stocks-snapshot --ticker AAPL
```

### stocks-open-close
Get the daily open, close, and after-hours prices for a stock ticker on a specific date.

**Usage:**
```bash
npx --yes massive stocks-open-close --ticker <ticker> --date <YYYY-MM-DD> [options]
```

**Parameters:**
- `--ticker` (required): Stock ticker symbol.
- `--date` (required): Date of the requested open/close (YYYY-MM-DD).
- `--adjusted` (boolean): Whether to adjust for splits (default: true).

**Example:**
```bash
npx --yes massive stocks-open-close --ticker AAPL --date 2023-01-15
```

### stocks-previous
Get the previous day's open, high, low, and close (OHLC) for a stock ticker.

**Usage:**
```bash
npx --yes massive stocks-previous --ticker <ticker> [options]
```

**Parameters:**
- `--ticker` (required): Stock ticker symbol.
- `--adjusted` (boolean): Whether to adjust for splits (default: true).

**Example:**
```bash
npx --yes massive stocks-previous --ticker AAPL
```

### stocks-grouped
Get the daily open, high, low, and close (OHLC) for the entire stocks market.

**Usage:**
```bash
npx --yes massive stocks-grouped --date <YYYY-MM-DD> [options]
```

**Parameters:**
- `--date` (required): Date of the requested aggregates (YYYY-MM-DD).
- `--adjusted` (boolean): Whether to adjust for splits (default: true).
- `--include-otc` (boolean): Include OTC securities (default: false).

**Example:**
```bash
npx --yes massive stocks-grouped --date 2023-01-15
```

### stocks-sma
Get Simple Moving Average (SMA) for a stock ticker.

**Usage:**
```bash
npx --yes massive stocks-sma --ticker <ticker> [options]
```

**Parameters:**
- `--ticker` (required): Stock ticker symbol.
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
npx --yes massive stocks-sma --ticker AAPL --window 50
```

### stocks-ema
Get Exponential Moving Average (EMA) for a stock ticker.

**Usage:**
```bash
npx --yes massive stocks-ema --ticker <ticker> [options]
```

**Parameters:**
- `--ticker` (required): Stock ticker symbol.
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
npx --yes massive stocks-ema --ticker AAPL --window 50
```

### stocks-rsi
Get Relative Strength Index (RSI) for a stock ticker.

**Usage:**
```bash
npx --yes massive stocks-rsi --ticker <ticker> [options]
```

**Parameters:**
- `--ticker` (required): Stock ticker symbol.
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
npx --yes massive stocks-rsi --ticker AAPL --window 14
```

### stocks-macd
Get Moving Average Convergence/Divergence (MACD) for a stock ticker.

**Usage:**
```bash
npx --yes massive stocks-macd --ticker <ticker> [options]
```

**Parameters:**
- `--ticker` (required): Stock ticker symbol.
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
npx --yes massive stocks-macd --ticker AAPL
```

### last-trade
Get the most recent trade for a stock ticker.

**Usage:**
```bash
npx --yes massive last-trade --ticker <ticker>
```

**Parameters:**
- `--ticker` (required): Stock ticker symbol.

**Example:**
```bash
npx --yes massive last-trade --ticker AAPL
```

### last-quote
Get the most recent quote (NBBO) for a stock ticker.

**Usage:**
```bash
npx --yes massive last-quote --ticker <ticker>
```

**Parameters:**
- `--ticker` (required): Stock ticker symbol.

**Example:**
```bash
npx --yes massive last-quote --ticker AAPL
```
