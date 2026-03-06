---
name: clawzempic
version: 2.3.5
description: Save 70-95% on LLM costs with smart routing, caching, and memory.
author: Clawzempic
homepage: https://clawzempic.ai
license: MIT
keywords: [llm, proxy, routing, caching, cost-optimization, memory, anthropic, openrouter]
metadata:
  openclaw:
    emoji: "⚡"
    category: ai-tools
    requires:
      env: []
---

# Clawzempic

Drop-in LLM proxy that routes simple requests to cheaper models, caches repeated context, and adds cross-session memory. Works with Anthropic and OpenRouter keys.

## Install

```bash
openclaw plugins install clawzempic
```

The plugin handles signup, auth, and model registration automatically.

Or standalone:

```bash
npx clawzempic
```

## How It Works

Every request is scored for complexity in <2ms and routed to the right tier:

| Tier | Traffic | Savings |
|------|---------|---------|
| Simple | ~45% | up to 95% |
| Mid | ~25% | up to 80% |
| Complex | ~20% | 0% (full quality) |
| Reasoning | ~10% | 0% (full quality) |

No LLM classifier in the hot path. Weighted multi-dimension scorer handles routing.

## Memory

Server-side memory across sessions. No plugins, no extra API keys, no config. Your agent doesn't need to "remember" to remember.

- Recent activity (per-session)
- Scratchpad (cross-session working notes)
- Context windowing (per-request)
- Core memory (permanent facts and preferences)
- Long-term recall (embedding-based)

## Verify

```bash
npx clawzempic doctor    # Check config + test connection
npx clawzempic savings   # Savings dashboard
```

## Links

- Website: https://clawzempic.ai
- Dashboard: https://www.clawzempic.ai/dash
- npm: https://www.npmjs.com/package/clawzempic
