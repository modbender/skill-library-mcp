# Whisper Context (OpenClaw Skill)

Slash OpenClaw context costs by avoiding full chat-history replay:

- Delta compression (send only what changed)
- Intelligent caching (repeat queries get cheaper)
- Long-term memory (store/recall facts, preferences, goals, events)

## Install (ClawHub)

```bash
npx clawhub@latest install whisper-context
```

## Setup

```bash
export WHISPER_CONTEXT_API_URL=https://context.usewhisper.dev
export WHISPER_CONTEXT_API_KEY=YOUR_KEY
export WHISPER_CONTEXT_PROJECT=openclaw-cost-optimization
```

## One-liners

Query packed context (use this before calling the model):

```bash
node whisper-context.mjs query_context --query "PASTE_USER_MESSAGE" --user_id "user-123" --session_id "sess-123"
```

Ingest memory after you reply:

```bash
echo '{ "user": "PASTE_USER_MESSAGE", "assistant": "PASTE_ASSISTANT_REPLY" }' | node whisper-context.mjs ingest_session --session_id "sess-123" --user_id "user-123" --turn_json -
```

Cost analytics:

```bash
node whisper-context.mjs get_cost_summary --start_date "2026-01-01T00:00:00.000Z"
```

Cache stats:

```bash
node whisper-context.mjs cache_stats
```

## What This Calls (API endpoints)

- Token savings happens on `POST /v1/context/query` using `compress: true`, `compression_strategy: "delta"`, and `use_cache: true`.
- Memory persistence uses `POST /v1/memory/ingest/session`.
- Cost reporting uses `GET /v1/cost/summary`.

## Screenshots

Add images here when you publish to ClawHub:

- `./assets/openclaw-skill.png`
- `./assets/dashboard-costs.png`

