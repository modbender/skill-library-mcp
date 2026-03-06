---
name: whisper-context
version: 0.1.0
description: Official Whisper Context skill for OpenClaw. Cuts context tokens via delta compression + caching, and adds long-term memory across sessions.
author: "Whisper"
metadata:
  openclaw:
    requires:
      bins: ["node"]
      env: ["WHISPER_CONTEXT_API_KEY", "WHISPER_CONTEXT_PROJECT"]
      optional_env: ["WHISPER_CONTEXT_API_URL"]
    security:
      notes:
        - Makes outbound HTTPS requests to the Whisper Context API using a user-provided API key.
        - Does not require additional npm dependencies.
        - Review the script before use.
---

# Whisper Context (OpenClaw Skill)

Reduce OpenClaw API spend by shrinking the context you send to the model (delta compression + caching), while keeping long-term memory across sessions.

This skill provides a minimal Node-based helper (`whisper-context.mjs`) that OpenClaw agents can run to:

- Retrieve packed context for a user/session (`query_context`) with `compress: true` and `compression_strategy: "delta"`
- Persist the latest turn into long-term memory (`ingest_session`)
- Write/search memories (`memory_write`, `memory_search`)
- Run Oracle search/research (`oracle_search`)
- Fetch cost analytics (`get_cost_summary`)
- Inspect/warm cache (`cache_stats`, `cache_warm`)

## Install (ClawHub)

```bash
npx clawhub@latest install whisper-context
```

ClawHub installs the skill folder into your OpenClaw skills workspace (typically `~/.openclaw/workspace/skills/`).

## Setup

Set environment variables (where OpenClaw reads env for your agent):

```bash
WHISPER_CONTEXT_API_URL=https://context.usewhisper.dev
WHISPER_CONTEXT_API_KEY=YOUR_KEY
WHISPER_CONTEXT_PROJECT=openclaw-cost-optimization
```

Notes:

- `WHISPER_CONTEXT_API_URL` is optional (defaults to `https://context.usewhisper.dev`).
- `WHISPER_CONTEXT_PROJECT` can be a project slug/name.
- If the project does not exist yet, the helper will auto-create it in your org on first use.
- For best memory behavior, use stable `user_id` and `session_id` values (don’t hardcode them globally; derive them per user/session in your agent).

## Usage

All commands print JSON to stdout.

### Global flags

- `--project <slugOrName>`: override `WHISPER_CONTEXT_PROJECT`
- `--api_url <url>`: override `WHISPER_CONTEXT_API_URL`
- `--timeout_ms <n>`: request timeout (default: 30000)

### Tips for real agents (to actually slash spend)

- Always call `query_context` first and inject the returned `context` instead of re-sending your entire chat history.
- Keep `compress: true`, `compression_strategy: "delta"`, and `use_cache: true` (the defaults in this helper) to maximize token savings.
- Use stable `user_id` and `session_id` so memory works across sessions and cache keys stay effective.

### Query packed context

```bash
node whisper-context.mjs query_context \
  --query "What did we decide about the retriever cache?" \
  --user_id "user-123" \
  --session_id "session-123"
```

### Ingest a completed turn

```bash
node whisper-context.mjs ingest_session \
  --user_id "user-123" \
  --session_id "session-123" \
  --user "..." \
  --assistant "..."
```

If your message text is large or hard to shell-escape, pass JSON via stdin:

```bash
echo '{ "user": "....", "assistant": "...." }' | node whisper-context.mjs ingest_session --session_id "session-123" --turn_json -
```

## Security / Privacy Notes

- `ingest_session` sends both user and assistant text to the Context API (so it can build memory and improve retrieval).
- The helper only reads local files if you explicitly pass `@path` (or stdin via `-`).
- Treat your `WHISPER_CONTEXT_API_KEY` like a secret; don’t commit it to git.

### Write a memory

```bash
node whisper-context.mjs memory_write \
  --memory_type "preference" \
  --content "User prefers concise answers." \
  --user_id "user-123"
```

### Search memories

```bash
node whisper-context.mjs memory_search \
  --query "preferences" \
  --user_id "user-123"
```

### Oracle search / research

```bash
node whisper-context.mjs oracle_search --query "How does delta compression work?" --mode search
node whisper-context.mjs oracle_search --query "Design a plan..." --mode research --max_steps 3
```

### Cost summary

```bash
node whisper-context.mjs get_cost_summary \
  --start_date "2026-01-01T00:00:00.000Z" \
  --end_date "2026-02-01T00:00:00.000Z"
```

### Cache stats (prove your savings)

```bash
node whisper-context.mjs cache_stats
```

### Cache warm (optional)

```bash
node whisper-context.mjs cache_warm --queries "retriever cache,l1 query cache,delta compression" --ttl_seconds 3600
```

## Agent Integration Pattern

1. Before calling the model: run `query_context` and prepend the returned `context` (if present) to your prompt.
2. After replying: run `ingest_session` with the user + assistant messages to persist memory.

## Troubleshooting

- `Missing WHISPER_CONTEXT_API_KEY`: export the env var where OpenClaw runs commands.
- `HTTP 401/403`: verify your API key and that it has access to the project/org.
- `HTTP 404 Project not found`: verify `WHISPER_CONTEXT_PROJECT` (slug/name) exists.
