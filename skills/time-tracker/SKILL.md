---
name: time-tracker
description: Track work time per project with start/stop timers and generate
  productivity reports.
---


# Time Tracker

Track work time per project using local JSONL files with start/stop commands.

## Requirements

- File system access for `~/.time-tracker/`
- No external services or API keys needed

## Instructions

### Commands

| Command | Description |
|---------|-------------|
| `start <project> [task]` | Start a timer for a project/task |
| `stop` | Stop the current timer and record entry |
| `status` | Show current running timer |
| `report [today\|week\|month]` | Generate time report |
| `list projects` | List all tracked projects |
| `delete <entry-id>` | Delete a specific entry |

### Data storage

- **Entries**: `~/.time-tracker/entries.jsonl` (one JSON per line)
  ```json
  {"id": "uuid", "project": "webapp", "task": "frontend", "start": "2025-01-15T09:00:00+09:00", "end": "2025-01-15T11:30:00+09:00", "minutes": 150}
  ```
- **Current timer**: `~/.time-tracker/current.json`
  ```json
  {"project": "webapp", "task": "frontend", "start": "2025-01-15T09:00:00+09:00"}
  ```

### Report format

```
## ⏱️ Time Report — Week of 2025-01-13

| Project | Task | Hours | Sessions |
|---------|------|-------|----------|
| webapp | frontend | 8.5h | 4 |
| webapp | backend | 3.0h | 2 |
| blog | writing | 2.5h | 3 |
| **Total** | | **14.0h** | **9** |

### Daily Breakdown
- Mon: 4.5h | Tue: 3.0h | Wed: 2.5h | Thu: 4.0h | Fri: 0h
```

### Implementation

Create `~/.time-tracker/` directory if it doesn't exist. Use `date -Iseconds` for timestamps. Calculate minutes as `(end - start) / 60`. Append entries to JSONL file for easy parsing with `jq` or Python.

## Edge Cases

- **Forgot to stop**: If `current.json` exists on next `start`, warn and ask: stop previous (auto-calculate) or discard?
- **Midnight crossing**: A timer started at 23:00 and stopped at 01:00 = 2 hours, not negative.
- **Timezone changes**: Store all times with timezone offset (ISO 8601). Convert for display.
- **Empty report period**: Show "No entries" rather than an empty table.
- **Concurrent timers**: Only one timer at a time. Stop the current one before starting a new one.

## Security

- Time data is stored locally — no external transmission.
- Project/task names may reveal client work — keep `~/.time-tracker/` private.
