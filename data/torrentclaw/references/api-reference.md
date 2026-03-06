# TorrentClaw API Reference

## Search Response Schema

```json
{
  "total": 42,
  "page": 1,
  "pageSize": 20,
  "results": [
    {
      "id": 1,
      "imdbId": "tt1375666",
      "tmdbId": "27205",
      "contentType": "movie",
      "title": "Inception",
      "titleOriginal": "Inception",
      "year": 2010,
      "overview": "A thief who steals corporate secrets...",
      "posterUrl": "https://image.tmdb.org/t/p/w500/oYuLEt3zVCKq57qu2F8dT7NIa6f.jpg",
      "genres": ["Action", "Science Fiction", "Adventure"],
      "ratingImdb": "8.8",
      "ratingTmdb": "8.4",
      "contentUrl": "/movies/inception-2010-1",
      "hasTorrents": true,
      "maxSeeders": 847,
      "torrents": [
        {
          "infoHash": "aaf1e71c0a0e3b1c0f1a2b3c4d5e6f7a8b9c0d1e",
          "magnetUrl": "magnet:?xt=urn:btih:aaf1e71c...&dn=Inception+2010+1080p&tr=udp://tracker.opentrackr.org:1337/announce&tr=...",
          "torrentUrl": "/api/v1/torrent/aaf1e71c0a0e3b1c0f1a2b3c4d5e6f7a8b9c0d1e",
          "quality": "1080p",
          "codec": "x265",
          "sourceType": "BluRay",
          "sizeBytes": "2147483648",
          "seeders": 847,
          "leechers": 23,
          "source": "yts",
          "qualityScore": 85,
          "scrapedAt": "2026-02-13T10:30:00Z",
          "uploadedAt": "2024-03-15T12:00:00Z",
          "languages": ["en"],
          "audioCodec": "AAC",
          "hdrType": null,
          "releaseGroup": "YTS",
          "isProper": false,
          "isRepack": false,
          "isRemastered": false,
          "season": null,
          "episode": null
        }
      ]
    }
  ]
}
```

## Allowed Genres

Action, Adventure, Animation, Comedy, Crime, Documentary, Drama, Family, Fantasy, History, Horror, Music, Mystery, Romance, Science Fiction, Thriller, War, Western, Reality, Talk, News, Soap, Kids, TV Movie, Action & Adventure, Sci-Fi & Fantasy, War & Politics

## API Key Authentication

**Request Headers:**
```
Authorization: Bearer tc_live_xxxxx
```

Or via query parameter:
```
?api_key=tc_live_xxxxx
```

**Response Headers:**
```
X-RateLimit-Tier: free
X-RateLimit-Remaining: 115
X-Api-Key-Id: tc_live_abc1
```

**Rate Limit Tiers:**
- **Anonymous**: 30 req/min (no key)
- **Free**: 120 req/min, 1,000 req/day (with API key)
- **Pro**: 1,000 req/min, 10,000 req/day (with API key)
- **Internal**: Unlimited (with API key)

## Search Query Parameters

**Season & Episode Filtering:**
- `season=1` — Filter by TV show season number
- `episode=5` — Filter by episode number
- Note: Also supports parsing from query text (e.g., `q=breaking+bad+S01E05`)

**Audio & Video Quality:**
- `audio=atmos` — Filter by audio codec (aac, flac, opus, atmos)
- `hdr=dolby_vision` — Filter by HDR format (hdr10, dolby_vision, hdr10plus, hlg)
- `quality=2160p` — Filter by resolution (480p, 720p, 1080p, 2160p)

**Localization:**
- `locale=es` — Get titles in Spanish (also: fr, de, pt, it, ja, ko, zh, ru, ar)

## Response Fields

**Content fields:**
- `hasTorrents` (boolean) — Whether content has associated torrents
- `maxSeeders` (number) — Highest seeder count across all torrents for this content
- `backdropUrl` (string) — TMDB backdrop image URL
- `contentUrl` (string) — Relative URL for content detail page

