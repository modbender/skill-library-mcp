# MoviePilot API Reference

## Table of Contents
- [Authentication](#authentication)
- [Media Search](#media-search)
- [Subscribe Management](#subscribe-management)
- [Download](#download)
- [Recommend](#recommend)
- [History](#history)

## Authentication

MoviePilot supports multiple authentication methods:

### Method 1: Bearer Token (OAuth2 Password)

```bash
# Obtain token
curl -X POST "${BASE_URL}/api/v1/login/access-token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=${USERNAME}&password=${PASSWORD}"
```

Response:
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "super_user": true,
  "user_id": 1,
  "user_name": "admin"
}
```

Use in subsequent requests:
```
Authorization: Bearer <access_token>
```

### Method 2: API Key (Header)
```
X-API-KEY: <your_api_key>
```

### Method 3: API Key (Query Parameter)
```
?apikey=<your_api_key>
```

### Method 4: API Token (Query Parameter)
For endpoints suffixed with `2` (e.g., `/api/v1/subscribe/list`):
```
?token=<your_token>
```

---

## Media Search

### Search media/person info
```
GET /api/v1/media/search
```
| Parameter | Type   | In    | Description |
|-----------|--------|-------|-------------|
| title     | string | query | Search keyword (required) |
| type      | string | query | `media` or `person` |
| page      | int    | query | Page number |
| count     | int    | query | Results per page |

Response: Array of MediaInfo objects with fields:
- `title`, `year`, `tmdb_id`, `douban_id`, `bangumi_id`
- `type`: `电影` or `电视剧`
- `poster_path`, `backdrop_path`, `vote_average`, `overview`
- `media_id`: Unique media identifier (format: `tmdb:12345` or `douban:12345`)
- `season_info`: Season info for TV shows

### Get media details
```
GET /api/v1/media/{mediaid}
```
| Parameter | Type   | In    | Description |
|-----------|--------|-------|-------------|
| mediaid   | string | path  | Media ID (e.g., `tmdb:12345`, `douban:12345`) |
| type_name | string | query | `电影` or `电视剧` |
| year      | string | query | Year filter |

---

## Subscribe Management

### List all subscriptions
```
GET /api/v1/subscribe/
```
No parameters. Returns array of Subscribe objects.

### List all subscriptions (API_TOKEN)
```
GET /api/v1/subscribe/list?token=<token>
```

### Add subscription
```
POST /api/v1/subscribe/
Content-Type: application/json
```
Key body fields:
```json
{
  "name": "Movie/TV name",
  "type": "电影 or 电视剧",
  "tmdbid": 12345,
  "doubanid": "12345",
  "bangumiid": 12345,
  "year": "2024",
  "season": 1,
  "keyword": "optional search keyword",
  "quality": "optional quality filter",
  "resolution": "optional resolution filter",
  "best_version": 0,
  "sites": [],
  "save_path": "optional save path"
}
```
Required: at least `name` + one of `tmdbid`/`doubanid`/`bangumiid`, and `type`.

Response:
```json
{"success": true, "message": "...", "data": {...}}
```

### Get subscription by media ID
```
GET /api/v1/subscribe/media/{mediaid}
```
| Parameter | Type   | In    | Description |
|-----------|--------|-------|-------------|
| mediaid   | string | path  | e.g., `tmdb:12345` or `douban:12345` |
| season    | int    | query | Season number (for TV) |

### Update subscription
```
PUT /api/v1/subscribe/
Content-Type: application/json
```
Body: Full Subscribe object with `id` field set.

### Delete subscription by ID
```
DELETE /api/v1/subscribe/{subscribe_id}
```

### Delete subscription by media ID
```
DELETE /api/v1/subscribe/media/{mediaid}
```
| Parameter | Type   | In    | Description |
|-----------|--------|-------|-------------|
| mediaid   | string | path  | e.g., `tmdb:12345` |
| season    | int    | query | Season number (for TV) |

### Subscription detail
```
GET /api/v1/subscribe/{subscribe_id}
```

### Search all subscriptions
```
GET /api/v1/subscribe/search
```
Triggers a search for all active subscriptions.

### Search specific subscription
```
GET /api/v1/subscribe/search/{subscribe_id}
```

### Refresh subscriptions
```
GET /api/v1/subscribe/refresh
```

### Subscription history
```
GET /api/v1/subscribe/history/{mtype}
```
| Parameter | Type   | In    | Description |
|-----------|--------|-------|-------------|
| mtype     | string | path  | `movie` or `tv` |
| page      | int    | query | Page number |
| count     | int    | query | Results per page |

---

## Download

### List active downloads
```
GET /api/v1/download/
```
| Parameter | Type   | In    | Description |
|-----------|--------|-------|-------------|
| name      | string | query | Filter by name |

### Pause download
```
GET /api/v1/download/stop/{hashString}
```

### Resume download
```
GET /api/v1/download/start/{hashString}
```

### Delete download
```
DELETE /api/v1/download/{hashString}
```

---

## Recommend

### Douban hot movies
```
GET /api/v1/recommend/douban_movie_hot?page=1&count=20
```

### Douban hot TV
```
GET /api/v1/recommend/douban_tv_hot?page=1&count=20
```

### TMDB trending
```
GET /api/v1/recommend/tmdb_trending?page=1
```

### TMDB movies
```
GET /api/v1/recommend/tmdb_movies?page=1
```

### TMDB TV shows
```
GET /api/v1/recommend/tmdb_tvs?page=1
```

### Bangumi calendar (daily airing)
```
GET /api/v1/recommend/bangumi_calendar
```

---

## History

### Download history
```
GET /api/v1/history/download
```

### Transfer history
```
GET /api/v1/history/transfer
```

---

## Search Resources (Torrent Search)

### Fuzzy search
```
GET /api/v1/search/title
```
| Parameter | Type   | In    | Description |
|-----------|--------|-------|-------------|
| keyword   | string | query | Search keyword |
| page      | int    | query | Page number |
| sites     | string | query | Comma-separated site IDs |

### Exact search by media ID
```
GET /api/v1/search/media/{mediaid}
```
| Parameter | Type   | In    | Description |
|-----------|--------|-------|-------------|
| mediaid   | string | path  | e.g., `tmdb:12345` |
| mtype     | string | query | `movie` or `tv` |
| title     | string | query | Title filter |
| year      | string | query | Year filter |
| season    | int    | query | Season number |

### Get last search results
```
GET /api/v1/search/last
```
