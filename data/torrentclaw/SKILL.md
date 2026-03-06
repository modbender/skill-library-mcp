---
name: torrentclaw
description: Search and download torrents via TorrentClaw. Use when the user asks to find, search, or download movies, TV shows, or torrents. Detects local torrent clients (Transmission, aria2) and adds magnets directly, or offers magnet link copy and .torrent file download. Supports filtering by type (movie/show), genre, year, quality (480p-2160p), rating, language, and season/episode (S01E05, 1x05). Features API key authentication with tiered rate limits, AI-verified matching, and quality scoring (0-100). Returns titles with posters, ratings, and torrents with magnet links and quality scores.
license: MIT
metadata: {"version": "0.1.17", "repository": "https://github.com/torrentclaw/torrentclaw-skill", "homepage": "https://torrentclaw.com", "openclaw": {"emoji": "🎬", "os": ["darwin", "linux", "win32"], "requires": {"bins": ["curl", "bash", "jq"], "env": ["TORRENTCLAW_API_KEY"]}, "primaryEnv": "TORRENTCLAW_API_KEY"}, "tags": ["torrent", "movies", "tv-shows", "download", "media", "entertainment", "magnet", "transmission", "aria2", "search", "4k", "hdr"]}
---

# TorrentClaw

Search movies and TV shows across multiple torrent sources with TMDB metadata enrichment. Detect local torrent clients and start downloads automatically.

## Base URL

```
https://torrentclaw.com
```

## Workflow

Follow these steps when the user asks to find or download a torrent:

### Step 1: Detect torrent clients

Run the detection script to check what's available on the user's system:

```bash
bash "$(dirname "$0")/scripts/detect-client.sh"
```

The script outputs JSON with detected clients and OS info. Remember the result for Step 4.

### Step 2: Search for content

Query the TorrentClaw API. Always include the `x-search-source: skill` header for analytics. The API key is **optional** — anonymous usage allows 30 req/min, which is enough for casual searches. Only include the `Authorization` header if `$TORRENTCLAW_API_KEY` is set.

**Important:** Always use `--data-urlencode` for user-supplied values to prevent shell injection. Never interpolate user input directly into the URL string.

```bash
curl -s -G -H "x-search-source: skill" \
  --data-urlencode "q=QUERY" \
  -d "sort=seeders" -d "limit=5" \
  "https://torrentclaw.com/api/v1/search"
```

If the user has configured an API key for higher rate limits:

```bash
curl -s -G -H "x-search-source: skill" -H "Authorization: Bearer $TORRENTCLAW_API_KEY" \
  --data-urlencode "q=QUERY" \
  -d "sort=seeders" -d "limit=5" \
  "https://torrentclaw.com/api/v1/search"
```

**Useful filters** (append as query params):
- `type=movie` or `type=show`
- `quality=1080p` (also: 720p, 2160p, 480p)
- `genre=Action` (see references/api-reference.md for full list)
- `year_min=2020&year_max=2025`
- `min_rating=7`
- `lang=es` (ISO 639 language code)
- `audio=atmos` (also: aac, flac, opus)
- `hdr=dolby_vision` (also: hdr10, hdr10plus, hlg)
- `season=1` — Filter by TV show season
- `episode=5` — Filter by episode number
- `locale=es` — Get titles in Spanish (also: fr, de, pt, it, ja, ko, zh, ru, ar)
- `sort=seeders` (also: relevance, year, rating, added)

### Step 3: Present results

Display results in a clear table format. For each content item show:
- Title, year, content type
- IMDb rating (or TMDB rating as fallback)
- For each torrent: quality, codec, size (human-readable), seeders

Example format:
```
1. Inception (2010) - Movie - IMDb: 8.8
   a) 1080p BluRay x265 - 2.1 GB - 847 seeders
   b) 2160p WEB-DL x265 HDR - 8.3 GB - 234 seeders
   c) 720p BluRay x264 - 1.0 GB - 156 seeders
```

Ask the user which torrent they want.

### Step 4: Handle download

Based on the detection from Step 1:

**If a torrent client was detected:**
Offer to add the magnet link directly:

```bash
bash "$(dirname "$0")/scripts/add-torrent.sh" "MAGNET_URL"
```

Or with a specific client and download directory:

```bash
bash "$(dirname "$0")/scripts/add-torrent.sh" "MAGNET_URL" --client transmission --download-dir ~/Downloads
```

