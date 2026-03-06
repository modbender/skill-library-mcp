---
name: mlb-daily-scores
description: Daily MLB baseball scores, box scores, starting pitchers, and injury reports for your favourite team. Covers spring training, regular season, and playoffs. Runs on a schedule or on demand.
user-invocable: true
metadata:
  {
    "openclaw":
      {
        "emoji": "⚾",
        "requires": { "bins": ["python3"] },
        "os": ["darwin", "linux", "win32"],
        "hooks":
          {
            "postInstall": "cd {baseDir} && sed -i 's/\\r$//' *.py *.sh && chmod +x fetch_mlb.py setup.sh && python3 {baseDir}/setup.py",
          },
        "entrypoint": "{baseDir}/.venv/bin/python3 {baseDir}/fetch_mlb.py --config",
        "homepage": "https://clawhub.ai/skills?focus=search&q=mlb-daily-scores",
      },
  }
---

# MLB Daily Scores

Fetches yesterday's game recap and today's upcoming game preview for the user's configured favourite MLB team. Includes spring training, regular season, postseason (Wild Card, Division Series, Championship Series, World Series), and exhibition games.

## Data Source

Uses the free **MLB Stats API** (statsapi.mlb.com). No API key required.

## Setup (one-time)

### 1. Install dependencies

Run the setup script to install the Python packages:

```bash
# macOS/Linux
bash {baseDir}/setup.sh

# Any platform (including Windows)
python {baseDir}/setup.py
```

Or install manually:

```bash
pip install --user MLB-StatsAPI requests
```

### 2. Configure your team

Add this to `~/.openclaw/openclaw.json` under `skills.entries`:

```json5
{
  skills: {
    entries: {
      "mlb-daily-scores": {
        enabled: true,
        config: {
          team: "Toronto Blue Jays", // Your favourite team (full name)
          timezone: "America/Toronto", // Your local timezone (IANA format)
        },
      },
    },
  },
}
```

**Valid team names** — use the full official name:
Arizona Diamondbacks, Atlanta Braves, Baltimore Orioles, Boston Red Sox, Chicago Cubs, Chicago White Sox, Cincinnati Reds, Cleveland Guardians, Colorado Rockies, Detroit Tigers, Houston Astros, Kansas City Royals, Los Angeles Angels, Los Angeles Dodgers, Miami Marlins, Milwaukee Brewers, Minnesota Twins, New York Mets, New York Yankees, Oakland Athletics, Philadelphia Phillies, Pittsburgh Pirates, San Diego Padres, San Francisco Giants, Seattle Mariners, St. Louis Cardinals, Tampa Bay Rays, Texas Rangers, Toronto Blue Jays, Washington Nationals.

### 3. Set up the daily cron job

Ask me to set it up, or run manually:

```bash
openclaw cron add \
  --name "MLB Daily Scores" \
  --cron "0 6 * * *" \
  --tz "America/Toronto" \
  --session isolated \
  --message "Run the mlb-daily-scores skill for my configured team. Use the fetch_mlb.py script, format the results nicely, and include yesterday's recap, today's preview, and any injuries." \
  --announce \
  --channel discord \
  --to "channel:YOUR_CHANNEL_ID"
```

Adjust the parameters:

- `--cron "0 6 * * *"` — time to run (6:00 AM); change to your preferred time
- `--tz` — your timezone
- `--channel` — your preferred channel (discord, telegram, whatsapp, slack, etc.)
- `--to` — channel-specific target (channel ID, phone number, chat ID, etc.)

## How to use

### Automatic (cron)

Once the cron job is set up, the skill runs daily at your configured time and delivers the report to your channel.

### On demand (slash command)

Send `/mlb-daily-scores` in any chat to get an immediate update.

### Manual invocation

Ask me: _"What happened in the Blue Jays game yesterday?"_ or _"Give me today's MLB update"_

## Instructions for the agent

