---
name: lastfm
description: Access Last.fm user profile, now playing, top tracks/artists/albums by period, loved tracks, and optionally love/unlove tracks.
metadata:
  {
    "openclaw":
      {
        "requires": { "env": ["LASTFM_API_KEY", "LASTFM_USERNAME"], "bins": ["curl", "jq"] },
        "primaryEnv": "LASTFM_API_KEY",
        "emoji": "🎵"
      }
  }
---

# Last.fm Profile Skill

Retrieves Last.fm user listening data including now playing, top tracks/artists/albums by time period, and loved tracks. Optionally supports write operations (love/unlove tracks, scrobble) when `LASTFM_SESSION_KEY` is configured.

## Required Environment Variables

- `LASTFM_API_KEY`: Your Last.fm API key (get one at https://www.last.fm/api/account/create)
- `LASTFM_USERNAME`: Your Last.fm username

## Optional Environment Variables

- `LASTFM_SESSION_KEY`: Required for write operations (love/unlove, scrobble)
- `LASTFM_API_SECRET`: Required to sign write operations (love/unlove, scrobble)

## Workflow

1. Validate required environment variables are present
2. Ensure dependencies (`jq`, `curl`) are available
3. Determine which command the user is requesting
2. Determine which command the user is requesting
3. Construct API request to `ws.audioscrobbler.com/2.0/`
4. Execute HTTP GET request with appropriate method and parameters
5. Parse JSON response and format for user

## Supported Commands

### Read Operations (No Auth Required)

| Command | Description | Example |
|---------|-------------|---------|
| `now-playing`, `np` | Current or most recent track | `/lastfm np` |
| `top-tracks [period]` | Top tracks by period | `/lastfm top-tracks 7day` |
| `top-artists [period]` | Top artists by period | `/lastfm top-artists 1month` |
| `top-albums [period]` | Top albums by period | `/lastfm top-albums overall` |
| `loved` | Loved tracks | `/lastfm loved` |
| `recent [limit]` | Recent tracks (default 10) | `/lastfm recent 20` |
| `profile` | User profile info | `/lastfm profile` |

### Time Periods

- `7day` - Last 7 days
- `1month` - Last 30 days
- `3month` - Last 90 days
- `6month` - Last 180 days
- `12month` - Last year
- `overall` - All time (default if not specified)

### Write Operations (Auth Required)

| Command | Description | Example |
|---------|-------------|---------|
| `love <artist> <track>` | Love a track | `/lastfm love "Radiohead" "Creep"` |
| `unlove <artist> <track>` | Unlove a track | `/lastfm unlove "Radiohead" "Creep"` |

## API Request Construction

Base URL: `https://ws.audioscrobbler.com/2.0/`

Required parameters for all requests:
- `api_key`: Value from `LASTFM_API_KEY`
- `format`: `json`
- `method`: API method name

User-specific requests also require:
- `user`: Value from `LASTFM_USERNAME`

### Method Parameters

| Method | Additional Parameters |
|--------|----------------------|
| `user.getInfo` | `user` |
| `user.getRecentTracks` | `user`, `limit` (optional) |
| `user.getTopTracks` | `user`, `period` (optional) |
| `user.getTopArtists` | `user`, `period` (optional) |
| `user.getTopAlbums` | `user`, `period` (optional) |
| `user.getLovedTracks` | `user` |
| `track.love` | `artist`, `track`, `sk` (session key) |
| `track.unlove` | `artist`, `track`, `sk` (session key) |

## Response Parsing

### Now Playing Response

Extract from `recenttracks.track[0]`:
- If `@attr.nowplaying === "true"`: currently playing
- `artist.#text` - Artist name
- `name` - Track name
- `album.#text` - Album name

### Top Items Response

Extract array from:
- `toptracks.track[]` for top tracks
- `topartists.artist[]` for top artists
- `topalbums.album[]` for top albums

Each item includes:
- `name` - Item name
- `playcount` - Play count
- `artist.name` - Artist (for tracks/albums)
- `@attr.rank` - Position in chart

### Profile Response

Extract from `user`:
- `name` - Username
- `realname` - Real name (if set)
- `playcount` - Total scrobbles
- `country` - Country
- `registered` - Account creation date
- `url` - Profile URL

## Guardrails

- Never log or expose API keys or session keys in output
- Rate limit: respect Last.fm's 5 requests/second limit
- Write operations must fail gracefully if `LASTFM_SESSION_KEY` not set
- All user inputs must be URL-encoded before API calls
- Only connect to `ws.audioscrobbler.com` - no external endpoints
- Handle missing data gracefully (e.g., no now playing, empty loved tracks)
- Validate period parameter is one of: 7day, 1month, 3month, 6month, 12month, overall
- Validate `recent` limit is numeric and within 1–200

## Error Handling

| Error Code | Meaning | Action |
|------------|---------|--------|
| 10 | Invalid API key | Tell user to check `LASTFM_API_KEY` |
| 6 | Invalid parameters | Check required params are present |
| 29 | Rate limit exceeded | Wait and retry, inform user |
| 26 | Suspended API key | Direct user to Last.fm support |
| 4 | Authentication failed | Check session key for write ops |

## Example Output Formats

### Now Playing

```
🎵 Now Playing:
"Track Name" by Artist Name
from Album Name
```

Or if not currently playing:

```
🎵 Last Played:
"Track Name" by Artist Name
Listened: [timestamp]
```

### Top Tracks

```
🎵 Top Tracks (7 days):

1. "Track One" by Artist One (42 plays)
2. "Track Two" by Artist Two (38 plays)
3. "Track Three" by Artist Three (31 plays)
...
```

### Profile

```
🎵 Last.fm Profile: username

📊 15,432 total scrobbles
🌍 United Kingdom
📅 Member since: Nov 2002
🔗 last.fm/user/username
```

## Setup Instructions

1. Get a Last.fm API key at https://www.last.fm/api/account/create
2. Add to `~/.openclaw/openclaw.json`:

```json5
{
  skills: {
    entries: {
      lastfm: {
        enabled: true,
        env: {
          LASTFM_API_KEY: "your_api_key_here",
          LASTFM_USERNAME: "your_username"
        }
      }
    }
  }
}
```

3. For write operations, see `{baseDir}/references/auth-guide.md`
