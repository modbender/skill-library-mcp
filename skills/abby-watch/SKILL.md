---
name: abby-watch
description: Simple time display for Abby. Use when you need to know the current time or count down to a specific time.
---

# Abby Watch

Simple time display for quick access.

## Usage

```bash
# Simple time
abby time

# Verbose (full details)
abby time --verbose

# Countdown to a time
abby time --countdown "11:00"
```

## Examples

| Query | Command | Output |
|-------|---------|--------|
| What time is it? | `abby time` | 🕐 08:00 |
| Full details | `abby time --verbose` | Sunday, February 15th, 2026 — 8:00 AM (Australia/Sydney) |
| How long until 11? | `abby time --countdown 11:00` | ⏰ 3小时后 |

## Notes

- Default format: HH:MM
- Verbose includes full date and timezone
- Countdown handles times in 24-hour format (HH:MM)
