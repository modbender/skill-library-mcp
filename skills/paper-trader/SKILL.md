---
name: paper-trading
description: Run a structured paper-trading loop with SQLite-backed event logging, position tracking, and PnL review. Use when opening/closing simulated trades, journaling thesis notes, checking portfolio status, or generating weekly performance summaries.
metadata:
  {
    "openclaw":
      {
        "emoji": "📓",
        "requires": { "bins": ["node"] },
      },
  }
---

# Paper Trading

SQLite-backed paper trading with immutable event logs.

Asset identity:

- `symbol` is required for trade/snapshot commands.
- `mint` is optional (`--mint <address>`), useful for token-address-specific tracking.
- If multiple positions share the same symbol, pass `--mint` for `close`/`set-levels` so you target the right one.

## When to Use

Use this skill when the user wants to:

- paper trade ideas before live capital
- track entries/exits/stops/takes over time
- compute realized and unrealized PnL
- keep a thesis journal and periodic review

## Database

Default DB path:

```bash
~/.openclaw/paper-trading.db
```

Override with `--db <path>`.

## Commands

Use the script:

```bash
node --experimental-strip-types {baseDir}/scripts/paper_trading.ts --help
```

Environment notes:

- No npm dependency is required for SQLite (uses `node:sqlite`).
- Node may print `ExperimentalWarning` for SQLite in current versions; this is expected.

### 1) Initialize account

```bash
node --experimental-strip-types {baseDir}/scripts/paper_trading.ts init \
  --account main \
  --name "Main Paper Account" \
  --base-currency USD \
  --starting-balance 10000
```

### 2) Log market snapshot (for unrealized PnL)

```bash
node --experimental-strip-types {baseDir}/scripts/paper_trading.ts snapshot \
  --symbol BTC \
  --mint 6p6xgHyF7AeE6TZk8x9mNQd2r2hH7r4mYJ8t6x6hYfSR \
  --price 62000 \
  --source manual
```

### 3) Open position

```bash
node --experimental-strip-types {baseDir}/scripts/paper_trading.ts open \
  --account main \
  --symbol BTC \
  --mint 6p6xgHyF7AeE6TZk8x9mNQd2r2hH7r4mYJ8t6x6hYfSR \
  --side LONG \
  --qty 0.1 \
  --price 62000 \
  --fee 4 \
  --stop-price 60500 \
  --take-price 65000 \
  --max-risk-pct 1.5 \
  --note "Breakout + volume confirmation"
```

### 4) Update stop/take

```bash
node --experimental-strip-types {baseDir}/scripts/paper_trading.ts set-levels \
  --account main \
  --symbol BTC \
  --mint 6p6xgHyF7AeE6TZk8x9mNQd2r2hH7r4mYJ8t6x6hYfSR \
  --side LONG \
  --stop-price 61200 \
  --take-price 66000 \
  --note "Move stop to reduce downside"
```

### 5) Close position

```bash
node --experimental-strip-types {baseDir}/scripts/paper_trading.ts close \
  --account main \
  --symbol BTC \
  --mint 6p6xgHyF7AeE6TZk8x9mNQd2r2hH7r4mYJ8t6x6hYfSR \
  --side LONG \
  --qty 0.05 \
  --price 63500 \
  --fee 3 \
  --note "Partial take profit"
```

### 6) Journal note

```bash
node --experimental-strip-types {baseDir}/scripts/paper_trading.ts note \
  --account main \
  --symbol BTC \
  --side LONG \
  --note "Invalidation if daily close < 61k" \
  --tags thesis risk macro
```

### 7) Portfolio status

```bash
node --experimental-strip-types {baseDir}/scripts/paper_trading.ts status --account main
node --experimental-strip-types {baseDir}/scripts/paper_trading.ts status --account main --format json --pretty
```

### 8) Weekly review

```bash
node --experimental-strip-types {baseDir}/scripts/paper_trading.ts review --account main
node --experimental-strip-types {baseDir}/scripts/paper_trading.ts review --account main --format json --pretty
```

## Workflow

1. Keep snapshots updated for symbols with open positions.
2. Open trades only with explicit stop and risk cap (`--max-risk-pct`).
3. Log every change as an event, do not edit old events.
4. Run `status` after each trade and `review` at week end.

## Notes

- Events are append-only in SQLite (`events` table).
- PnL is recomputed by replaying events.
- `status` uses the latest snapshot per `symbol + mint` pair for unrealized PnL.

## Validation

Run the full paper-trading test suite:

```bash
node --test {baseDir}/tests/paper_trading.test.mjs
```