**If NO torrent client was detected:**
Offer these options:
1. **Copy magnet link** — Give the user the full `magnetUrl` from the API response to copy
2. **Download .torrent file** — `curl -o "filename.torrent" "https://torrentclaw.com/api/v1/torrent/INFO_HASH"`
3. **Install a client** — Run the install guide script:

```bash
bash "$(dirname "$0")/scripts/install-guide.sh" transmission
```

Recommend **Transmission** for Linux/macOS (lightweight daemon, simple CLI) and **aria2** as alternative (multi-protocol, no daemon needed).

## Endpoints

### Search — `GET /api/v1/search`

Main search endpoint. Required: `q` (query string).

**Filters:** `type` (movie/show), `genre`, `year_min`, `year_max`, `min_rating` (0-10), `quality` (480p/720p/1080p/2160p), `lang` (ISO 639), `audio` (aac/flac/opus/atmos), `hdr` (hdr10/dolby_vision/hdr10plus/hlg).

**Sorting:** `sort` = relevance | seeders | year | rating | added

**Pagination:** `page` (1-1000), `limit` (1-50, default 20)

**Response:** `{ total, page, pageSize, results: [{ id, imdbId, tmdbId, contentType, title, year, overview, posterUrl, backdropUrl, genres, ratingImdb, ratingTmdb, contentUrl, hasTorrents, maxSeeders, torrents: [{ infoHash, magnetUrl, torrentUrl, quality, codec, sourceType, sizeBytes, seeders, leechers, source, qualityScore, scrapedAt, uploadedAt, languages, audioCodec, hdrType, releaseGroup, isProper, isRepack, isRemastered, season, episode }] }] }`

**New fields:**
- `hasTorrents` (boolean) — Whether content has any associated torrents
- `maxSeeders` (number) — Highest seeder count across all torrents for this content
- `scrapedAt` (string) — ISO timestamp of last tracker scrape for real-time seeder/leecher counts

### Autocomplete — `GET /api/v1/autocomplete`

Fast typeahead. Param: `q` (min 2 chars). Returns max 8 suggestions.

### Popular — `GET /api/v1/popular`

Trending content by seeders. Params: `limit` (1-24, default 12), `page`.

### Recent — `GET /api/v1/recent`

Recently added content. Params: `limit` (1-24, default 12), `page`.

### Torrent File — `GET /api/v1/torrent/{infoHash}`

Download .torrent file by 40-char hex info hash. Returns binary `application/x-bittorrent`.

### Stats — `GET /api/v1/stats`

Content/torrent counts and recent ingestion history. No params.

### Credits — `GET /api/v1/content/{id}/credits`

Director and top 10 cast members with character names.

**Params:** `id` (path, required — content ID from search)

**Response:** `{ contentId, director: "name", cast: [{ name, character, profileUrl }] }`

**Usage:** Show cast info when the user asks "who's in this movie?" or wants details about a search result.

### Track — `POST /api/v1/track`

Record user interactions for popularity ranking. Call this after the user selects a torrent.

**Request body (JSON):**
```json
{"infoHash": "40-char hex", "action": "magnet|torrent_download|copy"}
```

**Response:** `{"ok": true}`

### Search Analytics — `GET /api/v1/search-analytics`

Search volume, top queries, and zero-result queries by period. **Requires API key with pro tier.**

**Params:** `days` (1-90, default 7), `limit` (1-100, default 20)

**Response:** `{ period, summary, topQueries, zeroResultQueries, dailyVolume }`

## Season & Episode Search

TorrentClaw supports smart episode filtering with multiple formats:

**Supported formats:**
- `S01E05` (standard format)
- `1x05` (alternative format)
- `1x05-1x08` (episode ranges)
- `Season 1 Episode 5` (natural language)

**Usage:**

1. **In query text** (automatic parsing):
```bash
curl -s -G --data-urlencode "q=breaking bad S05E14" \
  "https://torrentclaw.com/api/v1/search"
```

2. **With explicit parameters**:
```bash
curl -s -G --data-urlencode "q=breaking bad" \
  -d "season=5" -d "episode=14" \
  "https://torrentclaw.com/api/v1/search"
```

The API automatically detects episode patterns in queries and filters results accordingly.

## API Authentication

The API works without authentication (30 req/min anonymous tier). An API key is **only needed** if you require higher rate limits for heavy or automated usage.

**Rate Limit Tiers:**

| Tier | Requests/min | Requests/day | Authentication |
|------|--------------|--------------|----------------|
| Anonymous | 30 | Unlimited | None |
| Free | 120 | 1,000 | API key required |
| Pro | 1,000 | 10,000 | API key required |
| Internal | Unlimited | Unlimited | API key required |

