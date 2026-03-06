# Logging & Error Schema

## Structured log shape
```json
{
  "ts": "2026-02-24T10:00:00+01:00",
  "level": "info",
  "module": "spotify/auth",
  "event": "token_refreshed",
  "message": "Spotify token refreshed",
  "meta": { "expiresIn": 3600 }
}
```

## Unified error payload
```json
{
  "ok": false,
  "error": {
    "code": "SPOTIFY_RATE_LIMIT",
    "message": "Spotify API rate limit reached",
    "retryAfterSec": 30,
    "module": "spotify/playback"
  }
}
```

## Error codes (starter set)
- `CONFIG_INVALID`
- `AUTH_REQUIRED`
- `TOKEN_REFRESH_FAILED`
- `SPOTIFY_FORBIDDEN`
- `SPOTIFY_RATE_LIMIT`
- `DEVICE_NOT_FOUND`
- `DB_WRITE_FAILED`
