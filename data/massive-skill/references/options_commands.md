# Options Commands Reference

This document provides a reference for the options-related commands available in the Polygon CLI.

## Commands

### options-aggs
Get aggregate bars (OHLCV) for an options contract over a given date range.

**Usage:**
```bash
npx --yes massive options-aggs --ticker <ticker> --from <YYYY-MM-DD> --to <YYYY-MM-DD> [options]
```

**Parameters:**
- `--ticker` (required): Options ticker symbol (e.g., O:AAPL230616C00150000).
- `--from` (required): Start date (YYYY-MM-DD).
- `--to` (required): End date (YYYY-MM-DD).
- `--multiplier` (number): Timespan multiplier (default: 1).
- `--timespan` (string): Timespan unit (default: 'day'). Values: `second`, `minute`, `hour`, `day`, `week`, `month`, `quarter`, `year`.
- `--adjusted` (boolean): Whether to adjust for splits (default: true).
- `--sort` (string): Sort order (default: 'asc'). Values: `asc`, `desc`.
- `--limit` (number): Max results (default: 120).

**Example:**
```bash
npx --yes massive options-aggs --ticker O:AAPL230616C00150000 --from 2025-01-01 --to 2025-01-31 --timespan day --limit 10
```

### options-trades
Get trades for an options contract.

**Usage:**
```bash
npx --yes massive options-trades --ticker <ticker> [options]
```

**Parameters:**
- `--ticker` (required): Options ticker symbol.
- `--timestamp` (string): Query by specific timestamp.
- `--timestamp-gte`, `--timestamp-gt`, `--timestamp-lte`, `--timestamp-lt` (string): Timestamp range filters.
- `--limit` (number): Max results (default: 10).
- `--sort` (string): Sort field (default: 'timestamp'). Values: `timestamp`.
- `--order` (string): Sort order (default: 'asc'). Values: `asc`, `desc`.

**Example:**
```bash
npx --yes massive options-trades --ticker O:AAPL230616C00150000 --limit 5
```

### options-quotes
Get quotes for an options contract.

**Usage:**
```bash
npx --yes massive options-quotes --ticker <ticker> [options]
```

**Parameters:**
- `--ticker` (required): Options ticker symbol.
- `--timestamp` (string): Query by specific timestamp.
- `--timestamp-gte`, `--timestamp-gt`, `--timestamp-lte`, `--timestamp-lt` (string): Timestamp range filters.
- `--limit` (number): Max results (default: 10).
- `--sort` (string): Sort field (default: 'timestamp'). Values: `timestamp`.
- `--order` (string): Sort order (default: 'asc'). Values: `asc`, `desc`.

**Example:**
```bash
npx --yes massive options-quotes --ticker O:AAPL230616C00150000 --limit 5
```

### options-open-close
Get the daily open, close, and after-hours prices for an options contract on a specific date.

**Usage:**
```bash
npx --yes massive options-open-close --ticker <ticker> --date <YYYY-MM-DD> [options]
```

**Parameters:**
- `--ticker` (required): Options ticker symbol.
- `--date` (required): Date of the requested open/close (YYYY-MM-DD).
- `--adjusted` (boolean): Whether to adjust for splits (default: true).

**Example:**
```bash
npx --yes massive options-open-close --ticker O:AAPL230616C00150000 --date 2025-01-15
```

### options-chain
Get a snapshot of options chain for an underlying asset.

**Usage:**
```bash
npx --yes massive options-chain --underlying <ticker> [options]
```

**Parameters:**
- `--underlying` (required): Underlying ticker symbol (e.g., AAPL).
- `--strike` (number): Strike price.
- `--expiration` (string): Expiration date (YYYY-MM-DD).
- `--type` (string): Contract type. Values: `call`, `put`.
- `--order` (string): Sort order. Values: `asc`, `desc`.
- `--limit` (number): Max results (default: 10).
- `--sort` (string): Sort field.

**Example:**
```bash
npx --yes massive options-chain --underlying AAPL --type call
```

### options-contract
Get details for a specific options contract.

**Usage:**
```bash
npx --yes massive options-contract --underlying <ticker> --contract <contract_id>
```

**Parameters:**
- `--underlying` (required): Underlying ticker symbol.
- `--contract` (required): Options contract identifier (e.g., O:AAPL230616C00150000).

**Example:**
```bash
npx --yes massive options-contract --underlying AAPL --contract O:AAPL230616C00150000
```

### options-previous
Get the previous day's open, high, low, and close (OHLC) for an options contract.

**Usage:**
```bash
npx --yes massive options-previous --ticker <ticker> [options]
```

**Parameters:**
- `--ticker` (required): Options ticker symbol.
- `--adjusted` (boolean): Whether to adjust for splits (default: true).

**Example:**
```bash
npx --yes massive options-previous --ticker O:AAPL230616C00150000
```

### options-sma
Get Simple Moving Average (SMA) for an options contract.

**Usage:**
```bash
npx --yes massive options-sma --ticker <ticker> [options]
```

**Parameters:**
- `--ticker` (required): Options ticker symbol.
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
npx --yes massive options-sma --ticker O:AAPL230616C00150000 --window 50
```

### options-ema
Get Exponential Moving Average (EMA) for an options contract.

**Usage:**
```bash
npx --yes massive options-ema --ticker <ticker> [options]
```

**Parameters:**
- `--ticker` (required): Options ticker symbol.
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
npx --yes massive options-ema --ticker O:AAPL230616C00150000 --window 50
```

### options-rsi
Get Relative Strength Index (RSI) for an options contract.

**Usage:**
```bash
npx --yes massive options-rsi --ticker <ticker> [options]
```

**Parameters:**
- `--ticker` (required): Options ticker symbol.
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
npx --yes massive options-rsi --ticker O:AAPL230616C00150000 --window 14
```

### options-macd
Get Moving Average Convergence/Divergence (MACD) for an options contract.

**Usage:**
```bash
npx --yes massive options-macd --ticker <ticker> [options]
```

**Parameters:**
- `--ticker` (required): Options ticker symbol.
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
npx --yes massive options-macd --ticker O:AAPL230616C00150000
```

### last-options-trade
Get the most recent trade for an options contract.

**Usage:**
```bash
npx --yes massive last-options-trade --ticker <ticker>
```

**Parameters:**
- `--ticker` (required): Options ticker symbol.

**Example:**
```bash
npx --yes massive last-options-trade --ticker O:AAPL230616C00150000
```
