# Config & Secrets Policy

## Principle
- Keep secrets out of tracked files.
- Read credentials from environment or local vault injection.

## Required env vars
- `SPOTIFY_CLIENT_ID`
- `SPOTIFY_CLIENT_SECRET`

## Optional env vars
- `SPOTIFY_REDIRECT_URI`
- `LOG_LEVEL`

## Storage
- Access/refresh tokens live in `data/tokens.json` (local only).
- SQLite journal lives in `data/spotify-intelligence.sqlite`.

## Validation Rules
- Fail fast if required env vars are missing.
- Fail fast if redirect URI is malformed.
- Warn if token file permissions are too broad.
