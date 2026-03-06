# trading-upbit-skill (v13)

Upbit automated trading skill designed for OpenClaw cron operation.


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

## Install

```bash
cd /Users/sgyeo/.openclaw/workspace/skills/trading-upbit-skill
npm install
```

## Configure

## Credentials (ClawHub / OpenClaw)

This skill needs Upbit API credentials.

### Option A (recommended): OpenClaw skills-config env
Inject secrets via OpenClaw Skills Config so you don't store keys in files.

Edit `~/.openclaw/openclaw.json` (JSON5) and add:

```json5
{
  skills: {
    entries: {
      "trading-upbit-skill": {
        env: {
          UPBIT_ACCESS_KEY: "YOUR_UPBIT_ACCESS_KEY",
          UPBIT_SECRET_KEY: "YOUR_UPBIT_SECRET_KEY"
        }
      }
    }
  }
}
```

### Option B (local dev): config.json
You can also put keys in `config.json`:

```json
{
  "upbit": {
    "accessKey": "YOUR_UPBIT_ACCESS_KEY",
    "secretKey": "YOUR_UPBIT_SECRET_KEY"
  }
}
```

**Never commit or upload `config.json`.** It is included in `.gitignore` by default.


Create `config.json` in the skill root (DO NOT COMMIT). Start from `config.example.json`.

### Recommended config (budget % + split)

```json
{
  "upbit": {
    "accessKey": "YOUR_UPBIT_ACCESS_KEY",
    "secretKey": "YOUR_UPBIT_SECRET_KEY"
  },
  "trading": {
    "watchlist": ["KRW-BTC", "KRW-ETH", "KRW-SOL"],
    "monitorHoldings": true,
    "topVolume": {
      "enabled": true,
      "quote": "KRW",
      "topN": 10,
      "metric": "acc_trade_price_24h",
      "refreshMs": 900000
    },
    "excludeMarkets": ["KRW-USDT"],
    "budgetPolicy": {
      "mode": "balance_pct_split",
      "pct": 0.3,
      "reserveKRW": 0,
      "minOrderKRW": 5000,
      "roundToKRW": 1000
    },
    "aggressive": {
      "enabled": true,
      "entryNearThreshold": 0.99,
      "momentumCandles": 3,
      "momentumBullMin": 2,
      "takeProfitHard": 0.03,
      "trailingActivateAt": 0.01,
      "trailingStop": 0.01,
      "stopLoss": -0.02
    },
    "maxPositions": 5
  },
  "execution": {
    "dryRun": true
  },
  "logging": { "level": "info" }
}
```

## Run locally

```bash
node skill.js smoke_test
node skill.js monitor_once
node skill.js worker_once
```

## OpenClaw Cron (recommended)

Monitor (5m):
```bash
openclaw cron add   --name "Upbit Monitor 5m"   --cron "*/5 * * * *"   --tz "Asia/Seoul"   --session isolated   --command "cd /Users/sgyeo/.openclaw/workspace/skills/trading-upbit-skill && node skill.js monitor_once"   --delivery none
```

Worker (1m):
```bash
openclaw cron add   --name "Upbit Worker 1m"   --cron "* * * * *"   --tz "Asia/Seoul"   --session isolated   --command "cd /Users/sgyeo/.openclaw/workspace/skills/trading-upbit-skill && node skill.js worker_once"   --delivery none
```

## Testing synthetic BUY/SELL

See `README_TESTING.md`.

Quick test:
```bash
node scripts/tests/inject_buy_signal.js --market KRW-XRP --budget 10000 --price 2330 --target 2310 --ratio 1.008 --breakout true --near false --momentum true
node scripts/tests/run_worker_once.js
```

## Risk notice

This code can place real orders on Upbit. Use at your own risk.
Test with `execution.dryRun=true` first.
