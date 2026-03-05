---
name: kalshi-agent
description: Kalshi prediction market agent - analyzes markets and executes trades via the Kalshi v2 API
metadata:
  clawdbot:
    emoji: "🎰"
    homepage: https://docs.kalshi.com/api-reference/
    os: ["darwin", "linux", "win32"]
    requires:
      bins: ["python3", "pip"]
      env: ["KALSHI_ACCESS_KEY"]
      files: ["~/.kalshi/private_key.pem"]
    py_package: "cryptography>=41.0.0"
---

# Kalshi Agent Skill

CLI tool for trading prediction markets on [Kalshi](https://kalshi.com).

## Installation

```bash
npm install -g kalshi-cli
```

## Configuration

1. Get API credentials at: https://kalshi.com/api
2. Place your RSA private key at `~/.kalshi/private_key.pem`
3. Set your access key in `~/.kalshi/.env`:

```
KALSHI_ACCESS_KEY=your_access_key_id
```

Or run `kalshi setup-shell` to add it to your shell config.

---

## Commands

### Browse & Research

```bash
# List open markets (default 20)
kalshi markets
kalshi markets -l 50
kalshi markets --status settled

# Search by keyword, ticker, or category
kalshi search "Super Bowl"
kalshi search soccer
kalshi search hockey
kalshi search KXWO-GOLD-26

# Search with filters
kalshi search politics --min-odds 5     # hide markets where either side < 5%
kalshi search soccer --expiring          # sort by soonest expiry, show expiry column
kalshi search soccer -e -m 2 -l 20      # combine flags: expiring, 2% min-odds, 20 results

# Browse all active series (interactive — pick a number to drill down)
kalshi series
kalshi series soccer
kalshi series --all                      # include series with no active markets
kalshi series -e                         # sort by soonest expiry

# View single market detail
kalshi detail KXWO-GOLD-26-NOR

# View orderbook depth
kalshi orderbook KXWO-GOLD-26-NOR
```

### Search Behavior

Search uses a multi-strategy approach:

1. **Direct ticker lookup** — tries the query as a market ticker, event ticker (`KX` prefix), or series ticker
2. **Series matching** — dynamically searches all Kalshi series by title, category, and tags (e.g. "soccer" matches series tagged "Soccer")
   - If many series match, shows an **interactive numbered list** — enter a number to drill into that series' markets
   - If few series match, fetches and displays markets directly
3. **Market title search** — falls back to searching open market titles/tickers

Common sport/category aliases are expanded automatically (e.g. "nfl" also searches "football").

### Interactive Series Lists

Both `kalshi search` and `kalshi series` display numbered tables when listing series. After the table, you're prompted:

```
Enter # to drill down (or q to quit):
```

Pick a number to load that series' open markets inline. The prompt loops so you can explore multiple series without re-running the command.

### Portfolio

```bash
# Check balance
kalshi balance

# View positions
kalshi positions

# View open orders
kalshi orders
```

### Trading

```bash
# Buy 10 YES contracts at 68c each
kalshi buy KXSB-26 10 68

# Buy NO contracts
kalshi buy KXWO-GOLD-26-NOR 5 32 --side no

# Sell (same syntax)
kalshi sell KXWO-GOLD-26-NOR 5 40 --side no

# Skip confirmation prompt
kalshi buy KXSB-26 10 68 --force

# Cancel an open order
kalshi cancel <order-id>
```

### Notes

- Prices are in **cents** (68 = $0.68 = 68% implied probability)
- Prices display as both dollars and percentages (e.g. `$0.68 (68%)`)
- `--side` defaults to `yes` if not specified
- `buy` and `sell` show a cost/proceeds summary and ask for confirmation (bypass with `--force`)
- `--min-odds` / `-m` filters out markets where either side's bid is below a percentage threshold (default 0.5%)
- `--expiring` / `-e` sorts results by soonest expiry, adds an "Expires" column, and excludes already-expired entries
- Expiry times are human-readable: "8h 35m", "Fri 04:00PM", "Apr 01", "Jan 01, 2027"
- Event tickers start with `KX` (e.g. `KXWO-GOLD-26`); market tickers have more segments (e.g. `KXWO-GOLD-26-NOR`)
- Market tables show outcome names (e.g. "Norway" instead of raw tickers) when available

---

## API Reference

Full API docs: https://docs.kalshi.com/api-reference/
