# SKILL.md - MiniMax Usage Tracker

## Skill Information

- **Skill Name**: openclaw-skill-minimax-tracker
- **Version**: 1.0.0
- **Author**: QiaoTuCodes (Weiran), Yanyan
- **Description**: Track and monitor MiniMax API usage with progress bars and reminders for OpenClaw
- **Repository**: https://github.com/QiaoTuCodes/openclaw-skill-minimax-tracker

## Overview

This skill provides real-time tracking for MiniMax API usage. It calculates usage based on prompts consumed, tracks remaining quota, and displays progress in a compact bar format. Designed for OpenClaw agents to monitor API usage between resets.

## Features

- Real-time prompts usage tracking
- Visual progress bar with key metrics (RST/TTL/PKG/USE/REM/NXT)
- Automatic reset time calculation (15:00-20:00 UTC+8)
- JSON-based persistent storage
- Cron-ready for scheduled reminders

## Usage

### Commands

```bash
# Add usage (after API call)
python3 minimax_tracker.py add [n]

# View detailed status
python3 minimax_tracker.py status

# View compact progress bar
python3 minimax_tracker.py compact
```

### Output Format

```
[████████████████████] 98% RST:18:00 TTL:1h40m PKG:Starter USE:2/40 REM:38 NXT:19:19
```

### Integration with OpenClaw

```python
# In your skill or agent code
import subprocess

# Track usage after each API call
result = subprocess.run(
    ["python3", "path/to/minimax_tracker.py", "add", "1"],
    capture_output=True, text=True
)
```

### Cron Setup (Every 3 Hours)

```json
{
  "name": "minimax-usage-check",
  "schedule": "0 */3 * * *",
  "payload": {
    "kind": "agentTurn",
    "message": "Run: python3 ~/openclaw-workspace/skills/openclaw-skill-minimax-tracker/minimax_tracker.py compact"
  }
}
```

## Configuration

Edit the CONFIG dict in minimax_tracker.py:

| Parameter | Default | Description |
|-----------|---------|-------------|
| max_prompts | 40 | Monthly prompts limit |
| reset_hour_start | 15 | Reset window start (UTC+8) |
| reset_hour_end | 20 | Reset window end (UTC+8) |
| check_interval_hours | 3 | Reminder interval |

## Data Storage

Usage data is stored in:
```
~/.openclaw/workspace/minimax_usage_data.json
```

Format:
```json
{
  "usage_records": [
    {"time": "2026-02-27T16:19:00", "prompts": 1}
  ],
  "current_usage": 2,
  "last_reset": "2026-02-27T18:00:00",
  "last_check": "2026-02-27T16:23:00"
}
```

## Dependencies

- Python 3.8+ (standard library only, no pip packages needed)

## Installation

```bash
# Copy to OpenClaw skills folder
cp -r openclaw-skill-minimax-tracker ~/openclaw-workspace/skills/
```

## License

MIT License - See LICENSE file
