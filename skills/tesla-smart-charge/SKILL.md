---
name: tesla-smart-charge
description: "Smart Tesla charging scheduler with charge limit management. Runs
  daily to check a schedule file and charge only on configured dates.
  Automatically manages charge limits during sessions (default 100%) and after
  sessions (default 80%). Use when you need to: (1) Charge your Tesla on
  specific planned dates, (2) Manage charge limits for battery health, (3)
  Calculate optimal charging start times, (4) Set up recurring daily checking
  with flexible charge scheduling."
---


# Tesla Smart Charge Optimizer

Schedule Tesla charging to reach target battery % by a specific time. Runs daily via cron to check a schedule file and only charges on configured dates.

## Security & Dependencies

**Required:**
- Environment variable: `TESLA_EMAIL` (your Tesla account email)
- Skill dependency: `tesla` skill must be installed and properly configured with Tesla API credentials

**Security improvements (v1.1.0+):**
- ✅ No shell injection risk: Uses argument lists instead of shell=True
- ✅ Email validation: TESLA_EMAIL is validated before use
- ✅ Input validation: Charge limits are validated (0-100% range)
- ✅ Secure env passing: Credentials passed via environment variables, not string interpolation
- ✅ Explicit dependencies: Metadata declares required env vars and skill dependencies

## Quick Start

### 1. Set Up Schedule

Copy the example schedule file:

```bash
cp skills/tesla-smart-charge/references/tesla-charge-schedule-example.json \
   memory/tesla-charge-schedule.json
```

Edit `memory/tesla-charge-schedule.json` with your planned charge dates:

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

## Cron Setup (Recommended)

### Option 1: Daily Check at Midnight (Simple)

```bash
clawdbot cron add \
  --name "Tesla daily charge check" \
  --schedule "0 0 * * *" \
  --task "TESLA_EMAIL=your@email.com python3 /path/to/skills/tesla-smart-charge/scripts/tesla-smart-charge.py --check-schedule"
```

### Option 2: Daily Check + Session Management (Recommended)

For better charge limit management, run both:

**At midnight (initialize daily charge):**
```bash
clawdbot cron add \
  --name "Tesla daily charge check" \
  --schedule "0 0 * * *" \
  --task "TESLA_EMAIL=your@email.com python3 /path/to/skills/tesla-smart-charge/scripts/tesla-smart-charge.py --check-schedule"
```

**Every 30 minutes during active hours (manage session limits):**
```bash
clawdbot cron add \
  --name "Tesla session management" \
  --schedule "*/30 8-23 * * *" \
  --task "TESLA_EMAIL=your@email.com python3 /path/to/skills/tesla-smart-charge/scripts/tesla-smart-charge.py --manage-session"
```

The second job ensures charge limits are properly updated throughout the day:
- ✅ During session: Maintains 100% (or user-specified) limit
- ✅ After session: Applies 80% (or user-specified) limit for battery health

## How It Works

**Each day at midnight (or whenever cron runs):**

1. Script checks `memory/tesla-charge-schedule.json`
2. If today's date is in the charges array → executes charge plan
   - Fetches current battery level
   - Calculates optimal start time
   - **Sets charge limit to session limit (default 100%)**
   - Displays charge details
   - Shows **next scheduled charge date**
3. If today is NOT scheduled → applies post-charge limit
   - **Sets charge limit to default 80%** (or user-specified)
   - Still displays **next scheduled charge date**

**Session Management:**
- **During charge session:** Charge limit = `charge_limit_percent` (default 100%)
- **After charge session expires:** Charge limit = `post_charge_limit_percent` (default 80%)

**Result:** One cron job that handles both charging and limit management — no need to create new jobs for each date!

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

**Fields:**
- `date`: YYYY-MM-DD format (when to charge)
- `target_battery`: Target battery % (default: 100)
- `target_time`: HH:MM when charging should complete (default: 08:00)
- `charge_limit_percent`: Charge limit **during session** (default: 100%, optional)
- `post_charge_limit_percent`: Charge limit **after session ends** (default: 80%, optional)

## Environment Setup

### Tesla Email

```bash
export TESLA_EMAIL="your@email.com"
```

### Optional: Customize Charger Power

Default: 2.99 kW (home charger, ~13A @ 230V)

Adjust in cron task or when calling manually:

```bash
--charger-power 3.7      # 16A @ 230V
--charger-power 7.4      # 32A @ 230V (dual-phase)
```

## Commands

### Check Schedule for Today

```bash
TESLA_EMAIL="your@email.com" python3 scripts/tesla-smart-charge.py --check-schedule
```

Output:
- ✅ If scheduled: Shows charge plan + charge limits + next date
- ❌ If not scheduled: Shows next scheduled date + applies default 80% limit

### Manage Active Session (Run During or After Charge)

```bash
TESLA_EMAIL="your@email.com" python3 scripts/tesla-smart-charge.py --manage-session
```

This command:
- Checks if today's charge session is active
- **During session:** Sets charge limit to session limit (default 100%)
- **After session:** Sets charge limit to post-charge limit (default 80%)
- **No session:** Applies default 80% limit

**Tip:** Run this hourly or every 30 minutes during active charging days for real-time limit management.

### Show All Scheduled Charges

```bash
python3 scripts/tesla-smart-charge.py --show-schedule
```

### Show Last Charge Plan

```bash
python3 scripts/tesla-smart-charge.py --show-plan
```

## Examples

### Daily 100% Charge (Mon-Fri)

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

### Smart 80% for Battery Health (Every 3 Days)

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

## Charge Time Estimation

Charge time is calculated as:

```
energy_needed_kwh = (battery_capacity × (target - current) / 100) / charge_efficiency
charge_time_hours = energy_needed_kwh / charger_power_kw
start_time = target_time - charge_time_hours - margin_minutes
```

Where:
- `battery_capacity`: Vehicle battery size (kWh, default: 75)
- `charger_power_kw`: Your charger's power (kW, default: 2.99)
- `charge_efficiency`: ~0.92 (typical AC charging)
- `margin_minutes`: Buffer before target (default: 5 min)

**Example:** 75 kWh battery at 50%, charging to 100% by 08:00 with 2.99 kW:
- Energy needed: (75 × 50% / 100) / 0.92 = 40.8 kWh
- Charge time: 40.8 / 2.99 ≈ 13.6 hours
- Start time: 08:00 - 13.6h - 5min ≈ 18:25 previous day

## Workflow Tips

**Add new charges:** Edit `memory/tesla-charge-schedule.json` — cron picks up changes on next run

**Plan ahead:** Add weeks of charges in advance, script handles date logic

**One cron job:** No need to create separate jobs — one daily check does it all

**See what's next:** Each run displays the next scheduled charge date

## Parameters

When calling manually with `--target-time`:

```bash
python3 scripts/tesla-smart-charge.py \
  --target-time "HH:MM" \
  --target-battery 100 \
  --charger-power 2.99 \
  --battery-capacity 75 \
  --margin-minutes 5
```

For schedule-based operation, use `--check-schedule` (reads from JSON file).

## References

- **CRON_SETUP.md** - Full cron integration guide
- **API_REFERENCE.md** - Advanced parameters and formulas
- **tesla-charge-schedule-example.json** - Schedule file template
