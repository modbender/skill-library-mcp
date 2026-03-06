---
name: cacheforge-setup
version: 1.0.0
description: Set up CacheForge — register, configure upstream, get your API key in 30 seconds. One line of config, zero code changes.
author: CacheForge
license: MIT
homepage: https://app.anvil-ai.io
user-invocable: true
tags:
  - cacheforge
  - setup
  - onboarding
  - ai-agents
  - token-optimization
  - llm
  - openai
  - proxy
  - discord
  - discord-v2
metadata: {"openclaw":{"emoji":"⚒️","homepage":"https://app.anvil-ai.io","requires":{"bins":["python3"]}}}
---

## When to use this skill

Use this skill when the user wants to:
- Set up CacheForge for the first time
- Register a new CacheForge account
- Connect their LLM API provider to CacheForge
- Get a CacheForge API key

## Setup Flow

1. **Detect existing API keys** — Check for `OPENAI_API_KEY`, `OPENROUTER_API_KEY`, `ANTHROPIC_API_KEY` in the environment
2. **Collect credentials** — Ask user for email and password if not provided
3. **Auto-detect provider** — Infer upstream kind from key prefix:
   - `sk-or-` → openrouter
   - `sk-ant-` → anthropic
   - `sk-` → custom (OpenAI-compatible; legacy `openai` alias still accepted)
   - Preset default base URLs:
     - openrouter → `https://openrouter.ai/api/v1`
     - anthropic → `https://api.anthropic.com`
     - custom → `https://api.fireworks.ai/inference/v1`
4. **Provision** — Run `python3 setup.py provision` to register/authenticate and get a CacheForge API key
   - If registration mode is invite-only, pass `--invite-code` (or set `CACHEFORGE_INVITE_CODE`).
   - If email verification is enabled, complete verification and rerun `provision` to mint the tenant API key.
5. **Validate** — Run `python3 setup.py validate` to make a test request through the proxy
6. **Configure OpenClaw (recommended)** — Print the exact OpenClaw snippet and (with approval) apply it to `~/.openclaw/openclaw.json`
   - Print: `python3 setup.py openclaw-snippet`
   - Apply: `python3 setup.py openclaw-apply --set-default`
   - If upstream is OpenRouter, the snippet registers multiple popular models so users can switch in `/model` immediately.
7. **Fund credits** — Before first proxy traffic, top up at least `$10` via Stripe or crypto:
   - `python3 skills/cacheforge-ops/ops.py topup --amount 10 --method stripe`
   - `python3 skills/cacheforge-ops/ops.py topup --amount 10 --method crypto`

Important (Vault Mode):
- Vault Mode virtualizes tool outputs only when the request advertises a fetch-capable tool definition (`web_fetch` or `browser`).
- Without a fetch tool definition, CacheForge fail-opens with reason `no_fetch_tool`.

## Commands

```bash
# Full setup (interactive)
python3 skills/cacheforge-setup/setup.py provision \
  --email user@example.com \
  --password "..." \
  --invite-code "..." \
  --upstream-kind custom \
  --upstream-base-url https://api.fireworks.ai/inference/v1 \
  --upstream-key fw_...

# Just validate an existing setup
python3 skills/cacheforge-setup/setup.py validate \
  --base-url https://app.anvil-ai.io \
  --api-key cf_...

# Print the OpenClaw snippet (same structure as the CacheForge console)
python3 skills/cacheforge-setup/setup.py openclaw-snippet \
  --base-url https://app.anvil-ai.io \
  --api-key cf_...

# Apply CacheForge provider config into OpenClaw (JSON5-safe; prompts for approval)
python3 skills/cacheforge-setup/setup.py openclaw-apply \
  --base-url https://app.anvil-ai.io \
  --api-key cf_... \
  --set-default
```

## Environment Variables

- `CACHEFORGE_BASE_URL` — CacheForge API base (default: https://app.anvil-ai.io)
- `CACHEFORGE_API_KEY` — Existing API key (skip provisioning if set)
- `CACHEFORGE_INVITE_CODE` — Invite code (required on invite-only deployments)
- `OPENAI_API_KEY`, `OPENROUTER_API_KEY`, `ANTHROPIC_API_KEY`, `FIREWORKS_API_KEY` — Auto-detected for upstream
- `UPSTREAM_BASE_URL` — Optional override for `provision` upstream base URL

## After Setup

Once provisioned, set:
```bash
export OPENAI_BASE_URL=https://app.anvil-ai.io/v1
export OPENAI_API_KEY=cf_...  # your CacheForge tenant API key
```

All OpenAI-compatible tools (OpenClaw, Claude Code, Cursor, any agent framework) will route through CacheForge automatically.

If you prefer the OpenClaw-native provider approach (recommended), keep secrets out of `openclaw.json` and set:

```bash
export CACHEFORGE_API_KEY=cf_...
```

## API Contract (current)

This skill uses:
- `POST /api/provision`
- `GET /v1/account/info`