**Using an API key:**

Always use the `$TORRENTCLAW_API_KEY` environment variable via the `Authorization` header. Avoid passing the key as a query parameter — query strings may be logged in server access logs and HTTP referrer headers.

```bash
curl -s -G -H "Authorization: Bearer $TORRENTCLAW_API_KEY" \
  --data-urlencode "q=dune" \
  "https://torrentclaw.com/api/v1/search"
```

**Rate limit headers in response:**
- `X-RateLimit-Tier` - Your current tier (anonymous/free/pro/internal)
- `X-RateLimit-Remaining` - Requests remaining in current window

**Getting an API key:**
Contact via https://torrentclaw.com/contact or https://torrentclaw.com/api/v1/contact

## MCP Server Integration

For users of **Claude Desktop**, **Cursor**, or **Windsurf**, TorrentClaw is also available as an MCP (Model Context Protocol) server:

```bash
npx @torrentclaw/mcp
```

**MCP vs Skill:**
- **Skill (this file)**: For OpenClaw, Claude Code, Cline, Roo Code — natural language interface
- **MCP Server**: For Claude Desktop, Cursor, Windsurf — structured tools interface
- **Both** use the same TorrentClaw API backend

See https://torrentclaw.com/mcp for MCP installation and usage.

## Common Patterns

**Find best quality torrent for a movie:**
Search with `sort=seeders`, pick the torrent with highest `qualityScore`.

**Find 4K content:**
Use `quality=2160p` filter.

**Browse Spanish-language torrents:**
Use `lang=es` filter.

**Search for a specific TV episode:**
```bash
curl -s -G --data-urlencode "q=entrevias S01E05" \
  -d "locale=es" \
  "https://torrentclaw.com/api/v1/search"
```

**Search with API key for higher rate limits:**
```bash
curl -s -G -H "Authorization: Bearer $TORRENTCLAW_API_KEY" \
  --data-urlencode "q=dune" \
  -d "quality=2160p" \
  "https://torrentclaw.com/api/v1/search"
```

**Find popular sci-fi movies:**
```bash
curl -s -G --data-urlencode "genre=Science Fiction" \
  -d "type=movie" -d "sort=seeders" \
  "https://torrentclaw.com/api/v1/search"
```

**Find Dolby Vision / HDR content:**
```bash
curl -s -G --data-urlencode "q=dune" \
  -d "hdr=dolby_vision" -d "quality=2160p" \
  "https://torrentclaw.com/api/v1/search"
```

**Find Atmos audio torrents:**
```bash
curl -s -G --data-urlencode "q=oppenheimer" \
  -d "audio=atmos" \
  "https://torrentclaw.com/api/v1/search"
```

**Get cast info for a movie:**
```bash
curl "https://torrentclaw.com/api/v1/content/42/credits"
```

**Track torrent selection (call after user picks a torrent):**
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"infoHash":"aaf1e71c...","action":"magnet"}' \
  "https://torrentclaw.com/api/v1/track"
```

## Troubleshooting

**Scripts not executable:** Run `chmod +x scripts/*.sh` in the skill directory.

**Transmission not detected but installed:** Ensure `transmission-remote` is in PATH. On some systems the package is `transmission-cli`.

**aria2 starts but exits immediately:** aria2c in direct mode downloads to current directory. Use `--download-dir` flag or `--daemon` mode.

**No torrent client detected:** Run `bash scripts/install-guide.sh transmission` to see installation instructions for your OS (Linux, macOS, Windows/WSL).

**API key not working:**
- Verify the key format: `tc_live_` followed by 32 hex characters
- Check the `Authorization: Bearer <key>` header is correct
- Ensure the key hasn't expired (contact support if needed)
- Check `X-RateLimit-Tier` header in responses to confirm tier

**Rate limits:**
- Anonymous: 30 req/min (no auth)
- Free tier: 120 req/min, 1K/day (with API key)
- Pro tier: 1K req/min, 10K/day (with API key)
- If you get 429, wait a moment or use an API key for higher limits

**Windows users:** Scripts require bash. Use WSL (Windows Subsystem for Linux) or Git Bash.

## Links

- **Website**: https://torrentclaw.com
- **GitHub**: https://github.com/torrentclaw/torrentclaw-skill
- **OpenAPI Spec**: https://torrentclaw.com/api/openapi.json
- **Swagger UI**: https://torrentclaw.com/api/docs
- **MCP Server**: https://torrentclaw.com/mcp
- **llms.txt**: https://torrentclaw.com/llms.txt
