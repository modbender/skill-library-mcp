---
name: trakt-readonly
description: Read-only Trakt.tv skill for checking a user’s currently watching item, recent episode history, watched shows list, stats, profile, and playback progress (OAuth) using the Trakt API. Use when the user asks about their Trakt activity, watching status, or recent episodes. Requires a Trakt Client ID and username.
metadata: {"openclaw":{"requires":{"env":["TRAKT_CLIENT_ID","TRAKT_USERNAME"],"bins":["curl","jq"]},"primaryEnv":"TRAKT_CLIENT_ID","emoji":"📺"}}
---

# Trakt (OpenClaw) — Read-only

Use this skill to query Trakt.tv user data via the API (read-only). Default to **read-only**; do not implement write operations unless the user explicitly asks for OAuth support.

## Requirements

- Env vars:
  - `TRAKT_CLIENT_ID` (Trakt API Client ID)
  - `TRAKT_USERNAME` (Trakt username or user slug)
  - `TRAKT_ACCESS_TOKEN` (OAuth Bearer token, required for playback)
  - `TRAKT_CLIENT_SECRET` (required for device token exchange)
- Binaries: `curl`, `jq`

## Commands (script)

Use `{baseDir}/scripts/trakt-api.sh`.

- `watching` — current movie/episode being watched
- `recent [limit]` — recent episode history (default 10, max 100)
- `watched-shows` — recently watched shows list
- `profile` — user profile
- `stats` — user stats
- `playback <type> <start_at> <end_at>` — playback progress (OAuth required)

Examples:

```
TRAKT_CLIENT_ID=xxx TRAKT_USERNAME=user {baseDir}/scripts/trakt-api.sh watching
TRAKT_CLIENT_ID=xxx TRAKT_USERNAME=user {baseDir}/scripts/trakt-api.sh recent 5
TRAKT_CLIENT_ID=xxx TRAKT_ACCESS_TOKEN=yyy {baseDir}/scripts/trakt-api.sh playback movies 2016-06-01T00:00:00.000Z 2016-07-01T23:59:59.000Z
TRAKT_CLIENT_ID=xxx {baseDir}/scripts/trakt-api.sh device-code
TRAKT_CLIENT_ID=xxx TRAKT_CLIENT_SECRET=zzz {baseDir}/scripts/trakt-api.sh device-token <device_code>
```

## Guardrails

- Never log or expose API keys or access tokens.
- Only call `https://api.trakt.tv`.
- Read-only endpoints only; playback uses OAuth token read access.
- Device OAuth flow is read-only; do not request write scopes.
- Validate `recent` limit is numeric and between 1–100.
- Handle empty/404 responses gracefully (public profile required).

## References

- Read `references/trakt-api.md` for endpoints, headers, and auth notes.
