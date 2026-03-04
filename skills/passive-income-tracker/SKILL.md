# Passive Income Tracker — Bandwidth & Crypto Earnings Dashboard

Track all your passive income crypto apps from one place. Unified dashboard showing daily earnings, payout history, and USD/EUR totals across Grass.io, Storj, Mysterium, Honeygain, EarnApp, and more.

## What It Does

- **Unified earnings dashboard** — all apps in one view
- **Daily/weekly summaries** — automatically messaged to WhatsApp/Telegram
- **Payout tracking** — logs confirmed payouts and estimates pending rewards
- **USD/EUR conversion** — fetches live crypto prices for fiat estimates
- **Uptime correlation** — cross-checks earnings with service uptime
- **Alert on low earnings** — warns if an app stops earning (node down?)
- **CSV/JSON export** — for spreadsheet or tax reporting

## Supported Apps

| App | Method | Data |
|-----|--------|------|
| **Grass.io** | API (session token) | Points, bandwidth used, tier |
| **Storj** | Satellite API | Storage used, earnings, payouts |
| **Mysterium** | Local node API (3478) | Sessions, GiB shared, MYST earned |
| **Honeygain** | API (email+pass) | Credits, referrals, balance |
| **EarnApp** | API (token) | Bandwidth sold, balance, traffic |
| **Peer2Profit** | API (token) | P2P traffic earnings |
| **Custom** | HTTP endpoint | JSON polling |

## Quick Start

```bash
# Initialize tracker
passive-income-tracker init

# Add Grass.io (requires session token from browser)
passive-income-tracker add-app grass \
  --token "your-grass-session-token"

# Add Storj node
passive-income-tracker add-app storj \
  --satellite "us1.storj.io:7777" \
  --api-key "your-api-key"

# Add Mysterium node (local)
passive-income-tracker add-app mysterium \
  --node-url "http://localhost:3478"

# Check current earnings
passive-income-tracker status

# Get weekly summary
passive-income-tracker summary --period week

# Setup daily WhatsApp report at 8am
passive-income-tracker alert-setup \
  --channel whatsapp \
  --schedule "every day at 8am"
```

## Commands

| Command | Description |
|---------|-------------|
| `passive-income-tracker init` | Set up config and data directory |
| `passive-income-tracker add-app <name>` | Add a new passive income app |
| `passive-income-tracker list` | Show all configured apps |
| `passive-income-tracker status` | Current earnings for all apps |
| `passive-income-tracker summary` | Daily/weekly/monthly summary |
| `passive-income-tracker history [app]` | Earnings history chart |
| `passive-income-tracker alert-setup` | Configure alerts and reports |
| `passive-income-tracker export` | Export to CSV/JSON |

## Example Output

```
╔══════════════════════════════════════════════╗
║   PASSIVE INCOME TRACKER — 2026-02-25        ║
╠══════════════════════════════════════════════╣
║ App          │ Today    │ This Week │ Status  ║
╠══════════════════════════════════════════════╣
║ Grass.io     │ 412 pts  │ 2,891 pts │ 🟢 LIVE ║
║ Storj        │ $0.84    │ $5.88     │ 🟢 LIVE ║
║ Mysterium    │ 0.31 MYST│ 2.17 MYST │ 🟢 LIVE ║
║ Honeygain    │ $0.22    │ $1.54     │ 🟢 LIVE ║
╠══════════════════════════════════════════════╣
║ TOTAL (est.) │ ~$1.87   │ ~$13.09   │         ║
║ Monthly est. │          │           │ ~$56/mo ║
╚══════════════════════════════════════════════╝

💡 Grass.io earnings down 18% vs yesterday. Check node uptime.
```

## Daily WhatsApp Summary

When alerts are configured, you get a morning message:

```
📊 Passive Income — Daily Report (Feb 25)

Grass.io: 412 pts (+3.2%)
Storj: $0.84 (+1.1%)
Mysterium: 0.31 MYST (~$0.47)
Honeygain: $0.22

Total: ~$1.87 today
Weekly: ~$13.09
Monthly projection: ~$56

⚡ Action: Storj payout threshold ($10) reached in 3 days
```

## Grass.io Setup

Getting your session token:
1. Login at app.getgrass.io in Chrome
2. Open DevTools → Application → Local Storage → app.getgrass.io
3. Copy `userId` and `accessToken` values
4. Paste into `passive-income-tracker add-app grass --token <accessToken>`

> Note: Grass.io doesn't have an official public API. This skill uses the same endpoints as the web dashboard. Token may expire; re-auth if earnings show as 0.

## Storj Setup

```bash
# Get API key from Storj dashboard → Access → Create API Key
passive-income-tracker add-app storj \
  --satellite "eu1.storj.io:7777" \
  --api-key "your-16-char-key" \
  --wallet "0xYourEthereumAddress"
```

## Mysterium Setup

```bash
# Mysterium node must be running locally (Docker or native)
# Default API port is 4449 (not 3478 — check your config)
passive-income-tracker add-app mysterium \
  --node-url "http://localhost:4449" \
  --token "$(cat ~/.mysterium/keystore/node.key)"
```

## Price Data

Live prices fetched from CoinGecko (free, no API key). Supported:
- MYST → EUR/USD
- STORJ → EUR/USD  
- GRASS token → EUR/USD (when listed)
- Custom token → by CoinGecko ID

## Data & Privacy

All data stored locally at `~/.openclaw/workspace/passive-income-tracker/`. SQLite database. No telemetry, no cloud sync. API tokens stored encrypted at rest.

## Tax Export

```bash
# Export 2025 earnings for tax reporting
passive-income-tracker export \
  --from 2025-01-01 \
  --to 2025-12-31 \
  --format csv \
  --output ~/passive-income-2025.csv
```

Output includes: date, app, amount, currency, USD_value, EUR_value (at time of earning).

## Requirements

- Python 3.8+
- OpenClaw 1.0+
- Running passive income apps (Grass, Storj, Mysterium, etc.)
- Optional: CoinGecko API (free tier works)

## Source & Issues

- **Source:** https://github.com/mariusfit/passive-income-tracker
- **Issues:** https://github.com/mariusfit/passive-income-tracker/issues
- **Author:** [@mariusfit](https://github.com/mariusfit)
