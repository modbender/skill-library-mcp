# Maestro Bitcoin Skill

Minimal skill for agents that query Maestro Bitcoin APIs directly using x402.

Published on ClawHub: https://clawhub.ai/Vardominator/maestro-skill

## What This Skill Is

- Direct HTTP usage of Maestro endpoints.
- x402 payment flow with USDC on Ethereum or Base.
- No local wrapper script.

## What Agents Should Do

1. Read endpoint specs from `https://docs.gomaestro.org/bitcoin`.
2. Call endpoints directly.
3. If response is `402`, use `PAYMENT-REQUIRED` to construct/sign payment.
4. Retry with `PAYMENT-SIGNATURE`.
5. Consume API result.

## Required Capability

- Wallet access for USDC payments on Ethereum or Base.
