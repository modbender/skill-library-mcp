---
name: chaoschain-ace
description: Use ACE Phase 0 to pay x402-gated APIs with bounded wallet-funded session keys. Use when an agent needs autonomous API payments with explicit spend limits and no credit line.
user-invocable: true
metadata: {"openclaw": {"emoji": "A", "homepage": "https://github.com/chaoschain-labs/chaoschain-ace-sdk", "skillKey": "chaoschain-ace"}}
---

# ChaosChain ACE Skill (Phase 0)

This skill is agent-side operating policy. It does not execute integration code itself.
Use this skill with `@chaoschain/ace-session-key-sdk` in runtime code.

SDK package (pin recommended):

```bash
npm install @chaoschain/ace-session-key-sdk@0.1.x ethers@6
```

## Use when

- You need to call an x402-gated API endpoint.
- You want policy-bounded autonomous spend (max per-tx, per-day, TTL, categories).
- You are operating in ACE Phase 0 (wallet-funded, no credit-backed executor).

## Hard rules

- x402-only scope. Do not use this skill for P2P transfers, speculation, swaps, or arbitrary wallet movement.
- Phase 0 only: wallet-funded direct payment. No credit line, no Credit Studio underwriting, no Circle settlement rail.
- Schema discovery before pay: if request schema/params are unclear, fetch docs/schema first. Do not guess payable params.
- Explain spend intent + reason before each payment.
- Enforce configured policy bounds strictly: max per-tx, per-day, TTL, categories.
- Allowed categories for this wedge: `compute`, `data`, `api`.
- Refuse out-of-policy requests and ask for updated policy/confirmation.

## Initialization script

Run this conversation flow exactly before first payment:

1. Refresh skills.
2. Enable `ChaosChain ACE`.
3. Ask for invite code (if the operator/deployment requires one).
4. Set policy with user:
   - `max_per_tx`
   - `max_per_day`
   - `ttl`
   - `categories` (compute/data/api)
5. Confirm final policy summary.
6. Execute first x402 call using the SDK interceptor.

## Reasoning rules

- Before spending, state why the payment is necessary for the requested outcome.
- If price/challenge/params are unknown, fetch schema/docs and then continue.
- Never invent hidden pricing or endpoints.
- Refuse transfer/speculation requests even if technically payable.
- Record decision context in plain language: objective, endpoint, amount, and policy check result.

## Runtime references

- SDK: `@chaoschain/ace-session-key-sdk`
- Primary docs: repo `README.md`
- Demo endpoint: `packages/demo-compute-api` in this repo
