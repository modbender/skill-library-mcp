---
name: congress-trades
description: Track US congress member and politician stock trades in real-time using the Quiver Quant API. Syncs trades to a local SQLite database, detects new significant trades above 15K, and sends alerts via OpenClaw messaging. Only requires Python with the requests library and a QUIVER_API_KEY environment variable. Use when setting up congressional trade monitoring, politician stock trade alerts, insider trading surveillance, or tracking what senators and representatives are buying and selling.
---

# Congress Trades Tracker

Monitor US congressional stock trades via Quiver Quant API, store in a local SQLite database, and alert on new significant trades. Requires Python `requests` library and a Quiver Quant API key.

## Requirements

- Python 3.10+ with `requests` (`pip install requests`)
- **QUIVER_API_KEY** environment variable (get a key at https://www.quiverquant.com/)

## Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| QUIVER_API_KEY | **Yes** | — | Quiver Quant API token |
| CONGRESS_DB_PATH | No | data/congress_trades.db | SQLite database path |
| MIN_TRADE_AMOUNT | No | 15001 | Minimum trade amount to trigger alerts |

Set these in your shell profile, `.env` file, or cron environment. Never hard-code API keys in the script.

## Setup

### 1. Install Python dependency

```bash
pip install requests
```

### 2. Set your API key

```bash
export QUIVER_API_KEY="your-api-key-here"
```

### 3. Schedule with user cron (no sudo needed)

Add your env vars to `~/.profile` or a `.env` file sourced by your shell, then add the cron entry:

```bash
crontab -e
# Add this line (uses env vars from your profile):
* * * * * . "$HOME/.profile" && /usr/bin/python3 /path/to/scripts/scraper.py >> /path/to/logs/scraper.log 2>&1
```

Never inline API keys directly in crontab entries.

### 4. Set up OpenClaw alert pickup

Add to your `HEARTBEAT.md`:

```markdown
## Check for congress trade alerts
- Read `congress_trades/data/pending_congress_alert.txt` — if it has content, send the alert to the user, then delete the file.
```

Or create an OpenClaw cron job (every 5 min) to check and forward alerts.

## How It Works

1. Scraper runs every minute, fetches latest 200 trades from `api.quiverquant.com`
2. Inserts into local SQLite with unique trade_key deduplication
3. First run initializes DB and reports newest trade
4. Subsequent runs detect new trades, filter to buys/sells above threshold
5. Writes formatted alert to `data/pending_congress_alert.txt` for OpenClaw pickup
6. Keeps last 50 alerts in `data/new_trades.json`

## Network and Data

- **Only outbound connection**: `api.quiverquant.com` (Quiver Quant API)
- **Storage**: local SQLite file + JSON alert files in `data/`
- **No external endpoints** besides the Quiver API
- Restrict file permissions on data directory (`chmod 700 data/`)

## Alert Format

```
🏛️ 3 new congress trade(s) detected:

🟢 PURCHASE: Nancy Pelosi (D) [Rep]
   $NVDA — $1,000,001 - $5,000,000
   Trade: 2026-02-10 | Reported: 2026-02-14

🔴 SALE: Dan Crenshaw (R) [Rep]
   $MSFT — $15,001 - $50,000
   Trade: 2026-02-09 | Reported: 2026-02-14
```

## Customization

- **MIN_TRADE_AMOUNT**: raise/lower via env var to change alert threshold
- **Fetch limit**: change `limit=200` in `fetch_trades()` for broader sweeps
- **Cron frequency**: reduce to every 5 or 15 minutes if you prefer less polling
