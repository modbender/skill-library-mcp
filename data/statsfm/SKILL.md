---
name: statsfm
description: Music data tool powered by the stats.fm API. Look up album tracklists, artist discographies, and global charts without an account. With a stats.fm username, query personal Spotify listening history, play counts, top artists/tracks/albums, monthly breakdowns, and currently playing.
---

# stats.fm CLI

Comprehensive Python CLI for querying stats.fm API (Spotify listening analytics).

**Requirements:** Python 3.6+ (stdlib only, no pip installs needed)

**Script location:** `scripts/statsfm.py` in this skill's directory. Examples use `./statsfm.py` assuming you're in the scripts folder.

## Prerequisites

**Stats.fm account (optional)**
- A stats.fm account is only needed for personal listening data (history, top tracks, now playing, etc.)
- Without an account, you can still use public features: album tracklists, artist discographies, search, and global charts
- Don't have one? Visit [stats.fm](https://stats.fm) and sign up with Spotify or Apple Music (AM untested, Plus status unknown)
- Already have one? Copy your username from your profile

## Setup

**No account needed** for public commands: `search`, `album`, `artist-albums`, `charts-top-tracks`, `charts-top-artists`, `charts-top-albums`.

For personal stats (`profile`, `top-artists`, `top-tracks`, `recent`, `np`, etc.), pass your username with `--user USERNAME` / `-u USERNAME`. These commands exit with code 1 if no user is provided.

## Quick Start

```bash
# View your profile
./statsfm.py profile

# Top tracks this month
./statsfm.py top-tracks --limit 10

# Track stats for 2025
./statsfm.py track-stats 188745898 --start 2025 --end 2026
```

## All Commands

### User Profile
- `profile` - Show user profile and stats.fm membership info

### Top Lists
- `top-tracks` - Your most played tracks
- `top-artists` - Your most played artists
- `top-albums` - Your most played albums
- `top-genres` - Your top music genres

### Current Activity
- `now-playing` (aliases: `now`, `np`) - Currently playing track
- `recent` - Recently played tracks

### Detailed Stats
- `artist-stats <artist_id>` - Detailed stats for specific artist (with monthly breakdown)
- `track-stats <track_id>` - Detailed stats for specific track (with monthly breakdown)
- `album-stats <album_id>` - Detailed stats for specific album (with monthly breakdown)
- `stream-stats` - Overall streaming statistics

### Lookups
- `album <album_id>` - Album info and full tracklist (release date, label, genres, tracks with duration and [E] tags)
- `artist-albums <artist_id>` - All albums/singles by artist, grouped by type (Albums, Singles & EPs, Compilations), newest first. Deduped by ID, 15 per section by default, shows "(N more)" overflow.
  - `--type album|single|all` (default: all)
  - `--limit N` - Items per section

### Drill-Down
- `top-tracks-from-artist <artist_id>` - Top tracks from specific artist
- `top-tracks-from-album <album_id>` - Top tracks from specific album
- `top-albums-from-artist <artist_id>` - Top albums from specific artist

### Global Charts
- `charts-top-tracks` - Global top tracks chart
- `charts-top-artists` - Global top artists chart
- `charts-top-albums` - Global top albums chart

### Search
- `search <query>` - Search for artists, tracks, or albums

## Common Flags

### Date Ranges
All stats commands support both predefined ranges and custom dates:

**Predefined ranges:**
- `--range today` - Today only
- `--range weeks` - Last 4 weeks (default)
- `--range months` - Last 6 months
- `--range lifetime` - All time

**Custom date ranges:**
- `--start YYYY` - Start year (e.g., `--start 2025`)
- `--start YYYY-MM` - Start month (e.g., `--start 2025-07`)
- `--start YYYY-MM-DD` - Start date (e.g., `--start 2025-07-15`)
- `--end YYYY[-MM[-DD]]` - End date (same formats)

**Examples:**
```bash
# All of 2025
./statsfm.py top-artists --start 2025 --end 2026

# Just July 2025
./statsfm.py top-tracks --start 2025-07 --end 2025-08

# Q1 2025
./statsfm.py artist-stats 39118 --start 2025-01-01 --end 2025-03-31
```

