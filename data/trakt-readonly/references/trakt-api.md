# Trakt API (Read-only) Quick Reference

Base URL: `https://api.trakt.tv`

Headers (required for all requests):
- `Content-Type: application/json`
- `trakt-api-version: 2`
- `trakt-api-key: <TRAKT_CLIENT_ID>`

## Read-only endpoints used by this skill

### Playback progress (OAuth required)
`GET /sync/playback/{type}?start_at=...&end_at=...`

Headers:
- `Authorization: Bearer <TRAKT_ACCESS_TOKEN>`
- `Content-Type: application/json`
- `trakt-api-version: 2`
- `trakt-api-key: <TRAKT_CLIENT_ID>`

Notes:
- `type`: `movies` or `episodes`
- `start_at`/`end_at`: ISO timestamps

---

- Current watching:
  - `GET /users/{username}/watching`
- Recent episode history:
  - `GET /users/{username}/history/episodes?limit=10`
- Watched shows list:
  - `GET /users/{username}/watched/shows`
- User profile:
  - `GET /users/{username}`
- User stats:
  - `GET /users/{username}/stats`

## Auth

Read-only endpoints above require **only** a Trakt **Client ID** (API key). OAuth is required for playback progress and device flow (read-only).

### Device OAuth
- `POST /oauth/device/code` with `{ client_id }`
- `POST /oauth/device/token` with `{ code, client_id, client_secret }`

User completes activation at https://trakt.tv/activate.

## Notes

- `username` can be the Trakt username or user slug.
- Public profiles are required for access to user data without OAuth.
