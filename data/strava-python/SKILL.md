---
name: strava-python
version: 1.0.0
description: Query Strava activities, stats, and workout data using Python/stravalib with interactive setup
homepage: https://www.strava.com
metadata:
  openclaw:
    emoji: 🏃
    requires:
      bins:
        - python3
    install:
      - id: pip
        kind: pip
        package: stravalib
        label: Install stravalib (pip)
---

# Strava Python

Query your Strava activities, stats, and workout data through OpenClaw using Python and stravalib.

**Why this skill vs others:** Uses Python/stravalib with an interactive setup wizard (vs curl-based skills requiring manual JSON configuration).

## Requirements

- Python 3.7+
- `stravalib` package
- Strava API credentials (free)

## Setup

1. **Install dependencies:**
   ```bash
   pip install stravalib
   ```

2. **Run setup:**
   ```bash
   python3 setup.py
   ```

   This will:
   - Guide you through creating a Strava API app
   - Handle OAuth authentication
   - Save credentials to `~/.strava_credentials.json`

## Commands

**Recent activities:**
```bash
python3 strava_control.py recent
```

**Weekly/monthly stats:**
```bash
python3 strava_control.py stats
```

**Last activity:**
```bash
python3 strava_control.py last
```

## Examples

Ask OpenClaw:
- "Show my recent Strava activities"
- "What are my Strava stats this week?"
- "What was my last Strava workout?"

## Files

- `strava_control.py` - Main controller script
- `setup.py` - Interactive setup wizard
- `SKILL.md` - This file
- `~/.strava_credentials.json` - Credentials (auto-generated)

## Notes

- Requires Strava account (free)
- API credentials are personal and should not be shared
- Rate limits: 100 requests per 15 minutes, 1,000 daily
