---
name: passive-income-monitor
description: Monitors multiple passive income streams from a single command.
  Tracks bandwidth monetization nodes (Grass.io, Mysterium Network),
  decentralized storage earnings (Storj), DeFi yield positions, and ...
---

# passive-income-monitor

**Version:** 1.0.0  
**Author:** mariusfit  
**Category:** finance, crypto, automation, passive-income  
**Tags:** passive income, crypto, grass, storj, mysterium, defi, staking, yield, monitoring, alerts

## What This Does

Monitors multiple passive income streams from a single command. Tracks bandwidth monetization nodes (Grass.io, Mysterium Network), decentralized storage earnings (Storj), DeFi yield positions, and crypto staking rewards. Provides unified dashboard, earnings summaries, and configurable alerts when earnings drop or nodes go offline.

**Zero API keys required for basic mode.** Optional API keys unlock richer data.

## Use Cases

- Track all passive income sources in one place
- Get alerted when a node goes offline or earnings drop
- Calculate daily/weekly/monthly earnings projections
- Compare actual vs expected yields across DeFi protocols
- Log earnings history for tax/accounting purposes

## Commands

### `monitor check` — Quick status of all configured streams
```bash
bash passive-income-monitor.sh check
```
Output: Status table (stream name, status, last earned, 24h total)

### `monitor earnings` — Detailed earnings report
```bash
bash passive-income-monitor.sh earnings [--days 7] [--format json|table|csv]
```

### `monitor add <type> <name> <config>` — Add income stream
```bash
bash passive-income-monitor.sh add grass "node1" --wallet 0xABC...
bash passive-income-monitor.sh add storj "storage1" --api-key KEY --node-id NODE_ID
bash passive-income-monitor.sh add mysterium "node1" --rpc http://localhost:4449
bash passive-income-monitor.sh add defi "aave-usdc" --protocol aave --address 0xABC... --chain ethereum
bash passive-income-monitor.sh add staking "eth-validator" --address 0xABC... --chain ethereum
```

### `monitor remove <name>` — Remove income stream
```bash
bash passive-income-monitor.sh remove "node1"
```

### `monitor alert <threshold>` — Set alert thresholds
```bash
bash passive-income-monitor.sh alert --min-daily 5.00 --notify-offline --email user@example.com
```

### `monitor export` — Export earnings history
```bash
bash passive-income-monitor.sh export --format csv --output earnings-2026.csv
```

### `monitor dashboard` — Live terminal dashboard (ncurses-style)
```bash
bash passive-income-monitor.sh dashboard
```

## Supported Platforms

| Platform | Type | API | Notes |
|----------|------|-----|-------|
| Grass.io | Bandwidth | Public API | Wallet address required |
| Mysterium Network | Bandwidth | Local RPC | Node must be running |
| Storj | Storage | API Key | DCS node API |
| Aave v3 | DeFi Lending | Public on-chain | No key needed |
| Compound v3 | DeFi Lending | Public on-chain | No key needed |
| Lido | ETH Staking | Public API | Staking address |
| Ethereum Staking | Validator | Beaconcha.in API | Validator pubkey |
| Helium | IoT Network | Public API | Wallet address |

## Configuration

Config stored in `~/.config/passive-income-monitor/config.json`:
```json
{
  "streams": [
    {
      "name": "grass-node1",
      "type": "grass",
      "wallet": "0xABC...",
      "enabled": true
    },
    {
      "name": "mysterium-node",
      "type": "mysterium",
      "rpc": "http://localhost:4449",
      "enabled": true
    }
  ],
  "alerts": {
    "min_daily_usd": 5.00,
    "notify_offline": true,
    "notify_method": "file"
  },
  "currency": "USD"
}
```

## Alert Methods

- `file` — Write alerts to `~/.config/passive-income-monitor/alerts.log`
- `stdout` — Print to terminal
- `webhook` — POST to configured URL (Discord, Slack, custom)
- OpenClaw integration: alerts appear as agent notifications

## Output Examples

```
╔═══════════════════════════════════════════════════════════════╗
║          PASSIVE INCOME MONITOR — 2026-02-24                  ║
╠═══════════════════════════╦═══════════╦══════════╦═══════════╣
║ Stream                    ║ Status    ║ 24h      ║ 7d Total  ║
╠═══════════════════════════╬═══════════╬══════════╬═══════════╣
║ grass-node1               ║ ✅ Online  ║ $0.34    ║ $2.18     ║
║ mysterium-residential     ║ ✅ Online  ║ $0.12    ║ $0.84     ║
║ storj-node                ║ ⚠️ Offline ║ $0.00    ║ $1.92     ║
║ aave-usdc-pos             ║ ✅ Earning ║ $0.28    ║ $1.96     ║
║ lido-staking              ║ ✅ Active  ║ $0.45    ║ $3.15     ║
╠═══════════════════════════╬═══════════╬══════════╬═══════════╣
║ TOTAL                     ║           ║ $1.19    ║ $10.05    ║
╚═══════════════════════════╩═══════════╩══════════╩═══════════╝

⚠️  ALERT: storj-node has been offline >2h. Check node health.
📈 Projected monthly: $35.70 (based on 7d average)
```

## Requirements

- bash 4.0+
- curl (for API calls)
- jq (for JSON parsing)
- bc (for math)
- Optional: node.js (for on-chain data via ethers.js)

## Installation

```bash
# Via OpenClaw
clawhub install passive-income-monitor

# Manual
bash install.sh
```

## Notes

- All data cached locally; no external tracking or telemetry
- Earnings data stored in CSV for privacy and portability
- OpenClaw agent can call this tool proactively during heartbeats
- Works offline for cached data; requires internet for fresh API calls
