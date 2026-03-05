---
name: living-room-air-monitor
description: Monitor and report on living room air quality data. Collects temperature, humidity, PM2.5, and CO2 readings every hour from the Dirigera-connected air sensor, stores in SQLite database, and provides querying, averaging, charting, and reporting functions. Use when the user wants to (1) set up automated air quality data collection, (2) query historical air quality data, (3) generate charts for specific time periods, (4) get averages for days or months, or (5) send air quality reports via email or WhatsApp.
---

# Living Room Air Quality Monitor

This skill manages automated collection and reporting of air quality data from the living room ALPSTUGA air sensor connected to the IKEA Dirigera hub.

## What It Does

- **Collects data every hour** via cron for detailed tracking
- **Stores in SQLite database** with schema: datetime, temperature, humidity, pm25, co2
- **Skips incomplete readings** — only saves when all sensor values are present
- **Provides query functions** for retrieving data by datetime, day, month, or interval
- **Calculates averages** for any metric (temperature, humidity, PM2.5, CO2) by day or month
- **Generates line charts** for day, week, month, 3 months, 6 months, or year views
- **Sends reports** via email or WhatsApp (requires CONTACTS.json configuration)

**Note:** For smoke/fire detection with alerts, use the separate `living-room-smoke-detector` skill.

## Setup

### 1. Database Initialization

The database is auto-initialized on first data collection. Manual init:

```bash
python3 ~/.openclaw/workspace/skills/living-room-air-monitor/scripts/collect_air_data.py
```

**Data folder location:** `~/.openclaw/workspace/skills/living-room-air-monitor/data/`

**Files in data folder:**
- `air_quality.db` — SQLite database with all readings

### 2. Cron Setup

Add to crontab for automatic data collection every hour:

```bash
0 * * * * /opt/homebrew/bin/python3 /Users/macmini/.openclaw/workspace/skills/living-room-air-monitor/scripts/collect_air_data.py >> /tmp/air_quality_cron.log 2>&1
```

## Scripts Reference

### collect_air_data.py

Collects a single reading from the air sensor and saves to database.

```bash
# Collect data now
python3 scripts/collect_air_data.py
```

**Behavior:**
- Fetches data from Dirigera hub (192.168.1.100)
- Requires token in `~/.openclaw/workspace/.dirigera_token`
- Skips save if any sensor value is None
- Prints collected values to stdout

### query_data.py

Query the database for readings and averages.

```bash
# Get readings for a specific day
python3 scripts/query_data.py --day 2026-02-24

# Get readings for a month
python3 scripts/query_data.py --month 2026-02

# Get averages for a day (all metrics)
python3 scripts/query_data.py --avg-day 2026-02-24

# Get average for specific metric on a day
python3 scripts/query_data.py --avg-day 2026-02-24 --metric temperature

# Get averages for a month
python3 scripts/query_data.py --avg-month 2026-02

# Show available date range
python3 scripts/query_data.py --range
```

**Python API:**
```python
from scripts.query_data import (
    get_reading_by_datetime,      # Single reading closest to datetime
    get_readings_by_interval,      # All readings in range
    get_readings_by_day,           # All readings for a day
    get_readings_by_month,         # All readings for a month
    get_average_by_day,            # Average for one metric on one day
    get_average_by_month,          # Average for one metric in one month
    get_all_averages_by_day,       # All averages for a day
    get_all_averages_by_month,     # All averages for a month
    get_date_range                 # (earliest, latest) datetime strings
)
```

### generate_chart.py

Generate line charts for various time periods.

```bash
# Chart for today
python3 scripts/generate_chart.py

# Chart for specific day
python3 scripts/generate_chart.py --day 2026-02-24

# Chart for week ending on date
python3 scripts/generate_chart.py --week 2026-02-24

# Chart for month
python3 scripts/generate_chart.py --month 2026-02

# Chart for 3 months ending on date
python3 scripts/generate_chart.py --3month 2026-02-24

# Chart for 6 months ending on date
python3 scripts/generate_chart.py --6month 2026-02-24

# Chart for year
python3 scripts/generate_chart.py --year 2026

# Custom output directory
python3 scripts/generate_chart.py --day 2026-02-24 --output ~/charts
```

