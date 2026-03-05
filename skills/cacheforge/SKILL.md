---
name: cacheforge
version: 1.0.0
description: CacheForge primary skill — bootstrap onboarding + ops + stats for the OpenAI-compatible token optimization gateway. Cut your LLM bill by up to 30% (results vary by provider/workload).
author: CacheForge
license: MIT
homepage: https://app.anvil-ai.io
user-invocable: true
tags:
  - cacheforge
  - ai-agents
  - token-optimization
  - llm
  - cost-reduction
  - openai
  - proxy
  - gateway
  - discord
  - discord-v2
metadata: {"openclaw":{"emoji":"🧠","homepage":"https://app.anvil-ai.io"}}
---

## Purpose

`cacheforge` is the primary entrypoint skill. Install this one skill first.

On first use, it bootstraps companion skills if missing:
- `cacheforge-setup`
- `cacheforge-ops`
- `cacheforge-stats`

Then it routes the user request:
- setup/onboarding -> `cacheforge-setup`
- billing/upstream/keys -> `cacheforge-ops`
- usage/savings dashboard -> `cacheforge-stats`

## CacheForge Positioning

CacheForge is an OpenAI-compatible gateway for agent workflows.
It can reduce wasted spend and improve repeat-turn performance (results vary by provider/workload).

Vault Mode (Pro) is for tool-heavy agents.
Verify results in the CacheForge dashboard.

## Bootstrap Workflow (Required)

Before routing to companion skills, run:

```bash
bash "{baseDir}/scripts/bootstrap-companions.sh"
```

If bootstrap fails because `clawhub` is missing, tell the user to install companions manually:

```bash
for s in cacheforge-setup cacheforge-ops cacheforge-stats; do clawhub install "$s"; done
```

## Routing Rules

Use these routes after bootstrap:

- Setup / first-time onboarding:
  - `python3 "{baseDir}/../cacheforge-setup/setup.py" provision ...`
  - `python3 "{baseDir}/../cacheforge-setup/setup.py" openclaw-apply --set-default`
  - `python3 "{baseDir}/../cacheforge-setup/setup.py" validate`

- Account ops:
  - `python3 "{baseDir}/../cacheforge-ops/ops.py" balance`
  - `python3 "{baseDir}/../cacheforge-ops/ops.py" topup --amount 10 --method stripe`
  - `python3 "{baseDir}/../cacheforge-ops/ops.py" topup --amount 10 --method crypto`
  - `python3 "{baseDir}/../cacheforge-ops/ops.py" upstream ...`
  - `python3 "{baseDir}/../cacheforge-ops/ops.py" keys ...`

- Stats / savings:
  - `python3 "{baseDir}/../cacheforge-stats/dashboard.py" dashboard`
  - `python3 "{baseDir}/../cacheforge-stats/dashboard.py" usage --window 7d`
  - `python3 "{baseDir}/../cacheforge-stats/dashboard.py" breakdown --by model`

## Onboarding Guardrails

Always enforce this order for new users:
1. Register + verify email (if required by deployment).
2. Create tenant API key (`cf_...`).
3. Configure upstream provider (`openrouter`, `anthropic`, or `custom`).
4. Apply OpenClaw provider config (with backup).
5. Top up credits (minimum top-up is typically `$10`).
6. Run a validation request and check dashboard telemetry.

## Public Copy Rules

- Do not use hard numeric savings claims in public-facing output unless linked to a reproducible benchmark.
- Do not reveal Vault internals.
- Keep copy outcome-focused and include "results vary by provider/workload" when relevant.
