---
name: timemap
version: 1.0.0
description: Search historical entertainment, nightlife, and culture venues in Tel Aviv and Haifa from timemap.co.il. Bars, cafes, clubs, cinemas, food venues, performance spaces. Use for "bars in Tel Aviv history", "what was at this address", "nightlife history", "בילה בתל אביב", "מה היה פה פעם", "מועדונים שנסגרו", "בתי קפה היסטוריים", "בתי קולנוע בחיפה".
author: Alex Polonsky (https://github.com/alexpolonsky)
homepage: https://github.com/alexpolonsky/agent-skill-timemap
license: MIT
metadata: {"openclaw": {"emoji": "🗺️", "os": ["darwin", "linux"], "requires": {"bins": ["python3"]}}}
---

# Timemap - Tel Aviv & Haifa Venue History

Search historical entertainment, nightlife, and culture venues in Tel Aviv-Yafo and Haifa from [timemap.co.il](https://timemap.co.il) - a community-curated database mapping bars, cafes, clubs, cinemas, food venues, and performance spaces throughout the cities' history.

> Data from [timemap.co.il](https://timemap.co.il), a non-profit project by [Reut Miryam Cohen](https://x.com/reutc) and Amir Ozer - "a loving tribute to the places and people that made the cities we grew up in." Venues include opening/closing dates, locations, tags, user memories, and photos. This skill is an unofficial CLI wrapper.

## Quick Start

```bash
# Search for a venue (Hebrew or English)
python3 {baseDir}/scripts/timemap.py search "רוטשילד"
python3 {baseDir}/scripts/timemap.py search "Barby"

# See what was active in a specific year
python3 {baseDir}/scripts/timemap.py timeline 2010

# Get database statistics
python3 {baseDir}/scripts/timemap.py stats
```

## Commands

| Command | Description |
|---------|-------------|
| `search <query>` | Search venues by name or address (Hebrew or English) |
| `filter` | Filter by --city, --tags, --year, --active-in, --opened, --closed |
| `venue <id>` | Get full details for a specific venue (by ID or name) |
| `timeline <year>` | Show all venues that were active in a given year |
| `nearby <lat> <lng>` | Find venues near coordinates (--radius in km, default 0.5) |
| `tags [tag]` | List all tags, or show venues with a specific tag |
| `cities` | List cities with venue counts |
| `stats` | Database statistics (venues by city, tag, decade, status) |
| `memories <id>` | Show user memories for a specific venue |
| `random` | Pick a random venue (prefers ones with memories/photos) |

## Search Examples

```bash
# Search by name (Hebrew or English)
python3 {baseDir}/scripts/timemap.py search "טדי"
python3 {baseDir}/scripts/timemap.py search "Barby"

# Search by address
python3 {baseDir}/scripts/timemap.py search "רוטשילד"
python3 {baseDir}/scripts/timemap.py search "דיזנגוף"

# Get full details for a venue
python3 {baseDir}/scripts/timemap.py venue 192

# Find venues with user memories
python3 {baseDir}/scripts/timemap.py memories 253
```

## Filter Examples

```bash
# Filter by city
python3 {baseDir}/scripts/timemap.py filter --city tlv
python3 {baseDir}/scripts/timemap.py filter --city haifa

# Filter by tag
python3 {baseDir}/scripts/timemap.py filter --tags bar
python3 {baseDir}/scripts/timemap.py filter --tags food
python3 {baseDir}/scripts/timemap.py filter --tags cinema

# Venues that opened in a specific year
python3 {baseDir}/scripts/timemap.py filter --opened 2005

# Venues that closed in a specific year
python3 {baseDir}/scripts/timemap.py filter --closed 2010

# Venues active in a specific year
python3 {baseDir}/scripts/timemap.py filter --active-in 2008

# Combine filters
python3 {baseDir}/scripts/timemap.py filter --city tlv --tags bar --active-in 2010
```

## Timeline & Location Examples

```bash
# See what was happening in a specific year
python3 {baseDir}/scripts/timemap.py timeline 2005
python3 {baseDir}/scripts/timemap.py timeline 1995

# Find venues near coordinates (Rothschild Blvd area)
python3 {baseDir}/scripts/timemap.py nearby 32.0646 34.7731
python3 {baseDir}/scripts/timemap.py nearby 32.0646 34.7731 --radius 1.0

# Find venues near Florentin
python3 {baseDir}/scripts/timemap.py nearby 32.0566 34.7608 --radius 0.5
```

## Browse & Explore

```bash
# List all tags
python3 {baseDir}/scripts/timemap.py tags

# Show venues with a specific tag
python3 {baseDir}/scripts/timemap.py tags bar
python3 {baseDir}/scripts/timemap.py tags club

# List cities
python3 {baseDir}/scripts/timemap.py cities

# Database statistics
python3 {baseDir}/scripts/timemap.py stats

# Random venue (great for discovery)
python3 {baseDir}/scripts/timemap.py random
```

## Options Reference

| Option | Commands | Description |
|--------|----------|-------------|
| `--json` | all | Output in JSON format (agent-friendly) |
| `--limit N` | search, filter, timeline, nearby, tags | Max results (default: 25 for terminal, unlimited for --json) |
| `--no-color` | all | Disable colored output (auto-detected for non-TTY) |
| `--fresh` | all | Bypass cache and fetch fresh data from API |
| `--city` | filter | Filter by city code (tlv, haifa) |
| `--tags` | filter | Filter by tag (substring match) |
| `--year` | filter | Venues that opened or closed in this year |
| `--active-in` | filter | Venues that were active in this year |
| `--opened` | filter | Venues that opened in this year |
| `--closed` | filter | Venues that closed in this year |
| `--radius` | nearby | Search radius in km (default: 0.5) |

## City Codes

| Code | City |
|------|------|
| `tlv` | Tel Aviv |
| `haifa` | Haifa |

## Tags

7 main categories (matching the site's UI filters):

| Tag | Hebrew | Description |
|-----|--------|-------------|
| `bar` | ברים | Bar/pub |
| `food` | אוכל | Restaurant/food venue |
| `cafe` | בתי קפה | Cafe |
| `club` | מועדונים | Nightclub |
| `cinema` | בתי קולנוע | Cinema/movie theater |
| `live_shows` | הופעות | Live performances |
| `lgbtq` | להטב"ק | LGBTQ venue |

Additional tags: `dance_bar`, `lounge`, `wine_bar`, `restaurant`

Use `python3 {baseDir}/scripts/timemap.py tags` to see current counts from live data.

## Workflow Example

```bash
# 1. Explore what Tel Aviv nightlife looked like in 2008
python3 {baseDir}/scripts/timemap.py timeline 2008

# 2. Filter just the bars
python3 {baseDir}/scripts/timemap.py filter --active-in 2008 --tags bar

# 3. Get details on an interesting venue
python3 {baseDir}/scripts/timemap.py venue "Barby"

# 4. Read user memories about it
python3 {baseDir}/scripts/timemap.py memories "Barby"

# 5. Find nearby venues
python3 {baseDir}/scripts/timemap.py nearby 32.0646 34.7731 --radius 0.5
```

## Notes

- **Community-curated**: Historical data maintained by timemap.co.il community
- **No API key needed**: Public API endpoint, no authentication required
- **Bilingual**: Search works with Hebrew and English venue names
- **Caching**: 24-hour local cache (one API call per day max, ~500KB)
- **Coordinates**: Haversine formula for accurate distance calculations
- **Deleted venues filtered**: Venues marked as deleted are automatically excluded
- **Color output**: ANSI colors in terminal (respects `NO_COLOR` env var and `--no-color` flag)
- **User memories**: Many venues have community-submitted memories and photos
- **Year estimates**: Some opening/closing years are marked as estimates

## Agent Usage Patterns

For agent integration, always use `--json` flag for structured output:

```bash
# Search returns array of matching venues
python3 {baseDir}/scripts/timemap.py search "Barby" --json

# Timeline returns venues active in a year
python3 {baseDir}/scripts/timemap.py timeline 2010 --json

# Stats returns comprehensive database metrics
python3 {baseDir}/scripts/timemap.py stats --json
```

All commands support `--json` for machine-readable output with consistent structure:
```json
{
  "ok": true,
  "command": "search",
  "count": 2,
  "venues": [...]
}
```
