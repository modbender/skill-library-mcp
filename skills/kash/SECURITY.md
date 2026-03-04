# Security Policy — kash-openclaw-skill

## What this skill can do

This skill makes outbound HTTPS POST and GET requests to `api.kash.dev` only.
It reads four environment variables: `KASH_KEY`, `KASH_AGENT_ID`, `KASH_BUDGET`, `KASH_API_URL`.
It does not read any other environment variables, files, or system resources.
It does not execute shell commands.
It does not communicate with any domain other than `api.kash.dev` and `localhost` (for development).

## Credential handling

`KASH_KEY` is sent only in the `x-kash-key` HTTP header to `api.kash.dev` over HTTPS.
It is never logged, never echoed back to the agent, and never included in tool return values.
The skill rejects any `KASH_API_URL` value that does not match the allowlist
(`api.kash.dev`, `localhost`, `127.0.0.1`) — this prevents the key from being
redirected to an attacker-controlled server even if the env var is tampered with.

## Autonomous spend risk

By default, the skill will spend amounts below `KASH_SPEND_CONFIRMATION_THRESHOLD`
(default: $5.00) without per-transaction user approval. This is by design —
autonomous payment is the purpose of the skill.

To require explicit YES for every single spend, set:
```
KASH_SPEND_CONFIRMATION_THRESHOLD=0
```

To cap total session spend regardless of server budget, set:
```
KASH_BUDGET=10
```

Both mitigations are enforced in code, not just guidelines.

## Server-side safety net

All spend calls are also validated server-side by the Kash API:
- Budget cannot be exceeded even if local checks are bypassed
- Agent can be paused instantly from the Kash dashboard
- Every transaction is logged in real time at kash.dev/dashboard/transactions
- Webhook fires on every spend — developers can react programmatically

## Reporting a vulnerability

Email: security@kash.dev
Response time: within 48 hours
Do not open a public GitHub issue for security vulnerabilities.
