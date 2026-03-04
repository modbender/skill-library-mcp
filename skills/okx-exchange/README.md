**English** | [中文](./README_ZH.md)

---

# OKX Exchange Skill

A quantitative trading agent for OKX exchange — full automation across spot, perpetual swap, and futures via the official V5 API.

---

## Capabilities

| Category | Features |
|---|---|
| Market Data | Price, K-lines, ticker, technical indicators (MA / RSI / MACD) |
| Account | Balance, positions, pending orders, order history |
| Orders | Market/limit, hedged positions, TP/SL, batch orders, OCO algo orders |
| Strategies | Trend following, grid trading, spot-futures arbitrage |
| Risk Control | Liquidation alerts, daily trade limits, price impact checks, auto SL/TP |
| Monitoring | Account snapshots with history, cron automation, auto position close |
| Reports | Daily/weekly/all-time P&L, win rate, best/worst trade, per-coin breakdown |
| Learning | Auto-classify trades, identify success/failure patterns, optimize parameters |
| Mode Switch | Paper trading / live trading, isolated API keys per mode |

---

## Quick Start

### 1. Configure credentials

```bash
cat >> ~/.openclaw/workspace/.env << 'EOF'
# Demo / paper trading (safe default)
OKX_API_KEY=your_demo_key
OKX_SECRET_KEY=your_demo_secret
OKX_PASSPHRASE=your_demo_passphrase
OKX_SIMULATED=1

# Live trading (optional — only active when mode=live)
OKX_API_KEY_LIVE=your_live_key
OKX_SECRET_KEY_LIVE=your_live_secret
OKX_PASSPHRASE_LIVE=your_live_passphrase
EOF
```

> **`OKX_SIMULATED=1` enables paper trading (safe).** Validate everything here before switching to live.

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Initialize

```bash
cd ~/.openclaw/workspace/skills/okx-exchange/scripts
python3 setup.py
```

---

## Usage

All commands go through the unified entry point `okx.py`.

```bash
cd ~/.openclaw/workspace/skills/okx-exchange/scripts
source ~/.openclaw/workspace/.env
```

### Account

```bash
python3 okx.py account                    # Full portfolio summary
python3 okx.py account balance USDT       # Specific currency balance
python3 okx.py account positions          # Open positions
python3 okx.py account orders             # Pending orders
python3 okx.py account history SWAP       # Order history (perpetual swap)
```

### Order Execution

```bash
# Spot market buy
python3 okx.py buy BTC-USDT market 0.01

# Perpetual long with TP/SL attached
python3 okx.py buy BTC-USDT-SWAP market 1 --td cross --pos long --tp 55000 --sl 42000

# Close long position (reduce-only)
python3 okx.py sell BTC-USDT-SWAP market 1 --td cross --pos long --reduce

# Standalone OCO algo order (add/replace TP+SL on an existing position)
python3 okx.py algo oco BTC-USDT-SWAP 1 --tp 55000 --sl 45000 --td cross --pos long --reduce

# Cancel all orders for a symbol
python3 okx.py cancel-all BTC-USDT-SWAP
```

### Strategies

```bash
# Trend analysis (no trade)
python3 okx.py trend analyze BTC-USDT-SWAP --bar 1H

# Trend execution
python3 okx.py trend run BTC-USDT-SWAP 1 --bar 4H --tp 0.05 --sl 0.03 --td cross --pos long

# Grid trading — setup / rebalance / stop
python3 okx.py grid setup BTC-USDT 40000 50000 10 1000
python3 okx.py grid check BTC-USDT
python3 okx.py grid stop BTC-USDT

# Spot-futures arbitrage
python3 okx.py arb scan
python3 okx.py arb basis BTC-USDT BTC-USDT-SWAP
python3 okx.py arb open BTC-USDT BTC-USDT-SWAP 1000 --min-basis 0.1
```

### Snapshot & Monitoring

```bash
# Full account snapshot with historical tracking table
python3 okx.py snapshot

# Manual monitor commands
python3 okx.py monitor sl-tp        # SL/TP check — auto-close positions if triggered
python3 okx.py monitor scan         # Strategy scan across watchlist
python3 okx.py monitor liq-risk     # Liquidation risk alert (default: within 10%)

# Cron automation
bash scripts/cron_setup.sh setup            # Default: SL/TP every 5m, scan every 30m
bash scripts/cron_setup.sh setup 1m         # SL/TP every 1 minute
bash scripts/cron_setup.sh setup 10m 1h     # SL/TP every 10m, scan every 1h
bash scripts/cron_setup.sh teardown         # Stop all cron jobs
bash scripts/cron_setup.sh status           # Show running jobs
```

