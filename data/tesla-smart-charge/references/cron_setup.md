# Cron Integration - Tesla Smart Charge

Set up automatic daily checking with Clawdbot's cron system. The script checks a schedule file and only charges on configured days.

## Quick Setup

Create a cron job that runs at midnight and checks if a charge is scheduled:

```bash
clawdbot cron add \
  --name "Tesla daily charge check" \
  --schedule "0 0 * * *" \
  --task "Check Tesla charge schedule for today: TESLA_EMAIL=your@email.com python3 /path/to/skills/tesla-smart-charge/scripts/tesla-smart-charge.py --check-schedule"
```

## How It Works

1. **Create a schedule file** at `memory/tesla-charge-schedule.json` with your planned charges
2. **Cron runs daily** (e.g., at midnight with `0 0 * * *`)
3. **Script checks** if today matches a scheduled charge date
4. **If yes** → Calculates optimal start time and prepares charging
5. **If no** → Exits silently (no charge runs)
6. **Next charge shown** in output

## Schedule File Format

Copy `tesla-charge-schedule-example.json` to `memory/tesla-charge-schedule.json`:

```json
{
  "charges": [
    {
      "date": "2026-02-01",
      "target_battery": 100,
      "target_time": "08:00"
    },
    {
      "date": "2026-02-03",
      "target_battery": 80,
      "target_time": "07:00"
    }
  ]
}
```

**Fields:**
- `date`: YYYY-MM-DD format (when to charge)
- `target_battery`: % to charge to (default: 100)
- `target_time`: HH:MM when charging should be complete (default: 08:00)

## Usage Commands

### Check if charge is scheduled for today

```bash
TESLA_EMAIL=your@email.com python3 scripts/tesla-smart-charge.py --check-schedule
```

Output:
- ✅ If charge scheduled → Shows details and executes
- ❌ If no charge → Shows next scheduled date

### Show all scheduled charges

```bash
python3 scripts/tesla-smart-charge.py --show-schedule
```

### Show next charge scheduled

Built into `--check-schedule` output

## Cron Payload Example

```json
{
  "kind": "agentTurn",
  "message": "Tesla daily charge check: TESLA_EMAIL=your@email.com python3 /path/to/skills/tesla-smart-charge/scripts/tesla-smart-charge.py --check-schedule",
  "channel": "telegram",
  "to": "YOUR_USER_ID"
}
```

## Workflow

**Day 1:** Edit `memory/tesla-charge-schedule.json` → Add dates/battery targets
**Day 2+:** Cron runs daily → Auto-checks and executes if scheduled
**Result:** Script runs every day but only charges when configured

## Examples

### Daily 100% Charge (Workdays)

```json
{
  "charges": [
    {"date": "2026-02-02", "target_battery": 100, "target_time": "08:00"},
    {"date": "2026-02-03", "target_battery": 100, "target_time": "08:00"},
    {"date": "2026-02-04", "target_battery": 100, "target_time": "08:00"},
    {"date": "2026-02-05", "target_battery": 100, "target_time": "08:00"},
    {"date": "2026-02-06", "target_battery": 100, "target_time": "08:00"}
  ]
}
```

### Smart 80% for Health (Every 3 days)

```json
{
  "charges": [
    {"date": "2026-02-01", "target_battery": 80, "target_time": "07:00"},
    {"date": "2026-02-04", "target_battery": 80, "target_time": "07:00"},
    {"date": "2026-02-07", "target_battery": 80, "target_time": "07:00"}
  ]
}
```

### Variable Targets

```json
{
  "charges": [
    {"date": "2026-02-01", "target_battery": 100, "target_time": "08:00"},
    {"date": "2026-02-02", "target_battery": 80, "target_time": "07:00"},
    {"date": "2026-02-03", "target_battery": 60, "target_time": "06:00"}
  ]
}
```

## Troubleshooting

### "No charge scheduled for today"

This is normal! The script exits gracefully. Check:
- `memory/tesla-charge-schedule.json` exists
- Today's date is in the charges array
- Date format is YYYY-MM-DD

### "TESLA_EMAIL not set"

Set the environment variable:

```bash
export TESLA_EMAIL="your@email.com"
```

### Charge didn't start

- Check if battery is already at target (won't charge if already at %)
- Verify start time calculation is in the future
- Check cron logs for errors

### Modify Schedule

Edit `memory/tesla-charge-schedule.json` directly — next cron run picks up changes automatically.

