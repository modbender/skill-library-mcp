---
name: daily-briefing
description: Automated daily morning briefing generator. Fetches weather, calendar, news, AI/tech updates, OpenClaw insights, and actionable tips. Delivers via iMessage at 7am daily.
homepage: https://github.com/nudge/openclaw-skills/tree/main/daily-briefing
metadata:
  {
    "openclaw":
      {
        "emoji": "📰",
        "requires": { "bins": ["curl", "python3"] },
        "schedule": "0 7 * * *",
        "delivery": "paulkingham@mac.com",
      },
  }
---

# Daily Morning Briefing

An automated daily briefing that compiles weather, calendar, news, AI/tech updates, and OpenClaw insights into a concise morning message delivered via iMessage.

## What It Does

Every morning at 7am, the briefing delivers:

1. **Weather** – Current conditions and forecast for Leyton, London
2. **Calendar** – Today's events and context
3. **Top 5 News** – Headlines from trusted sources
4. **AI/Tech Pulse** – 3-4 interesting developments in AI and technology
5. **OpenClaw Deep Dive** – News, new skills, community highlights, suggestions
6. **Two Things to Try** – Actionable improvements for your workflow

## Quick Start

### Run manually

```bash
cd /Users/nudge/openclaw/skills/daily-briefing
./scripts/generate-briefing.sh
```

### Send via iMessage

```bash
cd /Users/nudge/openclaw/skills/daily-briefing
./scripts/send-briefing.sh paulkingham@mac.com
```

## Configuration

Edit `/Users/nudge/openclaw/skills/daily-briefing/config/config.yaml`:

```yaml
location:
  city: "Leyton"
  region: "London"
  country: "UK"
  latitude: 51.5667
  longitude: -0.0167

delivery:
  recipient: "paulkingham@mac.com"
  channel: "imessage"
  time: "07:00"
  timezone: "Europe/London"

content:
  news_sources:
    - "bbc"
    - "guardian"
    - "techcrunch"
  ai_sources:
    - "openai"
    - "anthropic"
    - "hacker-news"
  max_news_items: 5
  max_ai_items: 4

preferences:
  temperature_unit: "celsius"
  include_weather_icon: true
  include_calendar_details: true
```

## Cron Setup

The briefing runs automatically via OpenClaw's cron system:

```bash
# Check current cron jobs
openclaw cron list

# The briefing is pre-configured. To update schedule:
openclaw cron update daily-briefing --schedule="0 7 * * *"
```

### Manual cron entry (if needed)

Add to your system crontab (runs in OpenClaw context):

```cron
0 7 * * * cd /Users/nudge/openclaw/skills/daily-briefing && ./scripts/generate-and-send.sh
```

## Scripts

| Script | Purpose |
|--------|---------|
| `generate-briefing.sh` | Generates briefing text to stdout |
| `send-briefing.sh <recipient>` | Generates and sends via iMessage |
| `generate-and-send.sh` | Full pipeline (used by cron) |
| `lib/weather.py` | Weather fetching module |
| `lib/news.py` | News aggregation module |
| `lib/calendar.py` | Calendar context module |
| `lib/ai_pulse.py` | AI/tech news module |
| `lib/openclaw_dive.py` | OpenClaw insights module |

## Customization

### Change location

Edit `config/config.yaml` and update the `location` section.

### Add news sources

Modify `lib/news.py` to add RSS feeds or APIs. Default sources:
- BBC News
- The Guardian
- TechCrunch
- Hacker News

### Change delivery time

Update the cron schedule:
```bash
openclaw cron update daily-briefing --schedule="0 8 * * *"  # 8am instead
```

### Customize content sections

Edit `scripts/generate-briefing.sh` and comment out sections you don't want:

```bash
# Sections (comment out to disable)
SECTIONS=(
  weather
  calendar
  news
  ai_pulse
  openclaw_dive
  suggestions
)
```

## Output Format

The briefing produces a well-formatted message like:

```
📰 Good morning! Here's your briefing for Monday, February 16

🌤️ Weather in Leyton
   Partly cloudy, 8°C / 46°F
   High: 12°C · Low: 5°C
   💧 10% rain · 💨 12km/h wind

📅 Today
   09:00 - Team standup
   14:00 - Client call (Zoom)

📰 Top Stories
   • Headline one...
   • Headline two...
   • Headline three...
   • Headline four...
   • Headline five...

🤖 AI/Tech Pulse
   • OpenAI releases new feature...
   • Anthropic updates Claude...
   • Hacker News trending: ...

🦾 OpenClaw Deep Dive
   New this week: skill-name (description)
   Community highlight: ...
   Try this: ...

💡 Two Things to Try
   1. First suggestion...
   2. Second suggestion...
```

## Troubleshooting

### Weather not loading

- Check internet connection
- Verify wttr.in is accessible: `curl wttr.in/London?format=3`
- Try fallback to Open-Meteo API

### Calendar empty

- Ensure calendar access permissions for terminal
- Check that Calendar.app has events today
- Verify `icalBuddy` is installed (optional, for richer calendar data)

### iMessage not sending

- Confirm Messages.app is signed in
- Check recipient address is correct
- Verify Automation permission in System Settings
- Test manually: `imsg send --to "recipient" --text "test"`

### News not appearing

- News sources may require API keys for production use
- Default implementation uses web search for headlines
- For production, add API keys to `config/secrets.yaml`

## Dependencies

**Required:**
- `curl` – for web requests
- `python3` – for data processing

**Optional (enhanced features):**
- `imsg` – for iMessage delivery (via Homebrew: `brew install steipete/tap/imsg`)
- `icalBuddy` – for rich calendar data
- `jq` – for JSON processing

## Architecture

```
┌─────────────────┐
│  Cron (7am)     │
└────────┬────────┘
         │
┌────────▼────────┐
│ generate-and-   │
│ send.sh         │
└────────┬────────┘
         │
    ┌────┴────┬────────┬────────┬──────────┬──────────┐
    ▼         ▼        ▼        ▼          ▼          ▼
┌───────┐ ┌──────┐ ┌──────┐ ┌────────┐ ┌──────────┐ ┌─────────┐
│weather│ │calendar│ │news │ │ai_pulse│ │openclaw  │ │suggestions│
│  .py  │ │  .py   │ │ .py │ │  .py   │ │_dive.py  │ │  .py    │
└────┬──┘ └───┬────┘ └──┬───┘ └────┬───┘ └────┬─────┘ └────┬────┘
     └─────────┴─────────┴──────────┴──────────┴────────────┘
                             │
                    ┌────────▼────────┐
                    │  format-output  │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │  imsg send      │
                    └─────────────────┘
```

## Updates & Maintenance

The skill self-documents its last run. Check status:

```bash
cat /Users/nudge/openclaw/skills/daily-briefing/.last-run
cat /Users/nudge/openclaw/skills/daily-briefing/.last-status
```

To update the skill itself:
```bash
cd /Users/nudge/openclaw/skills/daily-briefing
git pull  # If tracked in git
```

## Ideas to Extend

- **Weekend edition** – Different content for Saturdays/Sundays
- **Pre-meeting briefings** – 15-min before calendar events
- **Travel mode** – Weather for destination city
- **Stock/crypto prices** – Add financial tickers
- **Podcast recommendations** – Based on listening history
- **Fitness summary** – Previous day's activity stats
- **Smart home status** – Brief overview of connected devices
