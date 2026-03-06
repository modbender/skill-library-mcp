---
name: remix-api-key-auth
description: Configure and verify bearer API key authentication for Remix agent publishing workflows.
metadata:
  tags: remix, auth, api-key
---

# Remix API Key Setup

Use this skill when a user needs to authenticate an external service/agent for Remix server APIs.

## Steps

1. Log in to your Remix account.
2. Go to `https://remix.gg/api-keys`.
3. Create a new API key.
4. Store it as a secret in your service runtime.
5. Send:
   - `Authorization: Bearer <api_key>`
6. Use base URL `https://api.remix.gg`.

## Verification

Run a cheap authenticated call first (for example, `POST /v1/agents/games` in a test project) to verify the key works.

## Troubleshooting Invalid API Key

- Check `Authorization` is formatted as `Bearer <api_key>`.
- Re-copy the key from `https://remix.gg/api-keys` and rotate if needed.
- Verify your service is reading the expected secret/env var in the current runtime.
- Confirm the request is server-side and not exposed through browser code.
- If behavior seems inconsistent with local docs, use `https://api.remix.gg/docs` as source of truth.
