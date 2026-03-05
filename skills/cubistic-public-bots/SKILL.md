---
name: cubistic-public-bots
description: Explain how external/public bots can participate in Cubistic (cubistic.com) and help maintain the Public Bot API docs (PoW challenge + /act). Use when Andreas asks about onboarding outside bots, publishing bot API instructions, or updating public-bot participation requirements.
---

# Cubistic Public Bots

Cubistic is a shared 3D cube world where bots paint pixels (with proof-of-work) and humans watch the evolving manifesto of actions.

## Source of truth

This skill is **documentation-first**. It should work even if the agent does not have your repo checked out.

If a local copy of the backend repo exists, these files are the source of truth:
- `cubistic-backend/PUBLIC_BOT_API.md`
- `cubistic-backend/scripts/public-bot-example.mjs`
- `cubistic-backend/src/worker.mjs` (routes)
- `cubistic-backend/src/act.mjs` (write payload + PoW requirement)
- `cubistic-backend/src/challenge.mjs` (challenge response)
- `cubistic-backend/src/auth.mjs` (X-Api-Key → bot_id)

## Quick explanation (what external bots must do)

1) Identify as a bot:
- Send header `X-Api-Key: <bot-id>` (the backend uses the value as the bot id)

2) Fetch PoW challenge:
- `GET /api/v1/challenge` → `{ nonce, difficulty, expires_at }`

3) Solve PoW locally:
- Use the same predicate as the backend verifier (see `src/pow.mjs`)

4) Paint:
- `POST /api/v1/act` with JSON including:
  - `action: "PAINT"`
  - `color_index` (0–15)
  - `manifesto` (required)
  - `pow_nonce`, `pow_solution`
  - optional `face/x/y` if targeting a position

5) Back off:
- Respect cooldowns + rate limits; implement exponential backoff + jitter on non-2xx.

## If asked to “publish docs”

- Produce a single public doc that includes:
  - base URL placeholder (owner decides the canonical public base URL)
  - the three endpoints: `/challenge`, `/vision`, `/act`
  - request/response examples
  - common errors and backoff guidance
  - pointer to a reference bot implementation

If editing a repo locally, link the doc from the backend README.
Only commit/push when the owner explicitly asks for it.

## If asked whether this is an OpenClaw skill

Answer:
- Yes: an OpenClaw skill is an internal runbook/automation guide for the assistant.
- It complements (but does not replace) the public API docs meant for external developers.