**Torrent fields:**
- `scrapedAt` (string, ISO 8601) — Timestamp of last tracker scrape for real-time seeder/leecher counts
- `uploadedAt` (string, ISO 8601) — When the torrent was first uploaded
- `releaseGroup` (string) — Release group name (e.g., "YTS", "RARBG")
- `isProper` (boolean) — Whether this is a PROPER release (fix for previous release issues)
- `isRepack` (boolean) — Whether this is a REPACK (re-packaged due to issues)
- `isRemastered` (boolean) — Whether this is a remastered release

## Credits Response Schema

```json
{
  "contentId": 1,
  "director": "Christopher Nolan",
  "cast": [
    {
      "name": "Leonardo DiCaprio",
      "character": "Cobb",
      "profileUrl": "https://image.tmdb.org/t/p/w185/..."
    }
  ]
}
```

Returns `contentId`, director name, and up to 10 cast members. Param: `id` (path, required)

## Track Request Schema

```json
{
  "infoHash": "aaf1e71c0a0e3b1c0f1a2b3c4d5e6f7a8b9c0d1e",
  "action": "magnet"
}
```

Method: **POST**. Actions: `magnet`, `torrent_download`, `copy`. Response: `{"ok": true}`

## Search Analytics Response Schema

```json
{
  "period": { "days": 7, "since": "2026-02-06T00:00:00Z" },
  "summary": { "totalSearches": 15420, "uniqueQueries": 8730, "avgResults": 12.3, "zeroResultSearches": 120, "webSearches": 10000, "apiSearches": 5420 },
  "topQueries": [{ "query": "dune", "count": 342, "avgResults": 15.2 }],
  "zeroResultQueries": [{ "query": "obscure title", "count": 5 }],
  "dailyVolume": [{ "date": "2026-02-13", "total": 2200, "web": 1500, "api": 700 }]
}
```

Params: `days` (1-90, default 7), `limit` (1-100, default 20). **Requires pro tier API key.**

## Error Responses

| Status | Meaning |
|--------|---------|
| 400 | Invalid parameters (missing q, bad genre, etc.) |
| 404 | Torrent file not found (torrent endpoint only) |
| 429 | Rate limited |
| 500 | Internal server error |

## Rate Limits

| Endpoint | Limit |
|----------|-------|
| /api/v1/search | 30/min |
| /api/v1/autocomplete | 60/min |
| /api/v1/popular | 30/min |
| /api/v1/recent | 30/min |
| /api/v1/content/{id}/credits | 30/min |
| /api/v1/stats | 10/min |
| /api/v1/torrent | 20/min |
| /api/v1/track | 60/min |
| /api/v1/search-analytics | 10/min |

## Torrent Download Integration

### Using magnetUrl with Transmission

```bash
# Search and add best torrent to Transmission
RESULT=$(curl -s -H "x-search-source: skill" "https://torrentclaw.com/api/v1/search?q=inception&type=movie&sort=seeders&limit=1")
MAGNET=$(echo "$RESULT" | jq -r '.results[0].torrents[0].magnetUrl')
transmission-remote -a "$MAGNET"
```

### Using magnetUrl with aria2

```bash
RESULT=$(curl -s -H "x-search-source: skill" "https://torrentclaw.com/api/v1/search?q=inception&sort=seeders&limit=1")
MAGNET=$(echo "$RESULT" | jq -r '.results[0].torrents[0].magnetUrl')
aria2c "$MAGNET" --dir=~/Downloads
```

### Downloading .torrent files

```bash
# Get info hash from search result
INFO_HASH=$(echo "$RESULT" | jq -r '.results[0].torrents[0].infoHash')

# Download .torrent file
curl -o "movie.torrent" "https://torrentclaw.com/api/v1/torrent/$INFO_HASH"

# The file includes a descriptive filename in Content-Disposition header:
# TorrentClaw.com-Inception-1080p-EN.torrent
```

## Data Sources

| Source | Content | Notes |
|--------|---------|-------|
| YTS | Movies | High quality, IMDb IDs |
| EZTV | TV Shows | Episode torrents, IMDb IDs |
| Knaben | Mixed | Meta-search aggregator |
| Prowlarr | Mixed | Indexer aggregator |
| Bitmagnet | Mixed | DHT discovery |
| Torrentio | Mixed | Stremio ecosystem |
| DonTorrent | Mixed | Spanish content |
| Torrents.csv | Mixed | Open dataset |
| TMDB | Metadata | Posters, genres, translations |
