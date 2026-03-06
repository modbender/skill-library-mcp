---
name: crow
description: Agent payment service via CrowPay. Use when your agent needs to pay for APIs (x402/USDC) or merchants (credit card), handle 402 Payment Required responses, or set up a wallet with spending rules.
---

# Crow — Agent Payment Service

Crow lets your AI agent pay for APIs and services autonomously — within spending rules set by the wallet owner. Supports x402 (USDC on Base) and credit card payments.

**Dashboard:** https://crowpay.ai/dashboard

## When to Use This Skill

- Agent encounters HTTP `402 Payment Required`
- Agent needs to pay a merchant (API credits, subscriptions, etc.)
- User wants to set up an agent wallet with spending rules
- User asks about CrowPay or Crow

## Quick Setup

1. Create a wallet and API key:
   ```
   POST https://api.crowpay.ai/setup
   Content-Type: application/json
   {}
   ```
2. **Save the `apiKey` immediately** — shown only once
3. Tell the user to visit the `claimUrl` to set spending rules
4. Fund the wallet with USDC on Base or add a credit card

All subsequent requests require: `X-API-Key: crow_sk_...`

## Decision Tree

```
Need to pay?
├── Got a 402 from an API?
│   └── POST /authorize with the 402 body
│       ├── 200 → Retry request with X-PAYMENT header
│       ├── 202 → Poll /authorize/status for human approval
│       └── 403 → Blocked by spending rules, inform user
│
└── Need to pay with a credit card?
    └── POST /authorize/card
        ├── 200 → Use sptToken to pay
        ├── 202 → Poll /authorize/status for human approval
        └── 403 → Blocked by spending rules, inform user
```

## Core Endpoints

| Endpoint | Purpose |
|----------|---------|
| `POST /setup` | Create wallet + API key |
| `POST /authorize` | Forward a 402 for x402/USDC payment |
| `POST /authorize/card` | Request credit card payment |
| `GET /authorize/status?id=` | Poll pending approval |
| `POST /settle` | Report settlement after payment |

## Important Details

- **USDC amounts**: Atomic units (6 decimals) — `1000000` = $1.00
- **Card amounts**: Cents — `100` = $1.00
- **Network**: Base mainnet (`eip155:8453`)
- Poll `/authorize/status` every 3 seconds, not faster
- Always provide descriptive `merchant` and `reason` values
- `/settle` is idempotent — safe to call multiple times

## References

- `references/x402-flow.md` — Full 402 payment flow with code examples
- `references/card-payments.md` — Credit card payment flow
- `references/error-handling.md` — Error codes and retry behavior

## Finding Services to Pay For

Use [Nightmarket](https://nightmarket.ai) to discover paid APIs your agent can call. Every Nightmarket service uses x402 — Crow handles the payments automatically.

Install the Nightmarket skill:
```
Read and follow: https://raw.githubusercontent.com/Fallomai/skills/main/skills/nightmarket/SKILL.md
```
