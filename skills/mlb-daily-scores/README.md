# ⚾ MLB Daily Scores — OpenClaw Skill

Get daily baseball updates for your favourite MLB team, delivered to any chat channel on a schedule.

**What you get every morning:**

- Yesterday's game recap (score, winning/losing/save pitchers, linescore)
- Today's game preview (opponent, time, venue, probable starters with stats)
- Current injury report for your team

## Quick Start

### 1. Install from ClawHub

```bash
clawhub install mlb-daily-scores
```

### 2. Configure your team

> **Note:** Python dependencies (`MLB-StatsAPI`, `requests`) are installed automatically when you run `clawhub install`. If you need to reinstall them manually, run:
>
> ```bash
> python ~/.openclaw/skills/mlb-daily-scores/setup.py
> ```

Edit `~/.openclaw/openclaw.json`:

```json5
{
  skills: {
    entries: {
      "mlb-daily-scores": {
        enabled: true,
        config: {
          team: "Toronto Blue Jays",
          timezone: "America/Toronto",
        },
      },
    },
  },
}
```

### 3. Set up the daily schedule

```bash
openclaw cron add \
  --name "MLB Daily Scores" \
  --cron "0 9 * * *" \
  --tz "America/Toronto" \
  --session isolated \
  --message "Run the mlb-daily-scores skill" \
  --announce \
  --channel discord \
  --to "channel:YOUR_CHANNEL_ID"
```

That's it! You'll get a daily baseball briefing at 9 AM.

## Configuration Reference

| Key        | Required | Default   | Description                                      |
| ---------- | -------- | --------- | ------------------------------------------------ |
| `team`     | Yes      | —         | Full MLB team name (e.g., `"Toronto Blue Jays"`) |
| `timezone` | No       | System TZ | IANA timezone (e.g., `"America/New_York"`)       |

### Supported Teams

Arizona Diamondbacks, Atlanta Braves, Baltimore Orioles, Boston Red Sox, Chicago Cubs, Chicago White Sox, Cincinnati Reds, Cleveland Guardians, Colorado Rockies, Detroit Tigers, Houston Astros, Kansas City Royals, Los Angeles Angels, Los Angeles Dodgers, Miami Marlins, Milwaukee Brewers, Minnesota Twins, New York Mets, New York Yankees, Oakland Athletics, Philadelphia Phillies, Pittsburgh Pirates, San Diego Padres, San Francisco Giants, Seattle Mariners, St. Louis Cardinals, Tampa Bay Rays, Texas Rangers, Toronto Blue Jays, Washington Nationals.

## Cron Schedule Examples

| Schedule           | Cron Expression | Description                      |
| ------------------ | --------------- | -------------------------------- |
| Morning briefing   | `0 9 * * *`     | Every day at 9:00 AM             |
| Lunchtime update   | `0 12 * * *`    | Every day at noon                |
| After games finish | `0 1 * * *`     | 1:00 AM (after west-coast games) |
| Weekdays only      | `0 9 * * 1-5`   | Mon–Fri at 9:00 AM               |

## On-Demand Usage

You can also get updates anytime by:

- Typing `/mlb-daily-scores` in any chat connected to OpenClaw
- Asking your assistant: _"What happened in the Yankees game yesterday?"_

## How It Works

1. The skill runs `fetch_mlb.py` which calls the free **MLB Stats API** (no API key needed)
2. It fetches yesterday's results, today's schedule, and current injuries
3. The OpenClaw agent formats the data into a clean, readable report
4. The report is delivered to your configured channel

## Requirements

- **Python 3.9+** (for `zoneinfo` module)
- **OpenClaw Gateway** with cron support
- **pip packages**: `MLB-StatsAPI`, `requests`

## Off-Season Behaviour

During the off-season (November–February) or on off-days, the skill silently skips — no messages are sent. It will automatically resume when games are scheduled.

## Troubleshooting

**"Team not found" error**
→ Use the full official team name (e.g., "New York Yankees" not "Yankees" or "NYY")

**No message delivered**
→ Check that the cron job is running: `openclaw cron list`
→ Verify the team has a game: the skill skips days with no games

**Dependency errors**
→ Ensure Python 3.9+ is installed: `python3 --version`
→ Reinstall packages: `pip3 install --user --force-reinstall MLB-StatsAPI requests`

## Publishing

To publish updates to ClawHub:

```bash
clawhub publish ./mlb-daily-scores \
  --slug mlb-daily-scores \
  --name "MLB Daily Scores" \
  --version 1.0.0 \
  --tags latest
```

## License

MIT
