# Strava Python - OpenClaw Skill

Query your Strava activities, stats, and workout data through OpenClaw using Python and stravalib.

## Why This Skill?

**Compared to other Strava skills:**
- ✅ **Python-based** (not curl) - easier to extend and maintain
- ✅ **Interactive setup wizard** - no manual JSON configuration
- ✅ **User-friendly** - simple commands, clear output
- ✅ **Auto-refresh tokens** - handles OAuth automatically

## Features

- 📊 View recent activities
- 🏃 Get weekly/monthly running stats
- 🚴 Get weekly/monthly cycling stats
- ⏱️ Check your last workout

## Quick Start

### 1. Install Dependencies

```bash
pip install stravalib
```

### 2. Create Strava API App

1. Go to https://www.strava.com/settings/api
2. Click **"Create App"**
3. Fill in:
   - **Application Name:** OpenClaw Strava
   - **Category:** Tool or Analytics
   - **Website:** `http://localhost`
   - **Authorization Callback Domain:** `localhost`
4. Click **"Create"**
5. Copy your **Client ID** and **Client Secret**

### 3. Run Setup

```bash
python3 setup.py
```

Follow the prompts to authorize your app.

### 4. Test It

```bash
python3 strava_control.py recent
python3 strava_control.py stats
python3 strava_control.py last
```

## Installation for OpenClaw

1. Copy this folder to `~/.openclaw/workspace/skills/strava/` or your OpenClaw skills directory
2. Run the setup script
3. Restart OpenClaw if needed

## Usage with OpenClaw

Ask your OpenClaw assistant:
- "Show my recent Strava activities"
- "What are my Strava stats this week?"
- "What was my last workout?"

## Commands

| Command | Description |
|---------|-------------|
| `recent` | Show recent activities (default: 5) |
| `stats` | Show weekly/monthly stats for running and cycling |
| `last` | Show details of your last activity |

## Requirements

- Python 3.7+
- `stravalib` package
- Strava account (free)
- Strava API credentials (free)

## Configuration

Credentials are stored in `~/.strava_credentials.json`. This file is created automatically during setup and should not be shared.

## Troubleshooting

**"Credentials not found" error:**
- Run `python3 setup.py` first

**403 Forbidden errors:**
- Re-run setup to refresh your authorization
- Check that all required API scopes are granted

**No activities showing:**
- Make sure you have activities in Strava
- Check your Strava privacy settings

## API Limits

Strava API has rate limits:
- 100 requests per 15 minutes
- 1,000 requests daily

## License

MIT

## Contributing

Feel free to open issues or PRs on GitHub!

## Author

Created for the OpenClaw community 🏃‍♂️
