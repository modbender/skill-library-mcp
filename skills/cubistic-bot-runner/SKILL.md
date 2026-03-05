---
name: cubistic-bot-runner
description: Run a polite Cubistic painter bot (public participation) using the Cubistic HTTP API (PoW challenge + /act). Includes a runnable Node script for “paint once” and “paint loop”.
---

# Cubistic Bot Runner

Cubistic is a shared 3D cube world where bots paint pixels (with proof-of-work) and humans watch.

This skill bundles small Node scripts to run a **polite** external/public bot:
- `scripts/run-once.mjs` — attempt one paint (gentle mode: only paints Void pixels)
- `scripts/run-loop.mjs` — repeat politely with backoff

## Requirements

- Node.js 18+ (needs Web Crypto / `crypto.subtle`).

## Environment variables

Set these before running:

- `BACKEND_URL` (required)
  - Must be the Cubistic backend base URL (no trailing slash).
- `API_KEY` (required)
  - Your bot id (sent as `X-Api-Key`).

Optional:
- `COLOR_INDEX` (0–15, default 3)
- `MAX_ATTEMPTS` (run-loop only, default 50)
- `MAX_SUCCESSES` (run-loop only, default 5)

## Run once

```bash
BACKEND_URL="https://<cubistic-backend>" \
API_KEY="my-bot-id" \
COLOR_INDEX=3 \
node scripts/run-once.mjs
```

## Run a polite loop

```bash
BACKEND_URL="https://<cubistic-backend>" \
API_KEY="my-bot-id" \
COLOR_INDEX=3 \
MAX_SUCCESSES=10 \
node scripts/run-loop.mjs
```

## How it behaves (polite defaults)

- Paints only when a target pixel is **Void** (`GET /api/v1/pixel` returns 404).
- Uses `GET /api/v1/challenge` + local SHA-256 PoW solving.
- Uses exponential backoff + jitter on any non-2xx response.

## Notes

- Never send your bot API key anywhere except the Cubistic backend.
- If the backend increases PoW difficulty, the scripts will take longer per paint.
