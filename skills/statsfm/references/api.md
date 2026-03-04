# stats.fm API Reference

Base URL: `https://api.stats.fm/api/v1`

All responses wrap data in `{"item": ...}` (single) or `{"items": [...]}` (list).

## Query Parameters

### Ranges (`range=`)
`today` | `days` | `weeks` | `months` | `lifetime`

### Date Filtering
- `before` — Unix timestamp (ms)
- `after` — Unix timestamp (ms)

### Pagination
- `limit` — max items to return
- `offset` — skip N items

### Order
- `order` — `asc` or `desc`

### Timezone
- `timeZone` — IANA timezone (e.g., `America/Toronto`)

---

## Users

### GET `/users/{userId}`
Profile info: id, customId, displayName, image, isPlus, bio, pronouns, privacySettings.

### GET `/users/{userId}/privacy`
Privacy settings object.

### GET `/users/{userId}/profile`
Profile details (bio, pronouns, theme).

### GET `/users/{userId}/streams/current`
Currently playing track. Returns: date, isPlaying, progressMs, deviceName, track object.

### GET `/users/{userId}/streams/recent`
Recently played tracks. Params: `limit`, `offset`.

### GET `/users/{userId}/streams`
Full stream history. Params: `before`, `after`, `limit`, `offset`.

### GET `/users/{userId}/streams/stats`
Aggregate stats. Params: `range` or `before`/`after`.
Returns: playedMs, count, etc.

### GET `/users/{userId}/streams/stats/dates`
Stats broken down by date. Params: `range` or `before`/`after`, `timeZone`.

### GET `/users/{userId}/top/tracks`
Top tracks. Params: `range`, `limit`, `offset`, `orderBy`.
Response items: position, streams, playedMs, track {id, name, artists[], albums[], durationMs, explicit}.

### GET `/users/{userId}/top/artists`
Top artists. Params: `range`, `limit`, `offset`, `orderBy`.
Response items: position, streams, playedMs, artist {id, name, image, genres[], followers}.

### GET `/users/{userId}/top/albums`
Top albums. Params: `range`, `limit`, `offset`, `orderBy`.
Response items: position, streams, playedMs, album {id, name, image}.

### GET `/users/{userId}/top/genres`
Top genres. Params: `range`, `limit`, `offset`, `orderBy`.
Response items: position, streams, playedMs, genre {tag}.

### GET `/users/{userId}/streams/tracks/{trackId}`
Streams of a specific track. Params: `range` or `before`/`after`, `limit`, `offset`.

### GET `/users/{userId}/streams/tracks/{trackId}/stats`
Stats for a specific track.

### GET `/users/{userId}/streams/tracks/{trackId}/stats/dates`
Per-date stats for a track. Params: `timeZone`.

### GET `/users/{userId}/streams/tracks/{trackId}/stats/per-day`
Per-day breakdown for a track.

### GET `/users/{userId}/streams/artists/{artistId}`
Streams of a specific artist.

### GET `/users/{userId}/streams/artists/{artistId}/stats`
Stats for a specific artist.

### GET `/users/{userId}/streams/artists/{artistId}/stats/dates`
Per-date stats for an artist.

### GET `/users/{userId}/streams/artists/{artistId}/stats/per-day`
Per-day breakdown for an artist.

### GET `/users/{userId}/streams/albums/{albumId}`
Streams of a specific album.

### GET `/users/{userId}/streams/albums/{albumId}/stats`
Stats for a specific album.

### GET `/users/{userId}/streams/albums/{albumId}/stats/dates`
Per-date stats for an album.

### GET `/users/{userId}/streams/albums/{albumId}/stats/per-day`
Per-day breakdown for an album.

### GET `/users/{userId}/streams/tracks/list`
Batch stream history for multiple tracks. Params: `ids` (comma-separated track IDs), `range` or `before`/`after`, `limit`, `offset`.

### GET `/users/{userId}/streams/tracks/list/stats`
Batch stats for multiple tracks. Params: `ids` (comma-separated track IDs), `range` or `before`/`after`.
Returns: Record keyed by track ID → StreamStats[].

### GET `/users/{userId}/top/artists/{artistId}/tracks`
Top tracks by a specific artist for this user.

### GET `/users/{userId}/top/artists/{artistId}/albums`
Top albums by a specific artist for this user.

### GET `/users/{userId}/top/albums/{albumId}/tracks`
Top tracks from a specific album for this user.

### GET `/users/{userId}/records/artists`
Artist records (milestones).

### GET `/users/{userId}/friends`
Friends list.

### GET `/users/{userId}/friends/count`
Friend count (number).

---

## Artists

### GET `/artists/{id}`
Artist info. Add `?type=spotify` to look up by Spotify ID instead of stats.fm ID.

### GET `/artists/list?ids=1,2,3`
Batch artist lookup. Add `&type=spotify` for Spotify IDs.

### GET `/artists/{id}/tracks`
All tracks by artist.

### GET `/artists/{id}/tracks/top`
Top tracks by artist.

### GET `/artists/{id}/albums`
All albums by artist.

### GET `/artists/{id}/albums/top`
Top albums by artist.

### GET `/artists/{id}/related`
Related artists.

### GET `/artists/{id}/top/listeners`
Top listeners (requires auth).

---

## Tracks

### GET `/tracks/{id}`
Track info. Add `?type=spotify` for Spotify ID lookup.

### GET `/tracks/list?ids=1,2,3`
Batch track lookup. Add `&type=spotify` for Spotify IDs.

### GET `/SPOTIFY/audio-analysis/{spotifyId}`
Spotify audio analysis.

### GET `/SPOTIFY/audio-features/{spotifyId}`
Spotify audio features (danceability, energy, etc.).

### GET `/SPOTIFY/audio-features?ids=id1,id2`
Batch audio features.

---

## Albums

### GET `/albums/{id}`
Album info. Add `?type=spotify` for Spotify ID lookup.

### GET `/albums/list?ids=1,2,3`
Batch album lookup.

### GET `/albums/{id}/tracks`
Album tracklist.

---

## Records

### GET `/records/artists/{recordId}`
Get a specific artist record (milestone) by record ID.

### GET `/records/artists?ids=1,2,3`
Batch lookup of artist records by IDs.

### GET `/records/artists/{recordId}/history`
History of a specific artist record.

---

## Search

### GET `/search?query=X&type=artist,track,album`
Search across types. Params: `query`, `type` (comma-separated: `artist`, `track`, `album`), `limit`, `offset`.

### GET `/search/elastic?query=X&type=artist`
Elastic search variant.

---

## Charts

### GET `/charts/top/tracks`
Global top tracks. Params: `range`.

### GET `/charts/top/artists`
Global top artists. Params: `range`.

### GET `/charts/top/albums`
Global top albums. Params: `range`.

### GET `/charts/top/users`
Top users globally. Params: `range`.

---

## Stats

### GET `/stats/database/size`
Database size info.
