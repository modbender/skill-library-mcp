---
name: okx-exchange
description: >
  OKX quantitative trading agent. Supports spot, USDT-M perpetual swap, and coin-M futures.
  Strategies: grid trading, trend following (MA/RSI/MACD), spot-futures arbitrage.
  Use for: (1) market data queries, (2) account/portfolio management, (3) order execution,
  (4) automated strategy execution, (5) risk management, (6) performance reports,
  (7) algo orders (OCO/conditional TP+SL), (8) liquidation risk alerts.
  Triggers: OKX trading, buy/sell crypto, grid strategy, arbitrage, trend signal,
  check balance, check positions, place order, stop loss, take profit,
  BTC price, ETH price, crypto price, coin price, bitcoin price,
  change interval, change stop loss, change take profit, monitoring frequency,
  algo order, oco order, conditional order, batch order, liquidation risk.
---

# OKX Exchange Skill

Quantitative trading agent for OKX exchange via the official V5 API.

**API Docs:** https://www.okx.com/docs-v5/en/

## Setup (First Time)

```bash
# 1. Add credentials to .env
cat >> ~/.openclaw/workspace/.env << 'EOF'
OKX_API_KEY=your_key
OKX_SECRET_KEY=your_secret
OKX_PASSPHRASE=your_passphrase
OKX_SIMULATED=1
EOF

# 2. Run setup
cd ~/.openclaw/workspace/skills/okx-exchange/scripts
python setup.py
```

**Important:** `OKX_SIMULATED=1` = paper trading (safe). Set to `0` for live trading.

## Session Init

On every session, load credentials first:
```bash
source ~/.openclaw/workspace/.env
cd ~/.openclaw/workspace/skills/okx-exchange/scripts
```

## Unified CLI (Recommended)

Use `okx.py` as the single entry point for all commands:
```bash
python3 okx.py help           # Show all commands
python3 okx.py account        # Portfolio overview
python3 okx.py buy BTC-USDT market 0.01
python3 okx.py trend analyze BTC-USDT-SWAP
```

All individual scripts remain usable directly, but `okx.py` is preferred for agent use.

## Instrument ID Format

| Type | Format | Example |
|------|--------|---------|
| Spot | `{BASE}-{QUOTE}` | `BTC-USDT` |
| Perpetual Swap | `{BASE}-{QUOTE}-SWAP` | `BTC-USDT-SWAP` |
| Futures | `{BASE}-{QUOTE}-{EXPIRY}` | `BTC-USDT-250328` |

`tdMode`: `cash` (spot), `cross` (cross-margin), `isolated` (isolated-margin)

## Account & Portfolio

```bash
python3 okx.py account                          # Full portfolio summary
python3 okx.py account balance                  # Balances only
python3 okx.py account balance USDT             # Specific currency
python3 okx.py account positions                # All positions
python3 okx.py account orders                   # Pending orders
python3 okx.py account history                  # Filled order history (SPOT)
python3 okx.py account history SWAP             # Perpetual swap order history
python3 okx.py account history SPOT BTC-USDT    # History for specific symbol
```

## Trading Mode (Live / Demo)

```bash
python3 okx.py mode           # Show current mode
python3 okx.py mode demo      # Switch to paper trading (safe)
python3 okx.py mode live      # Switch to live trading (requires confirmation + LIVE credentials)
```

Live credentials use separate env vars:
```
OKX_API_KEY_LIVE / OKX_SECRET_KEY_LIVE / OKX_PASSPHRASE_LIVE
```

## Order Execution

```bash
# Spot market buy
python3 okx.py buy BTC-USDT market 0.01

# Spot limit sell
python3 okx.py sell BTC-USDT limit 0.01 --px 50000

# Perpetual swap — long with TP/SL (attached to the order)
python3 okx.py buy BTC-USDT-SWAP market 1 --td cross --pos long --tp 55000 --sl 42000

# Perpetual swap — short
python3 okx.py sell BTC-USDT-SWAP market 1 --td cross --pos short

# Close position (reduce-only)
python3 okx.py sell BTC-USDT-SWAP market 1 --td cross --pos long --reduce

# Cancel order
python3 okx.py cancel BTC-USDT <ord_id>

# Cancel all orders for symbol
python3 okx.py cancel-all BTC-USDT

# Set leverage
python3 okx.py leverage BTC-USDT-SWAP 10 --td cross

# Transfer funds between accounts (6=Funding, 18=Trading)
python3 okx.py transfer USDT 500 funding trading   # Funding → Trading
python3 okx.py transfer USDT 500 trading funding   # Trading → Funding
```

Skip confirmation prompt (for automation):
```bash
python3 okx.py buy BTC-USDT market 0.01 --no-confirm
```

## Algo Orders (Standalone TP/SL — for existing positions)

Use when a position is already open and you want to add a stop-loss or take-profit separately.
Unlike `--tp/--sl` flags (which attach to the entry order), algo orders are independent.

