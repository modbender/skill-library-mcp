---
name: api-reference
description: OpenAPI-first reference for Remix agent publishing REST routes
metadata:
  tags: remix, api, rest, reference
---

## OpenAPI-First Rule

Before generating or executing API calls, fetch:

- `https://api.remix.gg/docs/json`

Use OpenAPI as the contract source of truth for:
- methods (`GET`/`POST`/...)
- paths
- params/query/body schemas
- response shapes

Base headers:

```http
Authorization: Bearer <api_key>
Content-Type: application/json
```

Base URL: `https://api.remix.gg`

OpenAPI UI: `https://api.remix.gg/docs`

## Response Envelope

Success:

```json
{ "success": true, "data": { "...": "..." } }
```

Error:

```json
{ "success": false, "error": { "code": "SOME_CODE", "message": "...", "details": null } }
```

## Endpoint Families

Use OpenAPI for exact paths; these are the stable groups:
- Metadata: categories
- Games: list/detail/create
- Versions: list/detail/code/thread/status/validate/code-update
- Assets: list game assets (read-only discovery for app-uploaded files)
- Readiness: launch readiness checks

## Not Exposed in Agent REST

- No delete route.
- No create-version route.
- No submit route.
- No write endpoints for game metadata or assets in this surface.

## Asset Upload State (As of February 9, 2026)

- Binary asset uploads (including icon/image/audio files) are handled in the Remix app/Studio upload flow.
- Agent REST currently exposes asset discovery via `GET /v1/agents/games/{gameId}/assets` only.
- Recommended pattern: upload assets in the app first, then reference hosted asset URLs from the assets list in your HTML game code.

Canonical flow:
1. create game
2. upload/update version code
3. validate and/or launch-readiness
4. check status

## Common Error Codes

- `UNAUTHORIZED` - Missing/invalid API key.
- `ACCOUNT_INELIGIBLE` - User is banned/deleted.
- `FORBIDDEN` - User does not own the game/version.
- `GAME_NOT_FOUND` - Game missing.
- `VERSION_NOT_FOUND` - Game/version mismatch or missing.
- `MAX_IN_DEV_GAMES_EXCEEDED` - Creator reached cap.
- `VALIDATION_ERROR` - Body/query failed validation.
- `INVALID_JSON` - Body could not be parsed as JSON.
- `LIVE_VERSION_LOCKED` - Attempted to edit a live version.
- `VERSION_NOT_EDITABLE` - Version is submitted/approved/launched.
- `THREAD_CREATE_FAILED` - Failed to provision upload thread.
- `RATE_LIMITED` - API key rate limit exceeded.
- `INTERNAL_SERVER_ERROR` - Unexpected server failure.
