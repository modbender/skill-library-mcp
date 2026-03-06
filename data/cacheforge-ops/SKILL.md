---
name: cacheforge-ops
version: 1.0.0
description: CacheForge operations — check balance, top up, manage upstream, API keys. Pay-as-you-go with Stripe or crypto.
author: CacheForge
license: MIT
homepage: https://app.anvil-ai.io
user-invocable: true
tags:
  - cacheforge
  - billing
  - operations
  - ai-agents
  - token-optimization
  - llm
  - api-keys
  - discord
  - discord-v2
metadata: {"openclaw":{"emoji":"💰","homepage":"https://app.anvil-ai.io","primaryEnv":"CACHEFORGE_API_KEY","requires":{"bins":["python3"],"env":["CACHEFORGE_API_KEY"]}}}
---

## When to use this skill

Use this skill when the user wants to:
- Check their CacheForge balance
- Top up credits (Stripe or crypto)
- Enable/configure auto top-up
- View or change upstream provider
- Manage API keys
- Handle 402 Payment Required errors

## Autonomous Billing Protocol

When you encounter a 402 error from CacheForge:
1. Run `ops.py balance` to check current balance
2. If balance is $0 or negative, run `ops.py topup --amount 10` to create a payment link
3. Share the payment URL with the user
4. After payment, retry the original request

## Commands

```bash
# Check balance and billing status
python3 skills/cacheforge-ops/ops.py balance

# Create a top-up payment link ($10 USD)
python3 skills/cacheforge-ops/ops.py topup --amount 10

# Enable auto top-up ($10 when balance drops below $2)
python3 skills/cacheforge-ops/ops.py auto-topup --enable --threshold 200 --amount 1000

# View upstream provider config
python3 skills/cacheforge-ops/ops.py upstream

# Set upstream provider
python3 skills/cacheforge-ops/ops.py upstream --set --kind openrouter --api-key sk-or-...

# List API keys
python3 skills/cacheforge-ops/ops.py keys

# Create a new API key
python3 skills/cacheforge-ops/ops.py keys --create

# View tenant info
python3 skills/cacheforge-ops/ops.py info
```

## Environment Variables

- `CACHEFORGE_BASE_URL` — CacheForge API base (default: https://app.anvil-ai.io)
- `CACHEFORGE_API_KEY` — Your CacheForge API key (required)

## API Contract (current)

This skill uses:
- `GET /v1/account/billing`
- `POST /v1/account/billing/topup`
- `PATCH /v1/account/billing/auto-topup`
- `GET /v1/account/info`
- `GET /v1/account/upstream`, `POST /v1/account/upstream`
- `GET /v1/account/keys`, `POST /v1/account/keys`, `POST /v1/account/keys/{keyID}/revoke`
