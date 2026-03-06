# Tesla Smart Charge Optimizer - Skill Package

This folder contains a complete reusable skill for intelligent Tesla charging automation with charge limit management.

## Files

- `SKILL.md` - Skill documentation and usage guide
- `scripts/tesla-smart-charge.py` - Main charging optimizer script with limit management
- `references/cron_setup.md` - Cron automation setup guide
- `references/api_reference.md` - Complete parameter and formula reference
- `references/tesla-charge-schedule-example.json` - Example schedule file

## Installation

The skill is ready to use. Ensure the Tesla skill is installed:

```bash
clawdhub install tesla
```

## Quick Start

1. Copy the schedule template:
```bash
cp references/tesla-charge-schedule-example.json ../memory/tesla-charge-schedule.json
```

2. Edit memory/tesla-charge-schedule.json with your planned charges and limits

3. Set up cron jobs (see SKILL.md for options):
```bash
# Daily check at midnight
clawdbot cron add \
  --name "Tesla daily charge check" \
  --schedule "0 0 * * *" \
  --task "TESLA_EMAIL=your@email.com python3 /path/to/skills/tesla-smart-charge/scripts/tesla-smart-charge.py --check-schedule"

# Session management every 30 min (8 AM - 11 PM)
clawdbot cron add \
  --name "Tesla session management" \
  --schedule "*/30 8-23 * * *" \
  --task "TESLA_EMAIL=your@email.com python3 /path/to/skills/tesla-smart-charge/scripts/tesla-smart-charge.py --manage-session"
```

## How It Works

- **Daily cron at midnight** checks if today's charge is scheduled
- **If scheduled** → Sets charge limit to session limit (default 100%)
- **If not scheduled** → Sets charge limit to post-charge limit (default 80%)
- **Session management** cron (every 30 min) ensures limits are up-to-date

## Key Features

✅ **Automatic charge limit management** (during & after sessions)
✅ Default limits: 100% during session, 80% after (battery health)
✅ Dynamic battery calculation (fetches real current battery)
✅ Schedule-based charging (only charge on planned days)
✅ Customizable charger power (13A, 16A, 32A, etc.)
✅ Automatic start time calculation
✅ Next charge shown after each run
✅ JSON plan output for integration
✅ Multi-vehicle support

## Usage Commands

**Check if charge scheduled for today:**
```bash
TESLA_EMAIL="your@email.com" python3 scripts/tesla-smart-charge.py --check-schedule
```

**Manage active session and limits:**
```bash
TESLA_EMAIL="your@email.com" python3 scripts/tesla-smart-charge.py --manage-session
```

**Show all scheduled charges:**
```bash
python3 scripts/tesla-smart-charge.py --show-schedule
```

**Show previous plan:**
```bash
python3 scripts/tesla-smart-charge.py --show-plan
```

## Schedule File Format

```json
{
  "charges": [
    {
      "date": "2026-02-01",
      "target_battery": 100,
      "target_time": "08:00",
      "charge_limit_percent": 100,
      "post_charge_limit_percent": 80
    },
    {
      "date": "2026-02-03",
      "target_battery": 80,
      "target_time": "07:00",
      "charge_limit_percent": 100,
      "post_charge_limit_percent": 80
    }
  ]
}
```

**New fields for charge limit management:**
- `charge_limit_percent` - Limit during session (default: 100%, optional)
- `post_charge_limit_percent` - Limit after session (default: 80%, optional)

## Created

2026-01-31 - Initial version with schedule-based daily checking
2026-02-02 - Added charge limit management (during & after sessions)
