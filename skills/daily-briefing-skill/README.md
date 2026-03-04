# Daily Briefing Skill for OpenClaw

An automated morning briefing that delivers weather, calendar, news, AI/tech updates, OpenClaw insights, and actionable tips directly to your messaging app.

## Features

- 🌤️ **Weather** — Current conditions and forecast for your location
- 📅 **Calendar** — Today's events and upcoming deadlines
- 📰 **Top News** — Headlines from trusted sources
- 🤖 **AI/Tech Pulse** — Latest developments in AI and technology
- 🦾 **OpenClaw Deep Dive** — New skills, community highlights, and tips
- 💸 **AI Spend Tracker** — Track your AI model usage and costs (via codexbar)
- 💡 **Two Things to Try** — Actionable suggestions to improve your workflow

## Installation

1. Clone or download this skill to your OpenClaw skills directory:
```bash
cd ~/openclaw/skills
git clone https://github.com/yourusername/daily-briefing.git
```

2. Install dependencies:
```bash
# Ensure you have these tools installed:
# - curl (for weather and news)
# - python3 (for data processing)
# - imsg (for iMessage delivery: brew install steipete/tap/imsg)
# - codexbar (optional, for cost tracking: brew install steipete/tap/codexbar)
```

3. Configure the skill:
```bash
cd daily-briefing
cp config/config.yaml.example config/config.yaml
# Edit config.yaml with your details
```

4. Test it:
```bash
./scripts/generate-briefing.sh
```

5. Send via iMessage:
```bash
./scripts/send-briefing.sh your-email@example.com
```

## Cron Setup

Add to your OpenClaw cron or system crontab:

```cron
0 7 * * * cd ~/openclaw/skills/daily-briefing && ./scripts/generate-and-send.sh
```

Or use OpenClaw's cron system:
```bash
openclaw cron add --name="Daily Briefing" --schedule="0 7 * * *" \
  --command="cd ~/openclaw/skills/daily-briefing && ./scripts/generate-and-send.sh"
```

## Configuration

Edit `config/config.yaml` to customize:

- **Location** — Set your city/region for weather
- **Delivery** — Your email and preferred channel
- **News sources** — Choose your preferred news outlets
- **Sections** — Enable/disable specific briefing sections

## Customization

### Adding News Sources

Edit `scripts/lib/news.py` and add your preferred RSS feeds or APIs.

### Changing the Voice

The briefing uses a conversational British tone by default. Edit `scripts/generate-briefing.sh` to change the style.

### Adding New Sections

1. Create a new Python module in `scripts/lib/`
2. Add it to `scripts/generate-briefing.sh`
3. Update `print_section` call with your emoji and title

## Requirements

- OpenClaw or compatible AI assistant framework
- macOS (for iMessage support)
- Python 3.8+
- curl
- Optional: codexbar for cost tracking

## License

MIT License — Feel free to use, modify, and share.

## Credits

Created by Paul (JustAskNudge) and shared with the OpenClaw community.
