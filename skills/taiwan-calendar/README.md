# Taiwan Calendar Plugin

Query Taiwan government calendar for accurate working day and holiday information.

## Overview

This plugin solves Claude Code's knowledge cutoff issues with Taiwan dates by querying government open data APIs
in real-time. Get accurate information about:

- Today's date and working day status
- Specific date queries (working day/holiday)
- Working day counts in date ranges
- N working days calculations
- Next working day/holiday lookups

## Installation

### From Local Plugin

```bash
# Install from this directory
claude plugin install ./plugins/taiwan-calendar
```

### From Marketplace (if published)

```bash
claude plugin install taiwan-calendar
```

## Usage

Once installed, Claude will automatically use this skill when you ask Taiwan calendar-related questions:

```
You: "今天是工作日嗎？"
Claude: [Uses taiwan-calendar skill]
       "今天 2025-01-06 (週一) 是工作日。"

You: "5 個工作日後是哪天？"
Claude: [Uses taiwan-calendar skill]
       "從今天算起 5 個工作日後是 2025-01-13 (週一)。"
```

## Features

### Basic Queries

- **Today's date**: Current Taiwan date (UTC+8) with weekday and working day status
- **Date check**: Query any date for holiday/working day information
- **Flexible input**: Supports YYYY-MM-DD, YYYY/MM/DD, MM/DD formats

### Range Queries

- **Working day count**: Calculate working days between two dates
- **Holiday listing**: Show holidays in a date range

### Advanced Calculations

- **Add working days**: Find date N working days from today or specific date
- **Next working day**: Find the next working day
- **Next holiday**: Find the next national holiday

## Data Source

- **Primary**: Taiwan government open data platform (data.gov.tw)
- **Fallback**: New Taipei City open data
- **Cache**: 1-hour local cache for performance

## Commands Reference

All commands are automatically invoked by Claude. For manual testing:

```bash
# Today's info
uv run --managed-python scripts/taiwan_calendar.py today

# Check specific date
uv run --managed-python scripts/taiwan_calendar.py check 2025-01-01

# Count working days
uv run --managed-python scripts/taiwan_calendar.py range 2025-01-01 2025-01-31

# N working days later
uv run --managed-python scripts/taiwan_calendar.py add-days 5

# Next working day
uv run --managed-python scripts/taiwan_calendar.py next-working

# Next holiday
uv run --managed-python scripts/taiwan_calendar.py next-holiday
```

## Requirements

- Python 3.11+ (automatically managed by `uv`)
- Internet connection (for API queries)
- Dependencies (automatically installed):
  - `requests`
  - `python-dateutil`

## Technical Details

- **Timezone**: Asia/Taipei (UTC+8)
- **Cache location**: System temp directory (cross-platform)
- **Cache expiry**: 1 hour
- **Supported platforms**: macOS, Linux, Windows

## Troubleshooting

### API Unavailable

If government APIs are down, the plugin will:

1. Try fallback API source
2. Use expired cache with warning if network unavailable
3. Show clear error message if all sources fail

### Invalid Date Format

Use supported formats:

- `YYYY-MM-DD` (e.g., 2025-01-06)
- `YYYY/MM/DD` (e.g., 2025/01/06)
- `MM/DD` (e.g., 01/06, assumes current year)

## License

MIT

## Author

pigfoot <pigfoot@gmail.com>

## Version

0.0.1
