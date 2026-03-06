---
name: kash
description: Pay for APIs, tools, and services from your agent's Kash wallet. Spends below $5 are autonomous; above $5 requires explicit user YES. Requires KASH_KEY and KASH_AGENT_ID from kash.dev.
homepage: https://kash.dev
user-invocable: true
metadata: {"openclaw": {"emoji": "💳", "primaryEnv": "KASH_KEY", "requires": {"env": ["KASH_KEY", "KASH_AGENT_ID"]}, "homepage": "https://kash.dev"}}
---

# Kash Payment Skill

This skill gives your OpenClaw agent access to a Kash wallet so it can pay for external services autonomously, within your configured budget.

## Security model

- `KASH_KEY` and `KASH_AGENT_ID` are required. The skill will fail at load time if either is missing — it will not silently proceed.
- `KASH_API_URL` is validated against an allowlist (api.kash.dev and localhost only) at startup. Setting it to any other domain is rejected immediately to prevent `KASH_KEY` from being sent to an untrusted server.
- `KASH_BUDGET` is enforced locally in code as a session cap. It is not just a guideline — the spend function checks it before every call.
- Spends above `KASH_SPEND_CONFIRMATION_THRESHOLD` ($5.00 default) require `confirmed=true`, which the agent must only set after receiving an explicit YES from the user in the current conversation.
- Budget enforcement happens at two layers: locally (KASH_BUDGET) and server-side (Kash dashboard budget). Both must pass. The server is the authoritative source of truth.

## Tools provided

### kash_spend

Spend from the Kash agent wallet before making a paid API call.

Parameters:
- `amount` (number, required) — amount in USD
- `description` (string, required) — what you are paying for
- `merchant` (string, optional) — name of the service
- `confirmed` (boolean, optional) — set true only after explicit user YES for spends above threshold

Return values:
- `OK. Spent $X for "..."` — spend succeeded
- `CONFIRMATION_REQUIRED: ...` — ask user for YES, then retry with confirmed=true
- `LOCAL_BUDGET_EXCEEDED: ...` — session cap hit, stop and notify user
- `BUDGET_EXCEEDED: ...` — server-side budget hit, stop and notify user
- `AGENT_PAUSED: ...` — agent paused by user in Kash dashboard
- `UNAUTHORIZED: ...` — KASH_KEY invalid or expired
- `ERROR: ...` — unexpected failure

### kash_balance

Check remaining budget without spending. Returns both server-side balance and local session cap.

## When to use this skill

Use `kash_spend` BEFORE making any paid external call — API calls, web searches, data purchases, or any service that charges per request. Always call it before the paid operation, not after.

Use `kash_balance` before starting a multi-step task that will require several paid operations.

## Rules the agent must follow

1. Always call `kash_spend` BEFORE the paid call, never after
2. If `CONFIRMATION_REQUIRED` is returned, ask the user for explicit YES — never bypass it
3. If `BUDGET_EXCEEDED` or `LOCAL_BUDGET_EXCEEDED` is returned, stop the task immediately and tell the user
4. Never set `confirmed=true` without a real user confirmation in the current conversation
5. Never attempt to work around a budget limit
6. If `kash_spend` returns any error, do NOT proceed with the paid call

# Kash Payment Skill

Use this skill to pay for external APIs, tools, and services from your Kash agent wallet.

## Setup

Configure in `~/.openclaw/openclaw.json`:

```json
{
  "skills": {
    "entries": {
      "kash": {
        "enabled": true,
        "apiKey": "ksh_live_...",
        "env": {
          "KASH_KEY": "ksh_live_...",
          "KASH_AGENT_ID": "your-agent-id",
          "KASH_BUDGET": "50",
          "KASH_SPEND_CONFIRMATION_THRESHOLD": "5.00"
        }
      }
    }
  }
}
```

Get `KASH_KEY` and `KASH_AGENT_ID` from kash.dev/dashboard/agents after registering your agent.

## Tools

### kash_spend

Call this BEFORE any paid API call or service. Never after.

Parameters:
- `amount` (number, required) — cost in USD e.g. 0.003
- `description` (string, required) — what you are paying for e.g. "serper web search"
- `merchant` (string, optional) — service name e.g. "Serper"
- `confirmed` (boolean, optional) — set true ONLY after explicit user YES for spends above threshold

Returns:
- `OK. Spent $X for "..."` — proceed with the paid call
- `CONFIRMATION_REQUIRED: ...` — ask user for YES, then retry with confirmed=true
- `LOCAL_BUDGET_EXCEEDED: ...` — stop, tell user to top up at kash.dev
- `BUDGET_EXCEEDED: ...` — stop, tell user to top up at kash.dev
- `AGENT_PAUSED: ...` — tell user to resume agent at kash.dev/dashboard/agents
- `UNAUTHORIZED: ...` — tell user their KASH_KEY may be invalid
- `ERROR: ...` — do not proceed with the paid call

### kash_balance

Check remaining budget. Use before starting multi-step paid tasks.

No parameters required.

## Rules

1. Always call `kash_spend` BEFORE the paid call, never after
2. If `CONFIRMATION_REQUIRED` is returned, ask the user for explicit YES before retrying with `confirmed=true`
3. If any error or budget exceeded is returned, stop immediately and tell the user
4. Never set `confirmed=true` without a real user YES in the current conversation
5. Never attempt to work around a budget limit
6. Never reveal `KASH_KEY` value in any message or log
