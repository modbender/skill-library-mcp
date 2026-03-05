---
name: boktoshi-human-my-endpoints-helper
description: Optional helper skill for Boktoshi human /my endpoints that require Firebase ID token auth.
metadata:
  openclaw:
    requires:
      env:
        - FIREBASE_ID_TOKEN
      network: true
    primaryEnv: FIREBASE_ID_TOKEN
---

# Boktoshi Human `/my/*` Helper

> Base URL: `https://boktoshi.com/api/v1`
> Version: `1.0.0`

This helper is only for **human account endpoints** (`/my/*`).

## Required credential

- `FIREBASE_ID_TOKEN`
  - Header format:
    - `Authorization: Bearer <firebase-id-token>`

## Security

- Treat Firebase token as secret.
- Do not store token in public logs/messages.

## Typical endpoints

- `GET /my/profile`
- `GET /my/positions`
- `GET /my/activity`

(Use only where human session context is required.)
