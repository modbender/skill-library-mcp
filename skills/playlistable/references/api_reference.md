# Playlistable MCP — API Reference

Base URL: `https://mcp.playlistable.io`
Transport: Streamable HTTP (POST `/` with JSON-RPC body)
Auth: `Authorization: Bearer sk_mcp_...` or `x-api-key: sk_mcp_...`

---

## generate_playlist

Create a playlist from a mood description. Returns immediately — tracks are generated asynchronously in the background.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `mood` | string | yes | Mood or prompt describing the playlist (1-500 chars) |

**Example:**
```json
{ "mood": "energetic workout bangers" }
```

**Response:**
```json
{
  "id": "abc123",
  "name": "energetic workout bangers",
  "spotifyId": "37i9dQZF1...",
  "url": "https://open.spotify.com/playlist/37i9dQZF1...",
  "playlistableUrl": "https://app.playlistable.io/playlist/abc123",
  "status": "pending",
  "visibility": "public",
  "createdAt": "2026-02-27T..."
}
```

**Notes:**
- Status starts as `"pending"` while tracks are being curated
- Use `get_playlist` to poll until status becomes `"ready"`
- Playlists are created as public on Spotify
- Free users get a teaser playlist (limited tracks); paid users get the full result

---

## get_playlist

Get full details of a playlist including tracks.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `id` | string | yes | Playlistable playlist ID |

**Example:**
```json
{ "id": "abc123" }
```

**Response:** Full playlist object with `tracks` array containing track name, artist, Spotify URL, album art, etc.

---

## get_playlists

List the authenticated user's playlists. Returns up to 10 per request.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `lastDocId` | string | no | ID of last playlist from previous page (for pagination) |

**Example:**
```json
{}
```

**Response:** Array of playlist objects (without full track lists).

---

## edit_playlist

Add or remove songs from a playlist using Spotify track IDs.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `id` | string | yes | Playlistable playlist ID |
| `addedSongs` | string or string[] | no | Spotify track ID(s) to add |
| `removedSongs` | string or string[] | no | Spotify track ID(s) to remove |

**Example:**
```json
{
  "id": "abc123",
  "addedSongs": ["4iV5W9uYEdYUVa79Axb7Rh", "7qiZfU4dY1lWllzX7mPBI3"],
  "removedSongs": ["1301WleyT98MSxVHPZCA6M"]
}
```

**Notes:** Use `search_songs` to find Spotify track IDs.

---

## delete_playlist

Delete a playlist by ID. Removes it from both Playlistable and Spotify.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `id` | string | yes | Playlistable playlist ID |

**Example:**
```json
{ "id": "abc123" }
```

---

## playlist_suggestions

Get 6 AI-generated playlist mood suggestions personalized to the user's listening history and time of day.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `userHour` | number (0-23) | no | User's local hour for time-aware suggestions (0 = midnight, 23 = 11pm). Defaults to server time. |

**Example:**
```json
{ "userHour": 8 }
```

**Response:** Array of 6 mood strings, e.g.:
```json
[
  "energetic morning workout",
  "upbeat commute pop",
  "focused deep work ambient",
  "feel-good indie for coffee",
  "motivational hip-hop",
  "chill acoustic wake-up"
]
```

**Notes:**
- Morning hours (6-11) → energetic/focus moods
- Afternoon (12-17) → productive/upbeat moods
- Evening (18-22) → relaxing/social moods
- Night (23-5) → chill/sleep moods

---

## search_songs

Search Spotify tracks by query.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `query` | string | yes | Search query (1-300 chars) |
| `limit` | number | no | Results to return (1-10, default 10) |

**Example:**
```json
{ "query": "Blinding Lights", "limit": 5 }
```

**Response:**
```json
[
  {
    "id": "0VjIjW4GlUZAMYd2vXMi3b",
    "name": "Blinding Lights",
    "artist": "The Weeknd",
    "image": "https://i.scdn.co/image/...",
    "url": "https://open.spotify.com/track/0VjIjW4GlUZAMYd2vXMi3b"
  }
]
```

---

## search_artists

Search Spotify artists by query.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `query` | string | yes | Search query (1-300 chars) |
| `limit` | number | no | Results to return (1-10, default 10) |

**Example:**
```json
{ "query": "The Weeknd", "limit": 3 }
```

**Response:**
```json
[
  {
    "id": "1Xyo4u8uXC1ZmMpatF05PJ",
    "name": "The Weeknd",
    "image": "https://i.scdn.co/image/...",
    "url": "https://open.spotify.com/artist/1Xyo4u8uXC1ZmMpatF05PJ",
    "genres": ["canadian contemporary r&b", "canadian pop", "pop"]
  }
]
```

---

## Authentication Endpoints

These are REST endpoints, not MCP tools — used internally by `auth.mjs`.

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/authorize?session_id={id}` | GET | Start OAuth flow (creates auth session) |
| `/login?session_id={id}` | GET | Interactive Spotify login page |
| `/callback` | GET | OAuth callback (handles Spotify redirect) |
| `/oauth/token` | POST | Exchange authorization code for API key |
| `/session?session_id={id}` | GET | Check auth session status |
| `/.well-known/oauth-authorization-server` | GET | OAuth server metadata |

**API Key format:** `sk_mcp_{base64url-encoded-32-bytes}`

**Auth headers (any of):**
- `Authorization: Bearer sk_mcp_...`
- `x-api-key: sk_mcp_...`

---

## Error Handling

| Scenario | What happens |
|----------|-------------|
| Token expired / invalid | 401 response — re-run `scripts/auth.mjs` |
| Free tier quota exceeded | Error text includes `purchase_url` |
| Missing Spotify token | "Missing Spotify token" — user needs to re-authenticate |
| Playlist not found | 404-style error in content text |
