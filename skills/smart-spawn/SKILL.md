---
name: smart-spawn-api
description: "Pick the best AI model for any task using the Smart Spawn API. No plugin needed — just HTTP requests to ss.deeflect.com/api."
---

# Smart Spawn API

Pick the best AI model for any task. Call the API, get a model recommendation, spawn with it.

**No plugin required.** Works with any OpenClaw instance or any HTTP client.

## Quick Start

```
1. GET ss.deeflect.com/api/pick?task=<description>&budget=<tier>
2. Use the returned model ID in sessions_spawn
```

## Pick Best Model

```bash
GET https://ss.deeflect.com/api/pick?task=build+a+react+dashboard&budget=medium
```

Response:
```json
{
  "data": {
    "id": "anthropic/claude-opus-4.6",
    "name": "Claude Opus 4.6",
    "score": 86,
    "pricing": { "prompt": 5, "completion": 25 },
    "reason": "Best general model at medium budget ($0-5/M) — score: 86"
  }
}
```

Then spawn:
```
sessions_spawn(task="Build a React dashboard with auth", model="anthropic/claude-opus-4.6")
```

## Parameters

| Param | Required | Description |
|-------|----------|-------------|
| `task` | Yes | Task description or category: `coding`, `reasoning`, `creative`, `vision`, `research`, `fast-cheap`, `general` |
| `budget` | No | `low` ($0-1/M), `medium` ($0-5/M, default), `high` ($2-20/M), `any` |
| `exclude` | No | Comma-separated model IDs to skip |
| `context` | No | Tags like `vision,long-context` for routing boost |

## Get Multiple Recommendations

```bash
GET https://ss.deeflect.com/api/recommend?task=coding&budget=low&count=3
```

Returns diverse models from different providers. Use for collective/parallel spawning.

## Compare Models

```bash
GET https://ss.deeflect.com/api/compare?models=anthropic/claude-opus-4.6,openai/gpt-5.2
```

Side-by-side scores, pricing, capabilities.

## Browse All Models

```bash
GET https://ss.deeflect.com/api/models?category=coding&sort=score&limit=10
```

Sort by `score`, `cost`, `efficiency`, or any category name.

## Decompose Complex Tasks

```bash
POST https://ss.deeflect.com/api/decompose
{"task": "Build and deploy a SaaS app", "budget": "medium"}
```

Returns sequential steps with optimal model per step.

## Swarm (Parallel DAG)

```bash
POST https://ss.deeflect.com/api/swarm
{"task": "Research competitors and build pitch deck", "budget": "low"}
```

Returns a dependency graph of parallel tasks with models assigned.

## Usage Pattern

For any task that needs a sub-agent:

1. **Decide budget** — `low` for cheap/fast, `medium` for quality, `high` for best available
2. **Call /api/pick** with the task description
3. **Use the returned `id`** as the `model` parameter in `sessions_spawn`
4. **If task is complex** — use `/api/decompose` or `/api/swarm` to break it into subtasks, spawn each with its recommended model

## Error Handling

- API down → skip model selection, use `sessions_spawn` without a model (falls back to default)
- No model found (404) → widen budget to `any` and retry
- Rate limited (429) → wait and retry, or fall back to default

## API Status

```bash
GET https://ss.deeflect.com/api/status
```

Shows model count, data freshness, source health. Data refreshes every 6 hours from 5 benchmark sources.
