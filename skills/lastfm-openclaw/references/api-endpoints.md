# Last.fm API Endpoints Reference

This document describes the Last.fm API endpoints used by this skill.

## Base URL

```
https://ws.audioscrobbler.com/2.0/
```

## Authentication

All read operations require only an API key. Write operations require a session key obtained through the authentication flow.

See [auth-guide.md](auth-guide.md) for authentication setup.

## Required Parameters

All requests must include:

| Parameter | Description |
|-----------|-------------|
| `api_key` | Your Last.fm API key |
| `method` | API method name |
| `format` | Response format (`json` recommended) |

---

## User Methods

### user.getInfo

Get information about a user profile.

**URL:** `?method=user.getInfo&user=USERNAME&api_key=KEY&format=json`

**Parameters:**

| Parameter | Required | Description |
|-----------|----------|-------------|
| `user` | Yes | Last.fm username |
| `api_key` | Yes | API key |

**Response Fields:**

```json
{
  "user": {
    "name": "username",
    "realname": "Real Name",
    "url": "https://www.last.fm/user/username",
    "image": [...],
    "country": "Country",
    "age": "25",
    "gender": "m",
    "subscriber": "0",
    "playcount": "54189",
    "playlists": "4",
    "registered": {
      "unixtime": "1037793040",
      "#text": "2002-11-20 11:50"
    }
  }
}
```

---

### user.getRecentTracks

Get recent tracks, including now playing.

**URL:** `?method=user.getRecentTracks&user=USERNAME&api_key=KEY&format=json&limit=10`

**Parameters:**

| Parameter | Required | Description |
|-----------|----------|-------------|
| `user` | Yes | Last.fm username |
| `api_key` | Yes | API key |
| `limit` | No | Number of results (default: 50, max: 200) |
| `page` | No | Page number |
| `from` | No | Unix timestamp start |
| `to` | No | Unix timestamp end |
| `extended` | No | Include extended data (0 or 1) |

**Now Playing Detection:**

The first track in `recenttracks.track[]` has `@attr.nowplaying="true"` if currently playing.

**Response Fields:**

```json
{
  "recenttracks": {
    "user": "username",
    "track": [
      {
        "@attr": { "nowplaying": "true" },
        "artist": { "mbid": "...", "#text": "Artist Name" },
        "name": "Track Name",
        "album": { "mbid": "", "#text": "Album Name" },
        "url": "https://www.last.fm/music/...",
        "date": { "uts": "1213031819", "#text": "9 Jun 2008, 17:16" }
      }
    ]
  }
}
```

---

### user.getTopTracks

Get top tracks for a user.

**URL:** `?method=user.getTopTracks&user=USERNAME&api_key=KEY&format=json&period=7day`

**Parameters:**

| Parameter | Required | Description |
|-----------|----------|-------------|
| `user` | Yes | Last.fm username |
| `api_key` | Yes | API key |
| `period` | No | Time period (see below) |
| `limit` | No | Number of results (default: 50) |
| `page` | No | Page number |

**Period Values:**

| Value | Description |
|-------|-------------|
| `overall` | All time (default) |
| `7day` | Last 7 days |
| `1month` | Last 30 days |
| `3month` | Last 90 days |
| `6month` | Last 180 days |
| `12month` | Last year |

**Response Fields:**

```json
{
  "toptracks": {
    "user": "username",
    "track": [
      {
        "@attr": { "rank": "1" },
        "name": "Track Name",
        "playcount": "42",
        "artist": { "name": "Artist Name", "mbid": "..." },
        "album": { "mbid": "..." },
        "url": "https://www.last.fm/music/..."
      }
    ]
  }
}
```

---

### user.getTopArtists

Get top artists for a user.

**URL:** `?method=user.getTopArtists&user=USERNAME&api_key=KEY&format=json&period=7day`

**Parameters:**

Same as `user.getTopTracks` (minus `period` variation).

**Response Fields:**

```json
{
  "topartists": {
    "user": "username",
    "artist": [
      {
        "@attr": { "rank": "1" },
        "name": "Artist Name",
        "playcount": "156",
        "mbid": "...",
        "url": "https://www.last.fm/music/..."
      }
    ]
  }
}
```

---

### user.getTopAlbums

Get top albums for a user.

**URL:** `?method=user.getTopAlbums&user=USERNAME&api_key=KEY&format=json&period=7day`

**Parameters:**

Same as `user.getTopTracks`.

**Response Fields:**

```json
{
  "topalbums": {
    "user": "username",
    "album": [
      {
        "@attr": { "rank": "1" },
        "name": "Album Name",
        "playcount": "38",
        "artist": { "name": "Artist Name", "mbid": "..." },
        "mbid": "...",
        "url": "https://www.last.fm/music/..."
      }
    ]
  }
}
```

---

### user.getLovedTracks

Get loved tracks for a user.

**URL:** `?method=user.getLovedTracks&user=USERNAME&api_key=KEY&format=json`

**Parameters:**

| Parameter | Required | Description |
|-----------|----------|-------------|
| `user` | Yes | Last.fm username |
| `api_key` | Yes | API key |
| `limit` | No | Number of results (default: 50) |
| `page` | No | Page number |

**Response Fields:**

```json
{
  "lovedtracks": {
    "user": "username",
    "track": [
      {
        "artist": { "name": "Artist Name", "mbid": "..." },
        "name": "Track Name",
        "mbid": "...",
        "url": "https://www.last.fm/music/...",
        "date": { "uts": "1213031819", "#text": "9 Jun 2008, 17:16" }
      }
    ]
  }
}
```

---

## Track Methods

### track.love

Love a track for a user session. **Requires authentication.**

**URL:** POST to `https://ws.audioscrobbler.com/2.0/`

**Parameters:**

| Parameter | Required | Description |
|-----------|----------|-------------|
| `method` | Yes | `track.love` |
| `api_key` | Yes | API key |
| `sk` | Yes | Session key |
| `artist` | Yes | Artist name |
| `track` | Yes | Track name |
| `api_sig` | Yes | Method signature (see auth guide) |

**Response:**

```json
{
  "lfm": {
    "status": "ok"
  }
}
```

---

### track.unlove

Remove a loved track. **Requires authentication.**

Same parameters and response as `track.love`.

---

## Error Codes

| Code | Description |
|------|-------------|
| 2 | Invalid service |
| 3 | Invalid method |
| 4 | Authentication failed |
| 5 | Invalid format |
| 6 | Invalid parameters |
| 7 | Invalid resource |
| 8 | Operation failed |
| 9 | Invalid session key |
| 10 | Invalid API key |
| 11 | Service offline |
| 13 | Invalid method signature |
| 16 | Temporary error |
| 26 | Suspended API key |
| 29 | Rate limit exceeded |

---

## Rate Limits

- **5 requests per second** per IP address
- Implement delays between requests if making multiple calls
- Error 29 indicates rate limit exceeded

---

## References

- Official API docs: https://www.last.fm/api
- Authentication: https://www.last.fm/api/webauth