### Other Flags
- `--limit N` / `-l N` - Limit results (default: 15)
- `--user USERNAME` / `-u USERNAME` - Specify the stats.fm username to query
- `--no-album` - Hide album names in track listings (albums show by default)

## Usage Examples

```bash
# Search for an artist, then drill down
./statsfm.py search "madison beer" --type artist
./statsfm.py artist-stats 39118 --start 2025
./statsfm.py top-tracks-from-artist 39118 --limit 20

# Weekly breakdown of a track
./statsfm.py track-stats 188745898 --start 2025 --end 2026 --granularity weekly

# Custom date range
./statsfm.py top-artists --start 2025-06 --end 2025-09

# Album tracklist and discography
./statsfm.py album 1365235
./statsfm.py artist-albums 39118 --type album

# Global charts
./statsfm.py charts-top-tracks --limit 20
```

## Output Features

### Automatic Monthly Breakdowns
Stats commands (`artist-stats`, `track-stats`, `album-stats`) automatically show:
- Total plays and listening time
- Monthly breakdown with plays and time per month
- Works for both predefined ranges and custom date ranges

Example output:
```
Total: 505 plays  (29h 53m)

Monthly breakdown:
  2025-02:   67 plays  (3h 52m)
  2025-03:  106 plays  (6h 21m)
  2025-04:   40 plays  (2h 24m)
  ...
```

### Display Information
- **Track listings:** Show position, track name, artist, album (by default), play count, time
- **Album listings:** Show position, album name, artist, play count, time
- **Artist listings:** Show position, artist name, play count, time, genres
- **Charts:** Show global rankings with stream counts
- **Recent streams:** Show timestamp, track, artist, album (by default)

## Plus vs Free Users

**Stats.fm Plus required for:**
- Stream counts in top lists
- Listening time (play duration)
- Detailed statistics

**Free users get:**
- Rankings/positions
- Track/artist/album names
- Currently playing
- Search functionality
- Monthly breakdowns (via per-day stats endpoint)

The script handles both gracefully, showing `[Plus required]` for missing data.

## API Information

**Base URL:** `https://api.stats.fm/api/v1`

**Authentication:** None needed for public profiles

**Response format:** JSON with `item` (single) or `items` (list) wrapper

**Rate limiting:** Be reasonable with requests. Avoid more than ~10 calls in rapid succession during deep dives.

## Error Handling

All errors print to **stderr** and exit with **code 1**.

| Scenario | stderr output | What to do |
|----------|--------------|------------|
| No user set | `Error: No user specified.` | Pass `--user USERNAME` flag |
| API error (4xx/5xx) | `API Error (code): message` | Check if user exists, profile is public, or ID is valid |
| Connection failure | `Connection Error: reason` | Retry after a moment, check network |
| Empty results | No error, just no output | User may be private, or no data for that period — try `--range lifetime` |
| Plus-only data | Shows `[Plus required]` inline | Acknowledge gracefully, show what's available |

## Finding IDs

Use search to find artist/track/album IDs:

```bash
# Find artist
./statsfm.py search "sabrina carpenter" --type artist
# Returns: [22369] Sabrina Carpenter [pop]

# Find track
./statsfm.py search "espresso" --type track
# Returns: [188745898] Espresso by Sabrina Carpenter

# Find album
./statsfm.py search "short n sweet" --type album
# Returns: [56735245] Short n' Sweet by Sabrina Carpenter
```

Then use the ID numbers in other commands.

## Tips

1. **Use custom dates for analysis:** `--start 2025 --end 2026` to see full year stats
2. **Chain discoveries:** Search → Get ID → Detailed stats → Drill down
3. **Compare periods:** Run same command with different date ranges
4. **Export data:** Pipe output to file for records: `./statsfm.py top-tracks --start 2025 > 2025_top_tracks.txt`
5. **Albums show by default:** Match the stats.fm UI behavior (album art is prominent)
6. **Monthly breakdowns:** All stats commands show month-by-month progression automatically

## For AI Agents

### Setup