**Output:** PNG files saved to `/tmp/air_charts/` by default.

**Python API:**
```python
from scripts.generate_chart import (
    generate_day_chart,      # (date, output_dir) -> chart_path
    generate_week_chart,     # (end_date, output_dir) -> chart_path
    generate_month_chart,    # (year, month, output_dir) -> chart_path
    generate_3month_chart,   # (end_date, output_dir) -> chart_path
    generate_6month_chart,   # (end_date, output_dir) -> chart_path
    generate_year_chart,     # (year, output_dir) -> chart_path
    generate_chart           # (start_dt, end_dt, output_path, title) -> chart_path
)
```

### send_report.py

Send comprehensive air quality reports via email or WhatsApp.

```bash
# Send today's report via email (default)
python3 scripts/send_report.py

# Send specific day via email
python3 scripts/send_report.py --day 2026-02-24

# Send weekly report via email
python3 scripts/send_report.py --week 2026-02-24

# Send monthly report via email
python3 scripts/send_report.py --month 2026-02

# Send via WhatsApp instead of email
python3 scripts/send_report.py --day 2026-02-24 --channel whatsapp

# Send text-only report (no chart)
python3 scripts/send_report.py --day 2026-02-24 --no-chart
```

**Python API:**
```python
from scripts.send_report import (
    send_report,          # (start_dt, end_dt, channel, include_chart, chart_path)
    send_daily_report,    # (date, channel='email')
    send_weekly_report,   # (end_date, channel='email')
    send_monthly_report,  # (year, month, channel='email')
    generate_text_report  # (start_dt, end_dt) -> report_text
)
```

## Report Contents

Reports include:
- Period covered and total readings count
- Average values for all metrics with ranges
- Air quality assessment (Good/Moderate/Poor) for PM2.5 and CO2
- All individual readings with timestamps

**PM2.5 thresholds:**
- ≤12 µg/m³: Good
- 12.1-35 µg/m³: Moderate
- >35 µg/m³: Unhealthy

**CO2 thresholds:**
- ≤1000 ppm: Good
- 1001-2000 ppm: Moderate
- >2000 ppm: Poor

## Typical Usage Patterns

### User asks: "Send me yesterday's air quality report"

```bash
python3 scripts/send_report.py --day $(date -v-1d +%Y-%m-%d) --channel email
```

### User asks: "What's the average temperature this month?"

```bash
python3 scripts/query_data.py --avg-month $(date +%Y-%m) --metric temperature
```

### User asks: "Show me a chart of the last week"

```bash
python3 scripts/generate_chart.py --week $(date +%Y-%m-%d)
```

### User asks: "Email me the monthly air quality report"

```bash
python3 scripts/send_report.py --month $(date +%Y-%m) --channel email
```

### User asks: "WhatsApp me today's air data"

```bash
python3 scripts/send_report.py --day $(date +%Y-%m-%d) --channel whatsapp
```

## Dependencies

- Python 3.x
- SQLite3 (built-in)
- matplotlib (auto-installed if missing)
- Dirigera hub access (IP: 192.168.1.100)
- Valid auth token in `~/.openclaw/workspace/.dirigera_token`
- `gog` CLI for email (already configured)
- `wacli` CLI for WhatsApp (already configured)
- `CONTACTS.json` in workspace root (for email/WhatsApp reports)

## Configuration

### CONTACTS.json

Create `~/.openclaw/workspace/CONTACTS.json` with your contact information:

```json
{
  "name": "Your Name",
  "email": "your@email.com",
  "whatsapp": "+614xxxxxxxxx"
}
```

**Note:** WhatsApp number must be in international format (e.g., `+61400000000`)

This file is shared across all skills and prevents hardcoding personal information.

## Database Schema

```sql
CREATE TABLE air_quality (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    datetime TEXT NOT NULL UNIQUE,
    temperature REAL,
    humidity REAL,
    pm25 REAL,
    co2 REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_datetime ON air_quality(datetime);
```

## Related Skills

- **[living-room-smoke-detector](https://clawhub.com/skills/living-room-smoke-detector)** — Dedicated smoke/fire detection with continuous Mac speaker alerts. Use this for emergency alerting while air-monitor handles data collection and reporting.