```bash
# OCO: TP + SL together — whichever triggers first cancels the other
python3 okx.py algo oco BTC-USDT-SWAP 1 --tp 55000 --sl 45000 --td cross --pos long --reduce

# Conditional: single stop-loss only
python3 okx.py algo stop BTC-USDT-SWAP 1 --sl 45000 --td cross --reduce

# List all pending algo orders
python3 okx.py algo list
python3 okx.py algo list BTC-USDT-SWAP   # filter by instrument

# Cancel a specific algo order
python3 okx.py algo cancel BTC-USDT-SWAP <algo_id>
```

**When to use which:**
- `--tp/--sl` at order time → atomic, guaranteed to attach, best for new entries
- `algo oco` → add/replace TP+SL after entry, or adjust levels mid-trade

## Strategies

### Trend Following (MA + RSI + MACD)

```bash
# Analyze only (no trade)
python3 okx.py trend analyze BTC-USDT-SWAP --bar 1H

# Run with auto-execution
python3 okx.py trend run BTC-USDT-SWAP 1 --bar 4H --tp 0.05 --sl 0.03 --td cross --pos long

# Dry run (analysis only, no trade)
python3 okx.py trend run BTC-USDT-SWAP 1 --dry
```

Signal logic:
- **BUY**: MA_fast > MA_slow + RSI < 70 + MACD histogram > 0
- **SELL**: MA_fast < MA_slow + RSI > 30 + MACD histogram < 0

### Grid Trading

```bash
# Setup grid: BTC-USDT, range 40000-50000, 10 grids, 1000 USDT total
python3 okx.py grid setup BTC-USDT 40000 50000 10 1000

# Check and rebalance filled orders (run periodically)
python3 okx.py grid check BTC-USDT

# Stop and cancel all grid orders
python3 okx.py grid stop BTC-USDT
```

### Spot-Futures Arbitrage

```bash
# Scan all pairs for opportunities
python3 okx.py arb scan

# Check specific pair basis
python3 okx.py arb basis BTC-USDT BTC-USDT-SWAP

# Open arbitrage position (buy spot + short swap)
python3 okx.py arb open BTC-USDT BTC-USDT-SWAP 1000 --min-basis 0.1

# Close arbitrage position when basis converges
python3 okx.py arb close BTC-USDT BTC-USDT-SWAP 0.01 1 --max-basis 0.02
```

## Snapshot Report

Fetches live data from the API on every run, persists the snapshot, and outputs a full report with a **real historical tracking table**.

```bash
python3 okx.py snapshot
```

Output includes:
- Total equity, initial capital, % change (relative to first snapshot)
- Available USDT, major holdings
- Contract positions (entry price, mark price, unrealized PnL, liquidation distance)
- Historical tracking table (from `memory/okx-monitor-snapshots.json`, up to 48 entries)

**All figures are sourced directly from the OKX API — no estimates or fabricated values.**

## Automated Monitoring (Cron)

```bash
# Default: sl-tp every 5 minutes, scan every 30 minutes
bash scripts/cron_setup.sh setup

# Custom intervals (dynamic parameters)
bash scripts/cron_setup.sh setup 1m       # sl-tp every 1 minute
bash scripts/cron_setup.sh setup 10m 1h   # sl-tp every 10 minutes, scan every 1 hour

# Stop all jobs
bash scripts/cron_setup.sh teardown

# Show status
bash scripts/cron_setup.sh status
```

Cron jobs:
- `okx-sl-tp` — periodically runs `snapshot` + `monitor sl-tp`, reports live data
- `okx-scan`  — periodically runs `monitor scan`, reports strategy signals

### Adjust cron interval (via user instruction)

If the user asks to change the monitoring frequency (e.g. "change to every 10 minutes"):

```bash
# Find the cron job ID first
openclaw cron list

# Then edit the interval (replace <id> with the okx-sl-tp job ID)
openclaw cron edit <id> --every 10m   # e.g. 1m, 5m, 15m, 30m, 1h
```

### Manual monitor run

```bash
python3 okx.py snapshot             # Full account snapshot report (with history — recommended)
python3 okx.py monitor              # SL/TP check + strategy scan + liquidation risk
python3 okx.py monitor sl-tp        # Only SL/TP check
python3 okx.py monitor scan         # Only strategy scan
python3 okx.py monitor liq-risk     # Liquidation risk check (default: alert if within 10%)
python3 okx.py monitor liq-risk 5   # Alert if mark price within 5% of liquidation price
```

### CRITICAL: Cron reporting rules

**Every cron report MUST call the scripts first. NEVER fabricate, estimate, or reuse previous numbers.**

Recommended single command for cron:
```bash
cd ~/.openclaw/workspace/skills/okx-exchange/scripts
python3 okx.py snapshot
python3 okx.py monitor sl-tp
```

`snapshot` automatically saves the snapshot and generates a report with historical tracking. Forward the output verbatim — do not add, remove, or rephrase any content.

Report only what the scripts actually output. If a script returns an error, report the error — do not substitute with previously seen values.

**Why this matters:** Each cron run is an isolated session with no memory of previous runs. Any numbers not fetched from the API in this session are either fabricated or stale.

## Performance Report

