# Slack OAuth Provider

## Overview

Slack uses OAuth v2 with **user tokens** (not bot tokens). TapAuth requests `user_scope` permissions, giving agents access to act on behalf of a specific user.

## Key Gotchas

### Bot Tokens vs User Tokens
Slack's OAuth v2 issues **both** a bot token (`access_token` at top level) and a user token (`authed_user.access_token`). TapAuth extracts the **user token** since agents need to act as the user, not as a bot.

### 200 on Errors
Slack API returns **HTTP 200 for errors** — you must check `body.ok === true`. A `200` response with `"ok": false` is an error. Always inspect the `error` field:
```json
{ "ok": false, "error": "invalid_auth" }
```

### Per-Method Rate Limits
Slack rate limits are **per-method, per-workspace** (not global). Tier 1 methods allow ~1 req/sec, Tier 4 allows ~100 req/min. Check `Retry-After` headers on 429s.

### Tokens Don't Expire
Slack user tokens **do not expire by default**. There is no refresh flow unless token rotation is explicitly enabled in the Slack app settings. TapAuth stores `expires_in: null`.

### HTTPS Required
All redirect URIs must use HTTPS — no exceptions, even in development.

## Scopes

TapAuth requests user scopes via the `user_scope` param (not `scope`). Default identity scopes:
- `identity.basic` — basic user info
- `identity.email` — email address
- `identity.team` — workspace info
- `identity.avatar` — profile picture

Additional scopes available: `users:read`, `channels:read`, `channels:history`, `files:read`, `search:read`, etc.

## Token Exchange

The token response nests user credentials under `authed_user`:
```json
{
  "ok": true,
  "access_token": "xoxb-...",
  "authed_user": {
    "access_token": "xoxp-...",
    "scope": "identity.basic,identity.email",
    "token_type": "bearer"
  }
}
```

TapAuth extracts `authed_user.access_token` as the grant's access token.