`{baseDir}` in these instructions refers to the directory containing this SKILL.md file. Determine this path from the location of this file (e.g., if this file is at `/home/openclaw/.openclaw/workspace/skills/mlb-daily-scores/skills/mlb-daily-scores/SKILL.md`, then `{baseDir}` is `/home/openclaw/.openclaw/workspace/skills/mlb-daily-scores/skills/mlb-daily-scores`).

When this skill is invoked (via cron, slash command, or user request):

1. **Determine the base directory** — find the directory where this SKILL.md and `fetch_mlb.py` are located. Call this `BASEDIR`.

2. **Read the user's config** from `skills.entries.mlb-daily-scores.config`:
   - `team`: the MLB team name (required)
   - `timezone`: IANA timezone string (optional, defaults to system timezone)

3. **Run the fetch script** using this EXACT command pattern (replacing BASEDIR with the actual path):

   ```bash
   BASEDIR/.venv/bin/python3 BASEDIR/fetch_mlb.py --config
   ```

   **IMPORTANT:** You MUST use the venv Python at `BASEDIR/.venv/bin/python3`. Do NOT use `python`, `python3`, or any other Python interpreter — the required packages are only installed inside the `.venv` virtual environment. Using any other Python will fail with import errors.

   The `--config` flag tells the script to read team/timezone directly from `~/.openclaw/openclaw.json`. No user values should be interpolated into the command string. This outputs JSON to stdout.

4. **Parse the JSON output** and check `has_data`:
   - If `has_data` is `false` and there's no error: it's off-season or a day off. Reply with `HEARTBEAT_OK` (this suppresses the message in cron/heartbeat mode).
   - If `has_data` is `false` and there's an `error` field: report the error to the user.
   - If `has_data` is `true`: format the report as described below.

5. **Format the report** using this structure (include `game_type` from the JSON when it is not Regular Season):

```
⚾ MLB Daily Report — [Team Name]
📅 [Today's Date]

━━━━━━━━━━━━━━━━━━━━━━━
📊 YESTERDAY'S RECAP [game_type, e.g. "(Spring Training)" — omit if Regular Season]
━━━━━━━━━━━━━━━━━━━━━━━

[Score Line, e.g.: Blue Jays 5, Yankees 3]

  W: [Winning Pitcher]
  L: [Losing Pitcher]
  S: [Save Pitcher, if any]

LINE SCORE:
[Linescore text from the API]

━━━━━━━━━━━━━━━━━━━━━━━
🔮 TODAY'S PREVIEW [game_type, e.g. "(Spring Training)" — omit if Regular Season]
━━━━━━━━━━━━━━━━━━━━━━━

[Opponent] @ [Home Team]
🕐 [Game Time in local timezone]
🏟️ [Venue]

Starting Pitchers:
  [Away Team]: [Pitcher Name] ([W-L], [ERA] ERA)
  [Home Team]: [Pitcher Name] ([W-L], [ERA] ERA)

━━━━━━━━━━━━━━━━━━━━━━━
🏥 INJURY REPORT
━━━━━━━━━━━━━━━━━━━━━━━

[For each injury]:
• [Player Name] ([Position]) — [Injury Description] [Status]

[If no injuries]: ✅ No players currently on the injury list.
```

6. **Omit sections** that have no data:
   - No yesterday game → skip the recap section, note "No game yesterday"
   - No today game → skip the preview section, note "No game scheduled today"
   - No injuries → show the clean bill of health line

7. **Keep the box score concise** — include the linescore (innings R/H/E) but NOT the full box score text (it's too long for chat). Only include the full boxscore if the user explicitly asks for more detail.

8. **Off-season handling** — If neither yesterday nor today has a game **and** there are no injuries to report, respond with just `HEARTBEAT_OK` so no message is delivered. The script covers all game types (spring training, regular season, postseason, exhibition), so true off-season gaps are only mid-November through late February.
