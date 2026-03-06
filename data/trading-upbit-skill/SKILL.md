---
name: trading-upbit-skill
description: Upbit automated trading (aggressive breakout) with cron-friendly run-once commands, TopVolume monitoring, and percent-based budget splitting.
user-invocable: true
metadata: {"version":"13.1.0","author":"Kuns9","type":"automated-trading","openclaw":{"requires":{"bins":["node"],"env":["UPBIT_ACCESS_KEY","UPBIT_SECRET_KEY"]},"primaryEnv":"UPBIT_ACCESS_KEY"}}
---

# trading-upbit-skill

Upbit automated trading skill for OpenClaw and local execution.


## What to consider before installing (Security)

This skill implements an automated Upbit trading bot and requires Upbit API keys. Before installing or handing over production keys:

1) **Inspect critical files**:
   - `scripts/execution/upbitClient.js` (Upbit HTTP client)
   - `scripts/config/index.js` (config + secrets loading)
   - `skill.js` (CLI entrypoint)

2) **Run in dry-run mode first**:
   - Set `execution.dryRun=true`
   - Run `node skill.js smoke_test`, `node skill.js monitor_once`, `node skill.js worker_once`

3) **Use the platform secret store**:
   - Provide keys via environment variables (OpenClaw Skills Config / secret store):
     - `UPBIT_OPEN_API_ACCESS_KEY`
     - `UPBIT_OPEN_API_SECRET_KEY`
   - Avoid storing secrets in `config.json`.

4) **Limit key permissions during testing**:
   - Use minimal funds / a test account where possible.
   - Monitor your Upbit account activity closely.

5) **Quick self-check**:
   - Run `node skill.js security_check` to scan the repository for hard-coded external URLs (allowlist: `api.upbit.com`).

Security notes:
- This skill **does not include telemetry** and **does not upload data** by design.
- The Upbit API base URL is **allowlisted** to `https://api.upbit.com/v1` and redirects are disabled.

## What it does

- Monitors markets (watchlist + optional TopVolume)
- Generates BUY/SELL events in `resources/events.json`
- Processes events in a worker (places orders or dry-run), and persists positions in `resources/positions.json`
- Designed for **cron**: `monitor_once` and `worker_once` are **run-once** commands

## Commands

### monitor_once
Run one monitoring cycle, enqueue events.

- `node skill.js monitor_once`

### worker_once
Process pending events (BUY/SELL), update positions.

- `node skill.js worker_once`

### smoke_test
Validate config and public endpoints (no trading).

- `node skill.js smoke_test`

## Budget Policy (v13)

Order sizing can be set to a **percentage of available KRW**, split equally across multiple buys in the same worker run.

```json
{
  "trading": {
    "budgetPolicy": {
      "mode": "balance_pct_split",
      "pct": 0.3,
      "reserveKRW": 0,
      "minOrderKRW": 5000,
      "roundToKRW": 1000
    }
  }
}
```

Behavior:
- totalBudget = floor((availableKRW - reserveKRW) * pct)
- if there are N BUY_SIGNALs pending, perOrderKRW = floor(totalBudget / N) rounded down to `roundToKRW`

## Cron (recommended)

Monitor (every 5 minutes):
- `cd <skillRoot> && node skill.js monitor_once`

Worker (every 1 minute):
- `cd <skillRoot> && node skill.js worker_once`

## Files

Required:
- `config.json` (do not commit)

Auto-created:
- `resources/events.json`
- `resources/positions.json`
- `resources/topVolumeCache.json`
- `resources/nearCounter.json`
- `resources/heartbeat.json`

Testing utilities:
- `scripts/tests/*` (see README_TESTING.md)
