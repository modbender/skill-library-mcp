---
name: crypto-regime-report
description: Generate market regime reports for crypto perpetuals using Supertrend and ADX indicators. Use when the user asks for a regime check, market report, trend analysis, or scheduled morning/evening crypto updates. Reports include price action, trend direction/strength, funding rates, open interest, volume analysis, and BTC correlation for a configurable watchlist.
metadata:
  openclaw:
    emoji: "📊"
    requires:
      bins: ["python3", "curl"]
---

# Crypto Regime Report

Generate regime reports for crypto perpetual futures using technical indicators.

## Quick Start

```bash
# Run a daily regime report
python3 {baseDir}/scripts/regime_report.py

# Run a weekly regime report
python3 {baseDir}/scripts/regime_report.py --weekly
```

Or ask directly: "What's the regime on BTC?" or "Run a market report."

**Note:** The script outputs a formatted report to stdout. The agent handles delivery (e.g., sending to Telegram, displaying in chat).

---

## What's Included in Reports

**Price & Trend:**
- Current price + 24h change
- Regime classification (Strong Bull/Bear, Weak Bull/Bear, Ranging)
- ADX value (trend strength)
- Trend direction (bullish/bearish based on Supertrend)
- Distance from Supertrend line (%)

**Volume & Liquidity:**
- Volume vs 20-day average (%)
- 🔇 = low volume, 🔊 = high volume

**Perpetuals Data:**
- Funding rate + change direction (↑↓→)
- Open Interest (current, in $B)
- 🔥 = elevated funding rate

**Market Context:**
- BTC correlation (0.0 to 1.0)
- 🔗 = high correlation (> 0.7)

---

## Setup Guide

### 1. Configure Your Watchlist

**Option A: Edit the default config**

Edit `{baseDir}/references/config.json` to customize your asset list:

```json
{
  "watchlist": [
    {"symbol": "BTC", "name": "Bitcoin", "okx": "BTC-USDT-SWAP"},
    {"symbol": "ETH", "name": "Ethereum", "okx": "ETH-USDT-SWAP"}
  ],
  "indicators": {
    "supertrend": { "period": 10, "multiplier": 3 },
    "adx": { "period": 14, "strong_threshold": 25, "weak_threshold": 20 }
  }
}
```

**Option B: Use a custom config file**

```bash
# Via environment variable (must be relative path within skill directory)
REGIME_CONFIG=references/my-config.json python3 {baseDir}/scripts/regime_report.py
```

**Security note:** For security, config paths are restricted to the skill directory. Absolute paths and path traversal (e.g., `../`) are not allowed.

An example config is provided at `{baseDir}/references/config.example.json` — copy and modify it for your needs.

**Config fields:**
- `symbol` — Short ticker (used for display)
- `name` — Full name (used for display)
- `okx` — OKX perpetual symbol (must match OKX's format: `ASSET-USDT-SWAP`)

**To find OKX symbols:** Visit [OKX Markets](https://www.okx.com/markets) or use:
```bash
curl -s "https://www.okx.com/api/v5/public/instruments?instType=SWAP"
# Optionally pipe through jq to filter: | jq '.data[].instId'
```

### 2. Configure Indicator Settings

Adjust in `config.json`:

| Setting | Default | Description |
|---------|---------|-------------|
| `supertrend.period` | 10 | Lookback period for ATR calculation |
| `supertrend.multiplier` | 3.0 | ATR multiplier for band width |
| `adx.period` | 14 | Lookback period for ADX |
| `adx.strong_threshold` | 25 | ADX level for "strong" trend |
| `adx.weak_threshold` | 20 | ADX level for "weak" trend |

### 3. Set Up Scheduled Reports (Optional)

Use OpenClaw's cron system to receive reports automatically.

**Via CLI:**

```bash
# Morning report (6am PST)
openclaw cron add \
  --name "Morning Regime Report" \
  --schedule "0 6 * * *" \
  --timezone "America/Los_Angeles" \
  --message "Run the crypto regime morning report"

# Evening report (3pm PST)
openclaw cron add \
  --name "Evening Regime Report" \
  --schedule "0 15 * * *" \
  --timezone "America/Los_Angeles" \
  --message "Run the crypto regime evening report"

# Friday weekly summary (4pm PST)
openclaw cron add \
  --name "Friday Weekly Summary" \
  --schedule "0 16 * * 5" \
  --timezone "America/Los_Angeles" \
  --message "Run the crypto regime weekly report with --weekly flag"
```

**Via config (`~/.openclaw/openclaw.json`):**

```json5
{
  // ... other config ...
  "cron": {
    "jobs": [
      {
        "name": "Morning Regime Report",
        "schedule": { "kind": "cron", "expr": "0 6 * * *", "tz": "America/Los_Angeles" },
        "sessionTarget": "isolated",
        "payload": { "kind": "agentTurn", "message": "Run the crypto regime morning report" },
        "delivery": { "mode": "announce" }
      },
      {
        "name": "Evening Regime Report",
        "schedule": { "kind": "cron", "expr": "0 15 * * *", "tz": "America/Los_Angeles" },
        "sessionTarget": "isolated",
        "payload": { "kind": "agentTurn", "message": "Run the crypto regime evening report" },
        "delivery": { "mode": "announce" }
      },
      {
        "name": "Friday Weekly Summary",
        "schedule": { "kind": "cron", "expr": "0 16 * * 5", "tz": "America/Los_Angeles" },
        "sessionTarget": "isolated",
        "payload": { "kind": "agentTurn", "message": "Run the crypto regime weekly report with --weekly flag" },
        "delivery": { "mode": "announce" }
      }
    ]
  }
}
```

### 4. Test the Reports

```bash
# Test daily report
python3 {baseDir}/scripts/regime_report.py

# Test weekly report
python3 {baseDir}/scripts/regime_report.py --weekly
```

---

## What It Does

1. Fetches OHLCV data from OKX for each asset on the watchlist
2. Calculates Supertrend to determine trend direction
3. Calculates ADX to measure trend strength
4. Fetches current funding rates and open interest
5. Outputs a formatted report suitable for Telegram delivery

---

## Indicators

### Supertrend (10, 3)
- **Period:** 10
- **Multiplier:** 3
- **Bullish:** Price above Supertrend line
- **Bearish:** Price below Supertrend line

### ADX (Average Directional Index)
- **> 25:** Strong trend (bull or bear)
- **20-25:** Weak/moderate trend
- **< 20:** No clear trend / ranging

## Regime Classification

| Supertrend | ADX | Regime |
|------------|-----|--------|
| Bullish | > 25 | Strong Bull |
| Bullish | 20-25 | Weak Bull |
| Bearish | > 25 | Strong Bear |
| Bearish | 20-25 | Weak Bear |
| Either | < 20 | Ranging |

---

## Data Sources

| Data | Source | Notes |
|------|--------|-------|
| Daily OHLCV | OKX API | Free, no key required |
| Weekly OHLCV | Yahoo Finance | 11+ years history, OKX fallback |
| Funding Rates | OKX API | Free, no key required |
| Open Interest | OKX API | Free, no key required |

**OKX API endpoints:**
- OHLCV: `/api/v5/market/candles`
- Funding: `/api/v5/public/funding-rate`
- Open Interest: `/api/v5/public/open-interest`

---

## Resources

### scripts/
- `regime_report.py` — Main script that fetches data and generates the report

### references/
- `config.json` — Default watchlist configuration (edit this to customize)
- `config.example.json` — Example config you can copy and modify
