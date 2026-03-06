---
name: memory-setup
description: Configure and validate OpenClaw memory recall for persistent context. Use when enabling memory_search/memory_get, fixing poor memory recall, or setting up MEMORY.md + memory/*.md workflows in an OpenClaw workspace.
---

# Memory Setup (OpenClaw)

Set up durable memory for OpenClaw so the agent can recall prior decisions, preferences, and todos.

## 1) Prepare workspace files

In workspace root, keep:

- `MEMORY.md` (curated long-term memory)
- `memory/YYYY-MM-DD.md` (daily notes)

Optional structure:

- `memory/projects/`
- `memory/system/`
- `memory/groups/`

## 2) Enable memory search in OpenClaw config

Configure under **`agents.defaults.memorySearch`** (not top-level `memorySearch`).

Example:

```json
{
  "agents": {
    "defaults": {
      "memorySearch": {
        "enabled": true,
        "provider": "local",
        "includeDefaultMemory": true,
        "maxResults": 20,
        "minScore": 0.3
      }
    }
  }
}
```

Notes:

- `includeDefaultMemory: true` indexes `MEMORY.md` + `memory/**/*.md`.
- Providers: `local`, `openai`, `gemini`, `voyage`, `mistral`.
- If using remote provider, set corresponding API key (env var or `memorySearch.remote.apiKey`).

## 3) Restart and verify

- Restart gateway after config changes.
- Verify with:
  - `openclaw status`
  - `openclaw memory status` (if available in your CLI build)

## 4) Test recall behavior

Ask a question about past context, then verify the agent:

1. Runs `memory_search`
2. Uses `memory_get` for precise lines when needed
3. Cites source path/lines when useful

## 5) Troubleshooting

### memory_search unavailable

- Ensure `agents.defaults.memorySearch.enabled = true`.
- Ensure policy allows memory tools.
- Restart gateway.

### low-quality matches

- Lower `minScore` (e.g. `0.2`) to broaden hits.
- Raise `maxResults` (e.g. `30`).
- Write more specific notes in `MEMORY.md` and daily logs.

### local provider issues

- Confirm local model path/settings if configured.
- If needed, switch provider to remote and set API key.

## 6) Recommended operating rule

Before answering questions about prior work, decisions, dates, people, preferences, or todos:

1. `memory_search` first
2. `memory_get` second (only needed lines)
3. Say you checked memory if confidence is still low

This keeps responses grounded and auditable.
