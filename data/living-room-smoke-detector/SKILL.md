---
name: living-room-smoke-detector
description: Simple smoke/fire detector for living room. Queries Dirigera air sensor every 5 minutes, detects dangerous PM2.5 over 250 or CO2 over 2000 levels, and broadcasts emergency alert on Mac speaker continuously until air quality normalizes. Acts as backup to regular smoke alarms.
---

# Living Room Smoke Detector

A simple, focused smoke and fire detection system that monitors the living room ALPSTUGA air sensor via the Dirigera hub.

## What It Does

- **Queries Dirigera directly** every 5 minutes (not from database)
- **Simple state only** - keeps just the latest reading, no history
- **Detects danger:** PM2.5 > 250 µg/m³ OR CO2 > 2000 ppm
- **Continuous alert** - plays "Attention! Abnormal smoke level detected" on Mac speaker
- **Loops until cleared** - keeps playing every 5 seconds until air quality normalizes
- **Backup smoke alarm** - works alongside your regular smoke detector

## Setup

### 1. Copy Alert Sound (optional)

If you already have the alert sound from the air monitor skill:

```bash
cp ~/.openclaw/workspace/skills/living-room-air-monitor/data/smoke_alert_message.mp3 \
   ~/.openclaw/workspace/skills/living-room-smoke-detector/data/alert.mp3
```

Otherwise it will auto-generate on first run.

### 2. Cron Setup

Add to crontab to check every 5 minutes:

```bash
*/5 * * * * /opt/homebrew/bin/python3 /Users/macmini/.openclaw/workspace/skills/living-room-smoke-detector/scripts/smoke_detector.py >> /tmp/smoke_detector.log 2>&1
```

## Usage

### Manual Check

```bash
python3 ~/.openclaw/workspace/skills/living-room-smoke-detector/scripts/smoke_detector.py
```

### View Status

```bash
# Latest reading
cat ~/.openclaw/workspace/skills/living-room-smoke-detector/data/detector_state.json

# Log
tail -f /tmp/smoke_detector.log
```

## How It Works

1. **Cron triggers** every 5 minutes
2. **Fetches data** directly from Dirigera hub
3. **Checks thresholds:**
   - PM2.5 > 250 µg/m³ (smoke particles)
   - CO2 > 2000 ppm (combustion byproduct)
4. **If danger detected:**
   - Saves state (alert_active = true)
   - Enters alert loop
   - Plays alert sound every 5 seconds
   - Re-checks sensor between plays
   - **Exits loop** when air clears
5. **If normal:** Updates state and exits

## State File

`data/detector_state.json`:

```json
{
  "latest_reading": {
    "pm25": 3,
    "co2": 525,
    "time": "2026-02-25T20:30:00"
  },
  "alert_active": false,
  "last_check": "2026-02-25T20:30:00"
}
```

## Alert Behavior

When danger is detected:
- Mac speaker plays: *"Attention! Abnormal smoke level detected"*
- Waits 5 seconds
- Checks sensor again
- Repeats until PM2.5 ≤ 250 AND CO2 ≤ 2000
- **Press Ctrl+C** to stop manually if needed

## Files

| File | Purpose |
|------|---------|
| `scripts/smoke_detector.py` | Main detection script |
| `data/alert.mp3` | Alert sound file |
| `data/detector_state.json` | Latest reading and status |

## Dependencies

- Python 3.x
- Dirigera hub access (192.168.1.100)
- Auth token at `~/.openclaw/workspace/.dirigera_token`
- macOS `afplay` (built-in)
- `say` and `ffmpeg` (for alert generation)

## Differences from Air Monitor Skill

| Feature | Air Monitor | Smoke Detector |
|---------|-------------|----------------|
| Data storage | Full SQLite database | Latest reading only |
| Query source | Database | Dirigera directly |
| Frequency | Every 2 min | Every 5 min |
| Purpose | History + charts | Immediate alerting |
| Alert | Single play | Continuous loop |
| Complexity | Multi-feature | Single-purpose |

Use **both** for complete coverage: air monitor for data logging, smoke detector for focused alerting.
