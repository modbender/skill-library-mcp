---
name: api-authentication
description: Authentication for Remix agent publishing REST APIs using bearer API keys
metadata:
  tags: remix, authentication, api-key
---

## Current Auth Model

Server API base URL: `https://api.remix.gg`

Remix server API uses bearer API keys generated from Remix account settings.

Supported auth header:
- `Authorization: Bearer <api_key>` (required)

The backend resolves the key to a user and enforces ownership checks on game/version mutations.

## How to Get an API Key

1. Log in to your Remix account.
2. Go to `https://remix.gg/api-keys`.
3. Generate a new API key.
4. Copy it once and store it in your server-side secret manager.

## Required Headers

```http
Authorization: Bearer <api_key>
Content-Type: application/json
```

## Security Notes

- Never expose API keys in client-side browser code.
- Store in server env vars or secret manager.
- Revoke and rotate keys from `https://remix.gg/api-keys`.
- Usage updates `lastUsed` automatically.

## Troubleshooting Invalid API Key

- Confirm you are sending the header exactly as `Authorization: Bearer <api_key>`.
- Make sure there are no extra quotes/spaces/newlines around the key in your environment variable.
- Verify the key is active in `https://remix.gg/api-keys` (not revoked or expired).
- Generate a new key and retry if you suspect the original key was copied incorrectly.
- Ensure requests are sent from your server/backend, not client-side browser code.
- For definitive request/response contracts, check `https://api.remix.gg/docs`.
