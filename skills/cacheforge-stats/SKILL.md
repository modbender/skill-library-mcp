---
name: cacheforge-stats
version: 1.0.0
description: CacheForge terminal dashboard — usage, savings, and performance metrics. See exactly where your tokens go.
author: CacheForge
license: MIT
homepage: https://app.anvil-ai.io
user-invocable: true
tags:
  - cacheforge
  - metrics
  - dashboard
  - ai-agents
  - token-optimization
  - llm
  - observability
  - discord
  - discord-v2
metadata: {"openclaw":{"emoji":"📊","homepage":"https://app.anvil-ai.io","primaryEnv":"CACHEFORGE_API_KEY","requires":{"bins":["python3"],"env":["CACHEFORGE_API_KEY"]}}}
---

## When to use this skill

Use this skill when the user wants to:
- See their CacheForge usage and savings
- View a terminal dashboard with charts
- Check token reduction rates
- See cost savings breakdown
- Monitor cache performance

## Commands

```bash
# Full terminal dashboard
python3 skills/cacheforge-stats/dashboard.py dashboard

# Usage summary
python3 skills/cacheforge-stats/dashboard.py usage --window 7d

# Breakdown by model/provider/key
python3 skills/cacheforge-stats/dashboard.py breakdown --by model

# Savings-focused view
python3 skills/cacheforge-stats/dashboard.py savings
```

## Environment Variables

- `CACHEFORGE_BASE_URL` — CacheForge API base (default: https://app.anvil-ai.io)
- `CACHEFORGE_API_KEY` — Your CacheForge API key (required)

## API Contract (current)

This skill uses:
- `GET /v1/account/billing`
- `GET /v1/account/info`
- `GET /v1/account/usage`
- `GET /v1/account/usage/breakdown`
