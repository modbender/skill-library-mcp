---
name: moviepilot
description: "MoviePilot media subscription and management tool. Use when the user wants to: (1) search for movies or TV shows, (2) subscribe/follow movies or TV shows for automatic download, (3) view or manage existing subscriptions, (4) cancel subscriptions, (5) check download status, (6) browse recommendations (Douban/TMDB/Bangumi), or any task involving MoviePilot."
---

# MoviePilot

Interact with MoviePilot API to search, subscribe, and manage movies/TV shows.

## Prerequisites

Required environment variables (must be set before use):
- `MOVIEPILOT_URL` - MoviePilot server URL (e.g., `http://127.0.0.1:3000`)
- `MOVIEPILOT_API_KEY` - API Key for authentication (preferred)
- Or `MOVIEPILOT_TOKEN` - Bearer token (obtained via login)

If credentials are not set, ask the user to provide them.

## Core Workflows

### 1. Subscribe to a Movie/TV Show

Typical user request: "帮我订阅《XXX》" or "Subscribe to XXX"

Steps:
1. Search for the media: `scripts/moviepilot_api.sh search "title"`
2. Parse results, confirm with user if multiple matches (show title, year, type, vote)
3. Extract `tmdb_id` (or `douban_id`), `type`, `title`, `year` from the chosen result
4. Create subscription:
   ```bash
   scripts/moviepilot_api.sh sub_add '{"name":"Title","type":"电影","tmdbid":12345,"year":"2024"}'
   ```
   - For TV shows, include `"season": N` if subscribing to a specific season
   - `type` must be `"电影"` (movie) or `"电视剧"` (TV show)

### 2. View Subscriptions

```bash
scripts/moviepilot_api.sh sub_list
```
Present results as a readable list: name, type, year, state.

### 3. Cancel Subscription

By subscription ID:
```bash
scripts/moviepilot_api.sh sub_delete <subscribe_id>
```

By media ID:
```bash
scripts/moviepilot_api.sh sub_delete_media "tmdb:12345"
```

### 4. Check Downloads

```bash
scripts/moviepilot_api.sh downloads
```

### 5. Browse Recommendations

```bash
# Options: douban_movie_hot, douban_tv_hot, tmdb_trending, tmdb_movies, tmdb_tvs, bangumi_calendar
scripts/moviepilot_api.sh recommend douban_movie_hot
```

### 6. Search Torrent Resources

```bash
scripts/moviepilot_api.sh search_resource "keyword"
```

## Important Notes

- Media IDs use prefix format: `tmdb:12345`, `douban:12345`, `bangumi:12345`
- Always search first to get the correct media ID before subscribing
- When search returns multiple results, present them to the user for selection
- The `type` field in Chinese: `"电影"` for movies, `"电视剧"` for TV shows
- For detailed API docs, see [references/api_reference.md](references/api_reference.md)

## Script Reference

The helper script `scripts/moviepilot_api.sh` supports these actions:

| Action | Description | Example |
|--------|-------------|---------|
| `login` | Get auth token | `login user pass` |
| `search` | Search media | `search "流浪地球"` |
| `media_detail` | Media details | `media_detail "tmdb:12345"` |
| `sub_list` | List subscriptions | `sub_list` |
| `sub_add` | Add subscription | `sub_add '{"name":"...","type":"电影","tmdbid":123}'` |
| `sub_delete` | Delete by sub ID | `sub_delete 5` |
| `sub_delete_media` | Delete by media ID | `sub_delete_media "tmdb:123"` |
| `sub_detail` | Subscription detail | `sub_detail 5` |
| `sub_refresh` | Refresh all subs | `sub_refresh` |
| `sub_history` | Subscription history | `sub_history movie` |
| `downloads` | Active downloads | `downloads` |
| `recommend` | Browse recommendations | `recommend tmdb_trending` |
| `search_resource` | Search torrents | `search_resource "keyword"` |
