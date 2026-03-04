# timemap - search Tel Aviv & Haifa's entertainment venue history

![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Agent Skills](https://img.shields.io/badge/Agent%20Skills-compatible-purple)

> **[Agent Skills](https://agentskills.io) format** - works with OpenClaw, Claude, Cursor, Codex, and other compatible clients

Search historical bars, cafes, clubs, cinemas, and food venues in Tel Aviv-Yafo and Haifa. Data from [timemap.co.il](https://timemap.co.il), a non-profit community project by [Reut Miryam Cohen](https://x.com/reutc) and Amir Ozer.

## Why this exists

[timemap.co.il](https://timemap.co.il) is a community project preserving the history of entertainment and culture venues in Tel Aviv-Yafo and Haifa - bars, clubs, cafes, cinemas, restaurants, performance spaces. As the creators put it: "much of this information was not easily available on the internet until now, a fact we find incomprehensible." This skill makes that database searchable from the terminal or through an AI assistant, so you can ask what was at a specific address, browse what the nightlife scene looked like in a given year, or explore the cultural history of a neighborhood.

## Installation

```bash
npx skills add alexpolonsky/agent-skill-timemap
```

<details>
<summary>Manual install</summary>

**OpenClaw / Claude / Cursor**

Clone or copy the `timemap` folder into your skills directory:
- OpenClaw: `~/clawd/skills/timemap/`
- Claude: `~/.claude/skills/timemap/`
- Cursor: `.cursor/skills/timemap/`

**Standalone CLI**

```bash
python3 scripts/timemap.py stats
```

**CLI shortcut** (optional)

```bash
ln -sf /path/to/timemap/timemap /usr/local/bin/timemap
timemap stats
```

Requirements: Python 3.9+ (stdlib only, no pip install needed)
</details>

## Try it

Ask your AI assistant:
> "What venues were active on Rothschild in 2008?"

Or use the CLI directly:
```bash
timemap search "רוטשילד"
timemap timeline 2005
timemap stats
```

## What you can ask

- "What bars were on Rothschild in 2010?"
- "What was at Dizengoff 99?"
- "Show me the nightlife scene in Florentin in 2005"
- "What cinemas existed in Haifa?"
- "Find LGBTQ venues in Tel Aviv"
- "What venues are near Allenby and King George?"
- "Tell me about Barby - all its locations over the years"
- "What food spots opened in the 90s?"

## Commands

| Command | Description |
|---------|-------------|
| `search <query>` | Search venues by name or address (Hebrew or English) |
| `filter` | Filter by --city, --tags, --year, --active-in, --opened, --closed |
| `venue <id>` | Full details for a specific venue (by ID or name) |
| `timeline <year>` | All venues that were active in a given year |
| `nearby <lat> <lng>` | Find venues near coordinates (--radius in km, default 0.5) |
| `tags [tag]` | List all tags, or show venues with a specific tag |
| `cities` | List cities with venue counts |
| `stats` | Database statistics (venues by city, tag, decade, status) |
| `memories <id>` | User memories for a specific venue |
| `random` | Pick a random venue (prefers ones with memories/photos) |

<details>
<summary>Options and tags reference</summary>

**Options**

| Option | Commands | Description |
|--------|----------|-------------|
| `--json` | all | JSON output for programmatic use |
| `--limit N` | search, filter, timeline, nearby, tags | Max results (default: 25 for terminal, unlimited for --json) |
| `--no-color` | all | Disable colored output (auto-detected for non-TTY, respects `NO_COLOR` env) |
| `--fresh` | all | Bypass cache and fetch fresh data from API |
| `--city` | filter | City code: tlv, haifa |
| `--tags` | filter | Tag (substring match) |
| `--year` | filter | Opened or closed in this year |
| `--active-in` | filter | Active in this year |
| `--opened` | filter | Opened in this year |
| `--closed` | filter | Closed in this year |
| `--radius` | nearby | Radius in km (default: 0.5) |

**Tags**

7 main categories (matching the site's UI filters):

| Tag | Description |
|-----|-------------|
| `bar` | Bar/pub |
| `food` | Restaurant/food venue |
| `cafe` | Cafe |
| `club` | Nightclub |
| `cinema` | Cinema/movie theater |
| `live_shows` | Live performances |
| `lgbtq` | LGBTQ venue |

Additional: `dance_bar`, `lounge`, `wine_bar`, `restaurant`

**City codes**

| Code | City |
|------|------|
| `tlv` | Tel Aviv-Yafo |
| `haifa` | Haifa |

</details>

<details>
<summary>Output examples</summary>

**Search output**
```
Found 4 match(es) for 'Barby':

  בארבי / Barby  Tel Aviv  club  2001-2023  closed  id:253
  בארבי / Barby  Tel Aviv  club  1998-2001  closed  id:251
  בארבי / Barby  Tel Aviv  club  2024-present  open  id:1357
  בארבי / Barby  Tel Aviv  live_shows, cafe  1994-1998  closed  id:248
```

**Venue detail**
```
=== בארבי ===
  English name: Barby
  ID: 253
  City: Tel Aviv
  Address: קיבוץ גלויות 52
  Tags: club
  Opened: 2001
  Closed: 2023
  Duration: 22 years
  Google Maps: https://www.google.com/maps?q=32.0512919,34.7698303
  Web: https://timemap.co.il/venue/253
```

**JSON output**
```json
{
  "ok": true,
  "command": "search",
  "query": "Barby",
  "count": 4,
  "venues": [...]
}
```
</details>

## How it works

Reads timemap.co.il's public API (single endpoint, all venues). Caches locally for 24 hours. No authentication needed. Haversine formula for distance calculations.

## Limitations

- Tel Aviv-Yafo and Haifa only (the two cities in the database)
- Community-curated data - may have gaps or inaccuracies
- Search is substring-based, not geocoded
- Read-only - no write access to the database

Independent open-source tool. Not affiliated with or endorsed by timemap.co.il. Community-curated data provided "as is" without warranty of any kind.

## Author

[Alex Polonsky](https://github.com/alexpolonsky) - [GitHub](https://github.com/alexpolonsky) - [LinkedIn](https://linkedin.com/in/alexpolonsky)

---

Part of [Agent Skills](https://github.com/alexpolonsky/agent-skills) - [Specification](https://agentskills.io/specification)