```bash
python3 okx.py report daily    # Today's P&L summary
python3 okx.py report weekly   # Last 7 days
python3 okx.py report all      # All-time
```

Output includes: trade count, win rate, total P&L, best/worst trade, and top-5 coin breakdown.

## Configuration

View or update preferences without editing JSON directly:
```bash
python3 okx.py prefs show
python3 okx.py prefs set auto_trade true
python3 okx.py prefs set stop_loss_pct 3.0
python3 okx.py prefs set watchlist BTC-USDT-SWAP,ETH-USDT-SWAP,SOL-USDT-SWAP
```

Full preferences schema (`~/.openclaw/workspace/memory/okx-trading-preferences.json`):

```json
{
  "max_order_usd": 100,
  "max_leverage": 10,
  "price_impact_warn": 0.005,
  "price_impact_abort": 0.01,
  "require_confirm": true,
  "stop_loss_pct": 5.0,
  "take_profit_pct": 10.0,
  "auto_trade": false,
  "max_position_usd": 100,
  "max_daily_trades": 10,
  "default_sz": "0.01",
  "strategies": ["trend"],
  "watchlist": ["BTC-USDT-SWAP", "ETH-USDT-SWAP"]
}
```

| Parameter | Default | Description |
|-----------|---------|-------------|
| `max_order_usd` | 100 | Max USD per single order |
| `max_leverage` | 10 | Max allowed leverage |
| `price_impact_warn` | 0.005 | Warn if market order impact > 0.5% |
| `price_impact_abort` | 0.01 | Abort if market order impact > 1% |
| `require_confirm` | true | Prompt before placing orders |
| `stop_loss_pct` | 5.0 | Auto stop-loss at -X% unrealized PnL |
| `take_profit_pct` | 10.0 | Auto take-profit at +X% unrealized PnL |
| `auto_trade` | false | Execute trades automatically (no confirmation) |
| `max_position_usd` | 100 | Max USD per position |
| `max_daily_trades` | 10 | Max auto-trades per day |
| `default_sz` | "0.01" | Default size for auto-trading |
| `strategies` | ["trend"] | Active strategies: trend / arbitrage |
| `watchlist` | [...] | Instruments for monitor scan |

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OKX_API_KEY` | — | Demo API key |
| `OKX_SECRET_KEY` | — | Demo API secret |
| `OKX_PASSPHRASE` | — | Demo API passphrase |
| `OKX_API_KEY_LIVE` | — | Live API key (used when `mode=live`) |
| `OKX_SECRET_KEY_LIVE` | — | Live API secret |
| `OKX_PASSPHRASE_LIVE` | — | Live API passphrase |
| `OKX_SIMULATED` | `0` | Set `1` for paper trading (demo account) |
| `OKX_WS` | `0` | Set `1` to enable WebSocket feed (real-time cache for tickers/candles/account/positions) |
| `OKX_API_URL` | `https://www.okx.com` | Override API base URL |
| `OKX_LOG_LEVEL` | `INFO` | `DEBUG` / `INFO` / `WARNING` / `ERROR` |
| `OKX_LOG_FORMAT` | `text` | `text` or `json` (structured logging) |
| `OKX_CRON_MODE` | `0` | Set `1` to suppress INFO output (for cron) |

### WebSocket Mode (`OKX_WS=1`)

When enabled, a background thread maintains real-time caches:
- **Public feed**: tickers, candles — `OKXClient.ticker()` / `candles()` read from cache first
- **Private feed**: account balances, positions, orders — `balance()` / `positions()` read from cache first
- REST API is used as fallback when cache is empty or WS is disabled

## Trading Rules

Before making any buy/sell decision, read and apply the principles in:
```
docs/trading-rules.md
```

These rules define how to observe the market, weigh signals, size positions, and learn from outcomes.
They do not prescribe a fixed strategy — the agent is expected to adapt its approach based on what the market is actually showing.

## Safety Rules

1. **Always confirm before placing orders** unless `auto_trade=true` or `--no-confirm`
2. **Price impact check**: abort if >1%, warn if >0.5%
3. **Start with `OKX_SIMULATED=1`** — validate everything before going live
4. **Never print or log credentials** — load via `source .env` only
5. **Set stop-loss on every position** — meme coins and leveraged positions can move fast
6. **Daily trade limit** — auto-trading will stop when `max_daily_trades` is reached

## Memory Files

| File | Purpose |
|------|---------|
| `memory/okx-trading-preferences.json` | Strategy config, risk parameters, and trading mode |
| `memory/okx-trading-state.json` | Runtime state (daily trade count, last scan) |
| `memory/okx-trading-journal.json` | Trade history from monitor (SL/TP closures, auto-entries) |
| `memory/okx-trade-journal.json` | Trade history from learning system (signal analysis) |
| `memory/okx-learning-model.json` | Learning model (win rates by coin/regime, optimal params) |
| `memory/okx-grid-{inst_id}.json` | Grid state per instrument |

## Kill Switch

```bash
# Stop all automated trading
bash scripts/cron_setup.sh teardown
# Or remove OKX_API_KEY from .env to prevent any API calls
```
