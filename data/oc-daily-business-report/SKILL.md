---
name: daily-business-report
description: Generate daily business briefings from multiple data sources. Aggregates weather, crypto prices, news headlines, system health, and calendar events into a formatted morning report. Use when asked to create a daily report, morning briefing, business summary, or status dashboard.
---

# Daily Business Report

Generate comprehensive daily briefings by aggregating data from free public APIs.

## Quick Start

```bash
# Generate full morning report
python scripts/report.py generate

# Generate specific sections only
python scripts/report.py generate --sections weather,crypto,news

# Output as JSON
python scripts/report.py generate -f json

# Output as markdown
python scripts/report.py generate -f md -o morning-report.md

# Configure your location and preferences
python scripts/report.py config --city "Brussels" --crypto "BTC,ETH,SOL" --news-country "us"

# Show current configuration
python scripts/report.py config --show

# Test individual data sources
python scripts/report.py test weather
python scripts/report.py test crypto
python scripts/report.py test news
```

## Commands

| Command | Args | Description |
|---------|------|-------------|
| `generate` | `[--sections LIST] [-f FORMAT] [-o FILE]` | Generate the full report |
| `config` | `[--city CITY] [--crypto COINS] [--news-country CC]` | Configure preferences |
| `config` | `--show` | Display current configuration |
| `test` | `<source>` | Test a single data source |

## Report Sections

| Section | Source | API Key Needed? |
|---------|--------|-----------------|
| **Weather** | wttr.in | No |
| **Crypto** | CoinGecko API | No |
| **News** | NewsData.io | Free tier (optional) |
| **Quote** | Quotable API | No |
| **System** | Local disk/memory | No |
| **Date** | Built-in | No |

## Example Output

```
╔══════════════════════════════════════════════════╗
║  DAILY BUSINESS REPORT — Mon 24 Feb 2026        ║
╠══════════════════════════════════════════════════╣
║                                                  ║
║  🌤 Weather: Brussels — 8°C, partly cloudy       ║
║  📈 BTC: $97,432 (+2.3%) ETH: $3,891 (-0.4%)   ║
║  📰 Top News:                                    ║
║     1. EU approves new AI regulation framework   ║
║     2. Tech stocks rally on earnings beat        ║
║  💬 "The best way to predict the future is to    ║
║     create it." — Peter Drucker                  ║
║  💾 Disk: 45% used | RAM: 62% used              ║
║                                                  ║
╚══════════════════════════════════════════════════╝
```

## Integration with OpenClaw

Perfect for cron jobs. Add to your `openclaw.json`:
```json
{
  "cron": {
    "entries": {
      "morning-report": {
        "schedule": "0 7 * * *",
        "agent": "main",
        "prompt": "Run daily-business-report generate and send the result."
      }
    }
  }
}
```