Check your memory for a stored stats.fm username. If you don't have one, ask. Every command that touches user data needs `--user USERNAME`.

### What This Tool Is For

This gives you direct access to someone's music listening history. That's personal. The value isn't in dumping tables of data — it's in showing someone something about themselves they didn't already know.

When someone asks about their music, they're not asking for a database query. They want to understand their own taste, revisit a memory, or discover a pattern. Your job is to connect the data to something meaningful.

### How to Think About It

**Someone mentions an artist:** They have a relationship with that artist. Find out what it looks like — how long they've been listening, what era they discovered them, which tracks stuck. `search` → `artist-stats` tells the story. `top-tracks-from-artist` shows what resonated. `artist-albums` gives context on the discography. Don't just list all three — read the first result and decide what's interesting before going deeper.

**Someone asks about their taste:** They want a mirror, not a spreadsheet. `top-artists` and `top-genres` across different time ranges reveal how their taste is shifting. Compare `--range weeks` to `--range months` to `--range lifetime` — the differences are the story. A lifetime #1 that's not in the top 20 this month is more interesting than the current #1.

**Someone mentions an album:** They want to know about it or remember it. `album` gives the tracklist and metadata. If they also have listening data, `album-stats` shows when and how much they played it. Monthly breakdowns reveal whether it was a one-week obsession or a slow burn.

**Someone asks what they're listening to:** `now-playing` is the literal answer. But `recent` with the last 10-15 tracks shows the session's mood. If there's a pattern (same artist, same genre), name it.

### Date Ranges

When the user says a time period, translate it:
- "This year" → `--start 2025 --end 2026`
- "Last summer" → `--start 2025-06 --end 2025-09`
- "When did I start listening to X" → `artist-stats <id>` with `--range lifetime` — the monthly breakdown shows the first month

### Reading the Data

The numbers tell stories. Look for these:

- **A month with 200+ plays** — that artist owned their life for a while. Say so.
- **First appearance in monthly breakdown** — that's when they discovered the artist. Context: was an album released that month?
- **Sudden drop after months of plays** — something changed. New obsession displaced it, or they moved on.
- **Old tracks in recent plays** — nostalgia trip or rediscovery. Worth noting.
- **One track with 5x the plays of the next** — that's their song. The one they put on repeat.

Don't just report numbers. "You played 847 tracks" means nothing. "You listened to Madison Beer for 30 hours in March — that's almost an hour a day" means something.

### Command Reference

| Intent | Command | Key flags |
|--------|---------|-----------|
| Play count for a track | `track-stats <id>` | `--start/--end`, `--granularity` |
| Play count for an artist | `artist-stats <id>` | `--start/--end`, `--granularity` |
| Rankings | `top-tracks`, `top-artists`, `top-albums`, `top-genres` | `--range`, `--start/--end`, `--limit` |
| Currently playing | `now-playing` | | 
| Recent tracks | `recent` | `--limit` |
| Artist's discography | `artist-albums <id>` | `--limit` |
| Album tracklist | `album <id>` | |
| Top tracks by artist | `top-tracks-from-artist <id>` | `--range`, `--limit` |
| Top tracks on album | `top-tracks-from-album <id>` | `--range`, `--limit` |
| Top albums by artist | `top-albums-from-artist <id>` | `--range`, `--limit` |
| Global charts | `charts-top-tracks`, `charts-top-artists`, `charts-top-albums` | `--range`, `--limit` |
| Find IDs | `search <query>` | `--type artist\|track\|album` |
| Overall stats | `stream-stats` | `--range`, `--start/--end` |

### Edge Cases

- **Free users:** Play counts are not available for top tracks — rankings and breakdowns still work, lead with those
- **Empty results:** Try `--range lifetime` as fallback. Could also be a private profile.
- **Search duplicates:** Use the first result
- **Apple Music:** Untested, may have gaps


## References
- Github Repo: [statsfm/statsfm-cli](https://github.com/Beat-YT/statsfm-cli)
- API Endpoints: [references/api.md](references/api.md)
- Official JS Client: [statsfm/statsfm.js](https://github.com/statsfm/statsfm.js)
