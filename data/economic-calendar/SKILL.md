---
name: economic-calendar
description: Fetch macro-economic events (Fed, ECB, CPI, etc.) from
  Investing.com. No API key required — pure scraping.
---

# economic-calendar

Fetch macro-economic events (Fed, ECB, CPI, etc.) from Investing.com. No API key required — pure scraping.

## Usage

```bash
# Today's high-importance US events (table output)
python scripts/economic_calendar.py

# Specific date with custom filters
python scripts/economic_calendar.py --date 2026-03-01 --importance high medium --countries "united states" germany

# Multiple days (next 7 days)
python scripts/economic_calendar.py --days 7 --importance high medium --countries "united states"

# JSON to stdout (for automation/piping)
python scripts/economic_calendar.py --date tomorrow --json stdout

# JSON to file (default: calendar_YYYYMMDD.json)
python scripts/economic_calendar.py --days 3 --json file
```

## Options

| Flag | Description | Default |
|------|-------------|---------|
| `--date` | Start date: `today`, `tomorrow`, `yesterday`, or `YYYY-MM-DD` | `today` |
| `--days` | Fetch range of N days (overrides `--date`) | — |
| `--importance` | Filter levels: `low`, `medium`, `high` (space-separated) | `high` |
| `--countries` | Countries (space-separated, quotes for multi-word) | `united states` |
| `--timezone` | Timezone for event times | `GMT +1:00` |
| `--json` | JSON mode: `file`, `stdout`, `none` | `file` |

## Countries

Available country names (use quotes for multi-word):
- `united states`
- `germany`
- `united kingdom`
- `france`
- `japan`
- `china`
- `canada`
- `australia`
- `switzerland`
- `eurozone`

## Timezones

Common timezones:
- `GMT +1:00` — Berlin/Vienna (CET) ✓ default
- `GMT +2:00` — Berlin/Vienna (CEST)
- `GMT -5:00` — New York (EST)
- `GMT -4:00` — New York (EDT)
- `GMT` — UTC

## Output Formats

### Table (default)
Human-readable formatted table to stdout:
```
================================================================================
  Economic Calendar  |  25.02.2026
  Countries: United States  |  Timezone: GMT +1:00  |  Importance: high
================================================================================
  Time    Imp.     Curr.  Event                          Forecast  Previous  Actual
  ------- -------- ------ ------------------------------ --------- --------- --------
  14:30   high     USD    Unemployment Claims            215K      219K      —
  14:30   high     USD    Core PPI m/m                   0.3%      0.4%      —
================================================================================
  2 event(s) found.
```

### JSON
```json
{
  "from": "2026-02-25",
  "to": "2026-02-25",
  "timezone": "GMT +1:00",
  "importances": ["high"],
  "countries": ["united states"],
  "events": [
    {
      "date": "Tuesday, February 25, 2026",
      "time": "14:30",
      "currency": "USD",
      "importance": 3,
      "event": "Unemployment Claims",
      "actual": "",
      "forecast": "215K",
      "previous": "219K"
    }
  ]
}
```

## Dependencies

```bash
pip install requests beautifulsoup4 lxml
```

## Notes

- **Source:** Investing.com (server-side rendered, reliable CSS selectors)
- **Rate limiting:** Built-in delays between requests
- **Session handling:** Maintains cookies across requests for proper session state
- **Data validity:** Historical data + 1+ years forward
- **No API key:** All data is publicly scraped

## Use in Workflows

```bash
# Daily briefing — get today's high/medium US events as JSON
python3 skills/economic-calendar/scripts/economic_calendar.py \
  --date today \
  --importance high medium \
  --countries "united states" \
  --json stdout
```
