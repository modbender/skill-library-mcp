---
name: dividend-premium-tracker
description: Track the dividend premium (dividend yield minus 10-year bond yield) for CSI Dividend Low Volatility Index. Monitor dividend yield, 10-year bond yield, and calculate the premium for investment decisions.
version: 1.0.1
---

# Dividend Premium Tracker

Track the dividend premium (dividend yield minus 10-year bond yield) for CSI Dividend Low Volatility Index.

## Description

This skill tracks the dividend premium for the CSI Dividend Low Volatility Index (H30269), which is crucial for investment decisions in China's dividend-focused market. The dividend premium represents the excess return of dividend-paying stocks over risk-free bonds.

## What It Tracks

- **CSI Dividend Low Volatility Index Dividend Yield** - From China Securities Index
- **10-Year China Government Bond Yield** - From Ministry of Finance
- **Dividend Premium** = Dividend Yield - Bond Yield

## Features

- 📊 Auto-download and track dividend and bond yield data
- 📈 Generate Excel reports with clean charts
- 🔔 Alert when bond yield rises for 3 consecutive days
- 🔔 Alert when premium drops below 1%
- 📅 Support for historical data backfill

## Commands

### Update Today's Data
```bash
python3 scripts/update_dividend_premium.py --update
```

### Check Monitoring Alerts
```bash
python3 scripts/monitor_dividend_premium.py --check
```

### Backfill Historical Data
```bash
python3 scripts/update_dividend_premium.py --backfill 2026-01-01 2026-01-31
```

## Files

```
dividend-premium-tracker/
├── SKILL.md              # This file
├── scripts/
│   ├── update_dividend_premium.py   # Main update script
│   └── monitor_dividend_premium.py  # Monitoring script
├── references/           # Documentation (optional)
└── assets/              # Output files (optional)
```

## Setup

### Telegram Alerts (Optional)

Set Telegram Bot Token for alerts:
```bash
export TELEGRAM_BOT_TOKEN="your_bot_token_here"
```

### Cron Job (Daily Update)

```bash
crontab -e
# Add line:
0 17 * * * cd /path/to/skill && python3 scripts/update_dividend_premium.py --update
```

## Data Sources

| Data | Source | URL |
|------|--------|-----|
| Dividend Yield | China Securities Index | [H30269 Indicator XLS](https://oss-ch.csindex.com.cn/static/html/csindex/public/uploads/file/autofile/indicator/H30269indicator.xls) |
| Bond Yield | Ministry of Finance | [ChinaBond](https://yield.chinabond.com.cn/cbweb-czb-web/czb/moreInfo?locale=cn_ZH&nameType=1) |

## Alert Thresholds

| Condition | Action |
|-----------|--------|
| Bond yield rises 3 consecutive days | Telegram alert |
| Premium < 1% | Telegram alert |

## Requirements

- Python 3.10+
- pandas
- openpyxl
- xlrd
- curl (for data download)

## Usage Notes

- Premium is calculated as: `Dividend Yield (%) - Bond Yield (%)`
- Premium < 1% suggests potential buying opportunity
- Premium < 0 indicates dividend stocks are cheaper than bonds
- Historical data from 2026-01-14 to present included

---

**Related Indices:**
- CSI Dividend Low Volatility Index (H30269/000966)
- 10-Year China Government Bond