### Performance Report

```bash
python3 okx.py report daily     # Today's P&L
python3 okx.py report weekly    # Last 7 days
python3 okx.py report all       # All time
```

### Trading Mode

```bash
python3 okx.py mode             # Show current mode
python3 okx.py mode demo        # Switch to paper trading
python3 okx.py mode live        # Switch to live (requires confirmation)
```

### Preferences

```bash
python3 okx.py prefs show
python3 okx.py prefs set stop_loss_pct 3.0
python3 okx.py prefs set take_profit_pct 8.0
python3 okx.py prefs set auto_trade true
python3 okx.py prefs set watchlist BTC-USDT-SWAP,ETH-USDT-SWAP,SOL-USDT-SWAP
```

---

## File Structure

```
okx-exchange/
├── SKILL.md                        # Agent instructions & triggers
├── README.md                       # This file (English)
├── README_ZH.md                    # Chinese version
├── requirements.txt                # Python dependencies (requests)
├── .env.example                    # Credentials template
│
├── docs/
│   ├── trading-rules.md            # Trading principles & decision guidelines
│   ├── decision-engine-guide.md    # Decision engine usage
│   └── learning-system-data-management.md
│
└── scripts/
    ├── okx.py                      # Unified CLI entry point
    ├── okx_client.py               # OKX REST API wrapper
    ├── okx_ws_client.py            # WebSocket real-time feed
    ├── okx_decision.py             # Decision engine
    ├── okx_learning.py             # Learning system (pattern recognition)
    ├── monitor.py                  # Automated monitor (SL/TP, scan, liq-risk)
    ├── account.py                  # Account & position display
    ├── execute.py                  # Order execution & safety checks
    ├── report.py                   # Performance report generation
    ├── config.py                   # Config & state persistence
    ├── errors.py                   # Error type definitions
    ├── logger.py                   # Structured logging
    ├── setup.py                    # First-run initialization
    ├── cron_setup.sh               # Cron job management
    │
    ├── strategies/
    │   ├── trend.py                # Trend following (MA + RSI + MACD)
    │   ├── grid.py                 # Grid trading
    │   └── arbitrage.py            # Spot-futures arbitrage
    │
    └── tests/                      # Unit tests (371 total, 0 failures)
        ├── run_all.py
        ├── test_account.py
        ├── test_algo_batch.py
        ├── test_arbitrage.py
        ├── test_config.py
        ├── test_decision.py
        ├── test_errors.py
        ├── test_execute.py
        ├── test_grid.py
        ├── test_learning.py
        ├── test_mode.py
        ├── test_okx_client.py
        ├── test_position_risk.py
        ├── test_private_ws.py
        ├── test_report.py
        ├── test_snapshot.py
        ├── test_trend.py
        └── test_ws_client.py
```

### Memory Files (runtime data)

| File | Purpose |
|---|---|
| `memory/okx-trading-preferences.json` | Risk parameters, strategy config, trading mode |
| `memory/okx-trading-state.json` | Runtime state (daily trade count, last scan time) |
| `memory/okx-trading-journal.json` | Monitor trade log (auto SL/TP closures) |
| `memory/okx-trade-journal.json` | Learning system trade log (signal analysis) |
| `memory/okx-learning-model.json` | Learning model (win rates by coin/regime, optimal params) |
| `memory/okx-monitor-snapshots.json` | Account snapshot history (up to 48 entries) |
| `memory/okx-grid-{inst_id}.json` | Grid state per instrument |

---

## Security

- API keys are stored in `~/.openclaw/workspace/.env` — never published to ClawHub
- Live and demo keys are fully isolated; switching mode never mixes credentials
- Order confirmation is on by default (`require_confirm=true`); set `auto_trade=true` for automation
- Daily trade limit (`max_daily_trades`) prevents runaway auto-trading

---

## Run Tests

```bash
cd scripts
python3 tests/run_all.py
# 371 tests, 0 failures
```

---

## Requirements

- Python 3.9+
- `requests >= 2.31.0`
- OKX account + V5 API Key ([apply here](https://www.okx.com/account/my-api))

---

**English** | [中文](./README_ZH.md)
