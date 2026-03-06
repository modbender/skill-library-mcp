---
name: polymarket-fast-loop-improved
displayName: Polymarket FastLoop Trader (Improved)
description: Trade Polymarket BTC/ETH/SOL 5-minute and 15-minute fast markets using multi-signal CEX momentum. Adds funding rate confirmation, order book imbalance, time-of-day filtering, volatility-adjusted sizing, win-rate calibration, and fee-accurate EV math. Use when user wants to trade sprint/fast markets with a more rigorous edge filter.
metadata: {"clawdbot":{"emoji":"⚡","requires":{"env":["SIMMER_API_KEY"],"pip":["simmer-sdk"]},"cron":null,"autostart":false,"automaton":{"managed":true,"entrypoint":"fastloop_improved.py"}}}
authors:
  - Based on Simmer (@simmer_markets) original, enhanced
version: "1.0.0"
published: false
---

# Polymarket FastLoop Trader — Improved

An enhanced version of the Simmer FastLoop skill with rigorous edge filtering, multi-signal confirmation, and real calibration tracking.

> **Default is paper mode.** Use `--live` for real trades. Always run 100+ paper trades first to validate your win rate before going live.

> ⚠️ Fast markets carry Polymarket's 10% fee. Your signal needs to be right **63%+ of the time** to profit. This skill will tell you your actual win rate.

## Key Improvements Over Original

| Feature | Original | Improved |
|---------|----------|----------|
| Fee math | Approximate | Exact breakeven with configurable buffer |
| Signal | Binance momentum only | Momentum + funding rate + order book |
| Momentum threshold | 0.5% (too low) | 1.0% default, calibration-driven |
| Time filtering | None | Skips low-liquidity hours |
| Position sizing | Fixed | Volatility-adjusted |
| Win rate tracking | None | Logs outcomes, reports calibration |
| Market selection | Soonest expiry | Configurable sweet-spot window |
| Stats | None | Full P&L, win rate, signal breakdown |

## Quick Start

```bash
# Install dependency
pip install simmer-sdk

# Set API key
export SIMMER_API_KEY="your-key-here"

# Paper mode — see what would happen (default)
python fastloop_improved.py

# Go live
python fastloop_improved.py --live

# Check calibration stats (win rate, P&L, signal accuracy)
python fastloop_improved.py --stats

# Resolve any expired paper trades against real outcomes
python fastloop_improved.py --resolve

# Quiet mode for cron
python fastloop_improved.py --live --quiet
```

## How to Run on a Loop

**OpenClaw native cron:**
```bash
openclaw cron add \
  --name "FastLoop Improved" \
  --cron "*/5 * * * *" \
  --tz "UTC" \
  --session isolated \
  --message "Run improved fast loop: cd /path/to/skill && python fastloop_improved.py --live --quiet. Show output summary." \
  --announce
```

**Linux crontab:**
```
*/5 * * * * cd /path/to/skill && python fastloop_improved.py --live --quiet
```

## Configuration

```bash
# Raise momentum threshold (recommended: 1.0–2.0%)
python fastloop_improved.py --set min_momentum_pct=1.5

# Require order book confirmation
python fastloop_improved.py --set require_orderbook=true

# Set sweet-spot window for market selection (seconds remaining)
python fastloop_improved.py --set target_time_min=90 --set target_time_max=180

# Disable time-of-day filter (trade 24/7)
python fastloop_improved.py --set time_filter=false
```

### All Settings

| Setting | Default | Description |
|---------|---------|-------------|
| `entry_threshold` | 0.05 | Min divergence from 50¢ |
| `min_momentum_pct` | 1.0 | Min % BTC move (raised from 0.5) |
| `max_position` | 5.0 | Max $ per trade |
| `signal_source` | binance | binance or coingecko |
| `lookback_minutes` | 5 | Candle lookback window |
| `min_time_remaining` | 60 | Skip if less than N seconds left |
| `target_time_min` | 90 | Prefer markets with ≥ N seconds left |
| `target_time_max` | 210 | Prefer markets with ≤ N seconds left |
| `asset` | BTC | BTC, ETH, or SOL |
| `window` | 5m | 5m or 15m |
| `volume_confidence` | true | Skip low-volume signals |
| `require_funding` | false | Require funding rate confirmation |
| `require_orderbook` | false | Require order book imbalance confirmation |
| `time_filter` | true | Skip low-liquidity hours (02:00–06:00 UTC) |
| `vol_sizing` | true | Adjust size by recent volatility |
| `fee_buffer` | 0.05 | Extra edge required above fee breakeven |
| `daily_budget` | 10.0 | Max spend per UTC day |
| `starting_balance` | 1000.0 | Paper portfolio starting balance |

## Signal Logic

Three signals are evaluated independently. The momentum signal is always required. Funding and order book are optional confirmation layers.

### 1. Momentum (always on)
- Fetch N one-minute Binance candles
- `momentum = (close_now - open_then) / open_then * 100`
- Must exceed `min_momentum_pct`

### 2. Funding Rate (optional, `require_funding=true`)
- Fetch Binance perpetual funding rate for the asset
- Positive funding + upward momentum = longs crowded, signal is weaker → SKIP
- Negative funding + upward momentum = confirmation → TRADE
- Logic inverted for downward momentum

### 3. Order Book Imbalance (optional, `require_orderbook=true`)
- Fetch top 20 levels of Binance L2 book
- `imbalance = (bid_depth - ask_depth) / (bid_depth + ask_depth)`
- Imbalance > 0.1 confirms upward momentum
- Imbalance < -0.1 confirms downward momentum

### Fee-Accurate EV
```
entry_price  = market price of chosen side
win_profit   = (1 - entry_price) × (1 - fee_rate)
breakeven    = entry_price / (win_profit + entry_price)
required_div = (breakeven - 0.50) + fee_buffer
```
Trade only fires if `actual_divergence ≥ required_div`.

### Time-of-Day Filter
Skips 02:00–06:00 UTC by default. US session (13:00–21:00 UTC) is the highest-liquidity window for crypto prediction markets.

### Volatility-Adjusted Sizing
```
24h_vol = std(hourly_returns_last_24h) × √24
size    = max_position × min(1.0, 0.02 / 24h_vol)
```
High volatility → smaller position. Low volatility with strong trend → full size.

## Win Rate Calibration

The skill tracks every paper and live trade in `fastloop_ledger.json`. After market expiry, run `--resolve` to fetch the actual Polymarket outcome and log it. After 50+ trades, `--stats` shows your real win rate broken down by momentum threshold, time of day, and asset — so you can tune settings based on actual data rather than guessing.

## Troubleshooting

All troubleshooting from the original skill applies. Additional:

**"Funding rate fetch failed"**
- Binance futures API may be rate-limited. Skill falls back to momentum-only.

**"Order book imbalance: neutral"**
- Market is balanced, signal is ambiguous — skipped if `require_orderbook=true`.

**"Time filter: low liquidity window"**
- Current UTC hour is in the 02–06 block. Set `time_filter=false` to override.
