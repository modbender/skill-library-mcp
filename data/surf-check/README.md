# 🏄 surf-check

A surf forecast decision engine that identifies when conditions are worth paddling out. Evaluates forecasts against configurable thresholds and outputs surfable conditions to stdout — what you do with that output is up to you.

Built as an AI agent skill for [OpenClaw](https://openclaw.ai), but works with any AI agent framework, automation pipeline, or as a standalone CLI.

## What It Does

surf-check **evaluates** surf forecasts and **outputs** conditions that meet your criteria. It does not send notifications directly — it's the decision layer, not the delivery layer.

```
[Forecast Data] → [surf-check] → [stdout] → [Your notification system]
```

**As a standalone CLI:** Outputs surfable conditions to stdout. Pipe to any notification system.

**As an AI agent skill:** Your agent reads the output and handles alerting (see [SKILL.md](SKILL.md)).

## Features

- **Tiered decision logic** — Requires higher confidence for longer-range forecasts
- **State tracking** — No duplicate output for the same forecast
- **Quiet hours** — Suppress output during configurable hours (default 10pm-6am)
- **Premium support** — Use your Surfline Premium subscription for 16-day forecasts
- **NOAA buoy data** — Cross-reference forecasts with real buoy readings
- **Cron-ready** — Designed for periodic automated checks

## How It Works

Surf forecasts get less accurate the further out you look. surf-check adjusts its confidence threshold accordingly:

| Days Out | Minimum Rating | Rationale |
|----------|----------------|-----------|
| 4+ days | Fair-Good or better | Forecasts are fuzzy, need high confidence |
| 1-3 days | Fair or better | Sweet spot for planning |
| Day of | Good or better | Only flag if it's actually firing |

Same-day conditions are suppressed after 8am (dawn patrol has already passed).

> **Note:** These are the default thresholds. All values are fully configurable in `src/types.ts` to match your preferences and local conditions.

## Installation

```bash
git clone https://github.com/kevinmcnamee/surf-check.git
cd surf-check
npm install
```

### For Premium Data (Optional)

If you have a Surfline Premium subscription and want 16-day forecasts:

```bash
# Install Playwright browsers
npx playwright install chromium

# Log in (opens browser for manual login)
npm run login -- --interactive
```

Your session cookies are saved locally and reused for authenticated API requests.

## Configuration

Create a config file at `~/.surf-check.json` (global) or `./surf-check.json` (local):

```json
{
  "spots": [
    { "id": "5842041f4e65fad6a7708a01", "name": "Belmar" },
    { "id": "630d04654da1381c5cb8aeb7", "name": "Long Branch" }
  ],
  "waveMin": 2,
  "waveMax": 6,
  "forecastDays": 7,
  "quietHours": {
    "enabled": true,
    "start": 22,
    "end": 6
  }
}
```

All fields are optional — defaults are used for any missing values.

### Finding Spot IDs

Go to your spot on Surfline.com. The URL contains the spot ID:

```
https://www.surfline.com/surf-report/spot-name/5842041f4e65fad6a7708a01
                                              └── this is the spot ID
```

### Defaults

| Setting | Default |
|---------|---------|
| spots | Belmar, Long Branch (NJ) |
| waveMin | 2 ft |
| waveMax | 6 ft |
| forecastDays | 7 |
| quietHours | 10pm - 6am |

### Quiet Hours

Notifications are suppressed during quiet hours (default 10pm-6am). Alerts aren't lost — they're sent on the next check outside quiet hours.

Set `"enabled": false` to output conditions 24/7.

## Usage

### Manual Check

```bash
# Full forecast with conditions
npm run check

# With debug output (shows why each day did/didn't match)
npm run check:debug

# JSON output
npm run check:json
```

Example output:
```
🏄 Checking Surfline forecasts...

📍 Belmar (16th Ave)
----------------------------------------
Wednesday, Feb 18: 3-4ft | Fair | Offshore 7mph
Thursday, Feb 19: 2-3ft | Poor-Fair | Cross-shore 6mph
Saturday, Feb 21: 2-3ft | Fair | Offshore 7mph

========================================
ALERTS
========================================
🏄 **Surf Forecast Summary**

**Belmar (16th Ave)**
• Saturday: 2-3ft (Fair)
```

### Automated Checks (Cron Mode)

```bash
npm run check:cron
```

Cron mode:
- Only outputs **new** surfable conditions
- Updates state file to track what's been output
- Silent if nothing new (perfect for cron jobs)

### State Management

Output history is stored in `data/state.json`:

```json
{
  "lastCheck": "2026-02-18T20:00:00.000Z",
  "alertsSent": {
    "5842041f4e65fad6a7708a01:2026-02-22": "2026-02-18T20:00:00.000Z"
  }
}
```

To reset and re-output all conditions:
```bash
rm data/state.json
```

## Turning Decisions into Alerts

surf-check outputs to stdout. To receive actual notifications, connect it to your preferred delivery method:

### OpenClaw (AI Agent)

The simplest setup. OpenClaw runs surf-check on a schedule and sends output to Telegram, Discord, or any configured channel.

```json
{
  "name": "surf-check",
  "schedule": { "kind": "cron", "expr": "0 */6 * * *", "tz": "America/New_York" },
  "payload": {
    "kind": "systemEvent",
    "text": "Run: cd ~/surf-check && npm run check:cron"
  },
  "sessionTarget": "main"
}
```

### Cron + Webhook

Pipe output to any webhook (Slack, Discord, ntfy, Pushover, etc.):

```bash
#!/bin/bash
OUTPUT=$(cd /path/to/surf-check && npm run check:cron 2>/dev/null)
[ -n "$OUTPUT" ] && curl -d "$OUTPUT" https://your-webhook-url
```

### Cron + Email

```bash
0 */6 * * * cd /path/to/surf-check && npm run check:cron | mail -s "Surf Alert" you@email.com
```

## Project Structure

```
surf-check/
├── src/
│   ├── types.ts              # Type definitions, spot configs
│   ├── providers/
│   │   ├── surfline.ts       # Public API client
│   │   ├── surfline-premium.ts # Authenticated API client
│   │   └── noaa.ts           # NOAA buoy data
│   └── services/
│       ├── alerts.ts         # Alert evaluation logic
│       └── state.ts          # State persistence
├── scripts/
│   ├── check-forecast.ts     # Main CLI script
│   └── login-surfline.ts     # Premium login helper
├── data/
│   ├── session/              # Auth cookies (gitignored)
│   └── state.json            # Alert history (gitignored)
└── package.json
```

## Surfline Rating Scale

| Rating | Value | Description |
|--------|-------|-------------|
| FLAT | 0 | No surf |
| VERY_POOR | 0 | Not worth it |
| POOR | 1 | Frustrating |
| POOR_TO_FAIR | 1-2 | Might get a few |
| FAIR | 2 | Fun for most |
| FAIR_TO_GOOD | 3 | Worth the drive |
| GOOD | 4 | Get out there |
| GOOD_TO_EPIC | 5 | Call in sick |
| EPIC | 5 | Once a year |

## Contributing

PRs welcome! Some ideas:

- [ ] SMS/email notifications
- [ ] Tide-aware alerts (prefer incoming tide)
- [ ] Wind quality scoring
- [ ] Historical accuracy tracking
- [ ] Web dashboard
- [ ] Multi-region support

## License

MIT

## Disclaimer

This tool uses Surfline's undocumented API. It may break if Surfline changes their API. This project is not affiliated with Surfline.

---

*Built for surfers who'd rather be in the water than checking forecasts.*
