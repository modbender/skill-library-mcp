---
name: peloton-stats
description: Fetch and report Peloton cycling workout statistics. Use when the user wants to see their Peloton workout data, weekly cycling stats, ride history, or performance metrics. Hits the Peloton API directly (no dependencies) to pull total rides, duration, calories, output/power, and instructor data for cycling workouts.
user-invocable: true
metadata:
  openclaw:
    requires:
      env:
        - PELOTON_USERNAME
        - PELOTON_PASSWORD
      config:
        - ~/.openclaw/agents/main/agent/auth-profiles.json
    primaryEnv: PELOTON_USERNAME
    emoji: "🚴"
---

# Peloton Stats

Fetch weekly cycling stats directly from the Peloton API. Zero dependencies — uses only Python stdlib.

## Setup

Store your Peloton credentials securely using OpenClaw's credential manager:

```bash
openclaw config set auth.profiles.peloton:default.type api_key
openclaw config set auth.profiles.peloton:default.provider peloton
openclaw config set auth.profiles.peloton:default.username "your-email@example.com"
openclaw config set auth.profiles.peloton:default.password "your-password"
```

Or edit `~/.openclaw/agents/main/agent/auth-profiles.json` directly:

```json
{
  "profiles": {
    "peloton:default": {
      "type": "api_key",
      "provider": "peloton",
      "username": "your-email@example.com",
      "password": "your-password"
    }
  }
}
```

## Usage

### Weekly Report

```bash
python3 ~/.openclaw/skills/peloton-stats/scripts/fetch_stats.py
```

Outputs markdown with:
- Total rides this week
- Total duration, calories, output (kJ)
- Average power (watts), resistance (%), cadence (RPM)
- Recent rides table (date, class, instructor, metrics)

## Data Retrieved

| Metric | Description |
|--------|-------------|
| **Total Rides** | Number of cycling workouts in last 7 days |
| **Duration** | Total minutes ridden |
| **Calories** | Total calories burned |
| **Output** | Total energy in kilojoules (kJ) |
| **Avg Power** | Average watts across all rides |
| **Avg Resistance** | Average resistance % |
| **Avg Cadence** | Average RPM |

## Notes

- Only fetches **cycling** workouts (not running, strength, yoga, etc.)
- Looks back **7 days** from runtime
- Requires active Peloton subscription
- Uses the unofficial Peloton API at `api.onepeloton.com`
