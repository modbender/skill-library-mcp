# Media Management

Media request and library management services commonly run alongside TrueNAS.

## Environment Variables

```
OVERSEERR_URL, OVERSEERR_API_KEY     — Media request UI (primary interface)
SONARR_URL, SONARR_API_KEY           — TV show management
RADARR_URL, RADARR_API_KEY           — Movie management
PROWLARR_URL, PROWLARR_API_KEY       — Indexer management
PLEX_URL                             — Media server (typically no auth on LAN)
TAUTULLI_URL, TAUTULLI_API_KEY       — Plex analytics
```

## Overseerr (Media Requests) — PRIMARY INTERFACE

Route all media requests through Overseerr first, not directly to Radarr/Sonarr.
This keeps everything in sync and tracks request history.

### Search

```bash
curl -s "$OVERSEERR_URL/api/v1/search?query=QUERY" -H "X-Api-Key: $OVERSEERR_API_KEY"
```

### Get Details

```bash
# Movie (by TMDB ID)
curl -s "$OVERSEERR_URL/api/v1/movie/TMDB_ID" -H "X-Api-Key: $OVERSEERR_API_KEY"

# TV show (by TMDB ID)
curl -s "$OVERSEERR_URL/api/v1/tv/TMDB_ID" -H "X-Api-Key: $OVERSEERR_API_KEY"
```

### Submit Request

```bash
curl -X POST "$OVERSEERR_URL/api/v1/request" -H "X-Api-Key: $OVERSEERR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"mediaType":"movie","mediaId":TMDB_ID,"rootFolder":"/data/media/movies"}'
```

### Request Body Schema

```json
{
  "mediaType": "movie" | "tv",
  "mediaId": 12345,           // TMDB ID (required)
  "tvdbId": 67890,            // For TV shows (optional, helps matching)
  "seasons": [1, 2] | "all",  // For TV shows
  "is4k": false,
  "serverId": 0,              // 0 = default server
  "profileId": 7,             // Quality profile ID — check your Radarr/Sonarr profiles
  "rootFolder": "/data/media/movies",  // Override destination folder
  "languageProfileId": 1,
  "tags": []
}
```

**Note:** `profileId` and `rootFolder` are user-configurable. Check your Radarr/Sonarr
quality profiles and root folder paths — they vary per setup.

### Folder Routing (Customizable)

You can organize media into genre-based folders. Configure root folders in Radarr/Sonarr,
then set the `rootFolder` in Overseerr requests accordingly.

Example folder structure (customize to your setup):

| Content Type | Example Path | When to Use |
|--------------|-------------|-------------|
| General movies | `/data/media/movies` | Default |
| Documentaries | `/data/media/documentaries` | Documentary genre |
| Kids content | `/data/media/kids` | Kids-rated content |
| Regional content | `/data/media/regional` | Non-English language films |

The routing logic is up to you — determine the right folder based on language, genre,
or content rating from the search results.

### Manage Requests

```bash
# Pending requests
curl -s "$OVERSEERR_URL/api/v1/request?take=20&filter=pending" -H "X-Api-Key: $OVERSEERR_API_KEY"

# Approve request
curl -X POST "$OVERSEERR_URL/api/v1/request/ID/approve" -H "X-Api-Key: $OVERSEERR_API_KEY"

# Request count summary
curl -s "$OVERSEERR_URL/api/v1/request/count" -H "X-Api-Key: $OVERSEERR_API_KEY"
```

## Sonarr (TV Shows)

```bash
# List series
curl -s "$SONARR_URL/api/v3/series" -H "X-Api-Key: $SONARR_API_KEY"

# Search for show
curl -s "$SONARR_URL/api/v3/series/lookup?term=QUERY" -H "X-Api-Key: $SONARR_API_KEY"

# Queue (downloading)
curl -s "$SONARR_URL/api/v3/queue" -H "X-Api-Key: $SONARR_API_KEY"

# Calendar (upcoming episodes)
curl -s "$SONARR_URL/api/v3/calendar?start=DATE&end=DATE" -H "X-Api-Key: $SONARR_API_KEY"

# Add series directly (fallback if Overseerr unavailable)
curl -X POST "$SONARR_URL/api/v3/series" -H "X-Api-Key: $SONARR_API_KEY" \
  -H "Content-Type: application/json" -d '{...series object from lookup...}'
```

## Radarr (Movies)

```bash
# List movies
curl -s "$RADARR_URL/api/v3/movie" -H "X-Api-Key: $RADARR_API_KEY"

# Search for movie
curl -s "$RADARR_URL/api/v3/movie/lookup?term=QUERY" -H "X-Api-Key: $RADARR_API_KEY"

# Queue (downloading)
curl -s "$RADARR_URL/api/v3/queue" -H "X-Api-Key: $RADARR_API_KEY"

# Add movie directly (fallback if Overseerr unavailable)
curl -X POST "$RADARR_URL/api/v3/movie" -H "X-Api-Key: $RADARR_API_KEY" \
  -H "Content-Type: application/json" -d '{...movie object from lookup...}'
```

## Prowlarr (Indexers)

```bash
# List indexers
curl -s "$PROWLARR_URL/api/v1/indexer" -H "X-Api-Key: $PROWLARR_API_KEY"

# Search all indexers
curl -s "$PROWLARR_URL/api/v1/search?query=QUERY&type=search" -H "X-Api-Key: $PROWLARR_API_KEY"

# Indexer performance stats
curl -s "$PROWLARR_URL/api/v1/indexerstats" -H "X-Api-Key: $PROWLARR_API_KEY"
```

## Plex

```bash
# Libraries
curl -s "$PLEX_URL/library/sections" -H "Accept: application/json"

# Active sessions (who's watching)
curl -s "$PLEX_URL/status/sessions" -H "Accept: application/json"

# Recently added
curl -s "$PLEX_URL/library/recentlyAdded" -H "Accept: application/json"

# Trigger library scan
curl -X GET "$PLEX_URL/library/sections/SECTION_ID/refresh"
```

## Tautulli (Plex Analytics)

```bash
# Current activity
curl -s "$TAUTULLI_URL/api/v2?apikey=$TAUTULLI_API_KEY&cmd=get_activity"

# Watch history
curl -s "$TAUTULLI_URL/api/v2?apikey=$TAUTULLI_API_KEY&cmd=get_history&length=20"

# User stats
curl -s "$TAUTULLI_URL/api/v2?apikey=$TAUTULLI_API_KEY&cmd=get_users"

# Most watched movies (last 30 days)
curl -s "$TAUTULLI_URL/api/v2?apikey=$TAUTULLI_API_KEY&cmd=get_most_watched_movies&time_range=30"

# Monthly play trends
curl -s "$TAUTULLI_URL/api/v2?apikey=$TAUTULLI_API_KEY&cmd=get_plays_per_month"
```

## Common Agent Tasks

### "Add a movie"

1. Search Overseerr: `search?query=TITLE`
2. Get TMDB ID from results
3. Determine root folder based on content type (language, genre, rating)
4. Submit request with appropriate `rootFolder` and `profileId`

### "Add a TV show"

Same flow as movies, but set `mediaType: "tv"` and `seasons: "all"` (or specific seasons).

### "Who's watching?"

Use Tautulli's `get_activity` command for real-time Plex session info.

### "What's coming up?"

Use Sonarr's calendar endpoint with today's date and a future range.

### "What's in the queue?"

Check both Sonarr and Radarr queues for active downloads.
