# ETF Finance Skill

A comprehensive ETF and fund portfolio management tool for OpenClaw.

## Features

- **Position Management**: Add, remove, and track your ETF/fund holdings
- **Profit/Loss Calculation**: Real-time calculation of gains/losses with percentage
- **Price Alerts**: Set target prices for alerts when prices go up or down
- **Real-time Data**: Fetches live prices from Yahoo Finance (free, no API key required)

## Installation

```bash
cd ~/.openclaw/workspace/skills/etf-investor
bash scripts/install.sh
```

The install script will:
- Create the data directory at `~/.clawdbot/etf_investor/`
- Set up a Python virtual environment with yfinance
- Initialize empty positions and alerts files

## Quick Start

### 1. Add a position
```bash
python3 scripts/add_position.py SPY 680.00 10 "S&P 500 ETF"
```

### 2. View your portfolio
```bash
python3 scripts/portfolio_summary.py
```

### 3. Set a price alert
```bash
python3 scripts/add_alert.py SPY 700.00 price_up
```

## Commands

### Position Management

| Command | Description |
|---------|-------------|
| `add_position.py` | Add a new position |
| `remove_position.py` | Remove a position |
| `list_positions.py` | List all positions |
| `portfolio_summary.py` | Show portfolio with P/L |

### Price Alerts

| Command | Description |
|---------|-------------|
| `add_alert.py` | Add a price alert |
| `remove_alert.py` | Remove alerts for a symbol |
| `list_alerts.py` | List all alerts |
| `check_alerts.py` | Check if any alerts triggered |

### Price Queries

| Command | Description |
|---------|-------------|
| `get_price.py` | Get current price for a symbol |
| `update_prices.py` | Update prices for all positions |

## Supported Symbols

- **US ETFs**: SPY, QQQ, VOO, VTI, IVV, IWM, etc.
- **International ETFs**: EFA, VEA, VWO, VXUS, etc.
- **Sector ETFs**: XLF, XLK, XLV, XLE, XLB, etc.
- **Funds**: Any fund symbol supported by Yahoo Finance

## Data Storage

All data is stored locally in `~/.clawdbot/etf_investor/`:
- `positions.json` - Your holdings
- `alerts.json` - Price alerts

## Uninstall

```bash
bash scripts/uninstall.sh
```

This will remove all data files and configurations.

## License

MIT License
