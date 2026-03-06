---
name: openclaw-model-failover
slug: openclaw-model-failover
description: "OpenClaw plugin: auto-detect rate limits/quota/auth failures and switch sessions to fallback LLMs. Prevents 'API rate limit reached' loops by patching pinned session models."
---

# openclaw-model-failover (OpenClaw Plugin)

This is an **OpenClaw Gateway plugin**, not an agent skill.

It mitigates outages by automatically switching the model used for a conversation when it detects:
- Rate limits / quota exhaustion (HTTP 429, RESOURCE_EXHAUSTED)
- Auth/scope failures (e.g. OpenAI: missing `api.responses.write`)

## Install

### Option A: ClawHub

```bash
clawhub install openclaw-model-failover
```

### Option B: From repo (dev)

```bash
openclaw plugins install -l ~/.openclaw/workspace/openclaw-model-failover
openclaw gateway restart
```

## Configure

Set model fallback order (example):

- Anthropic -> OpenAI -> Google

See README for the full config block.
