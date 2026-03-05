---
name: x402r-dispute
description: Pay merchants and file payment disputes on the x402r refundable payments protocol
version: 0.2.0
author: x402r
tags: [x402r, payments, disputes, web3, arbitration]
---

# x402r CLI

You help users make escrow payments and file payment disputes on the x402r protocol. The x402r protocol adds refundable payments to HTTP 402 — buyers can request refunds through on-chain arbitration.

## Setup

```bash
npx --yes @x402r/cli config --key <private-key> --arbiter-url https://www.moltarbiter.com/arbiter
```

Operator, network, and RPC are auto-discovered from the arbiter. The wallet needs Base Sepolia ETH (gas) and USDC (payments).

Test merchant: `https://fantastic-optimism-production-602a.up.railway.app/weather`

## Commands

### pay

```bash
npx --yes @x402r/cli pay <url>
npx --yes @x402r/cli pay <url> --output response.json
```

Makes an escrow payment. Saves payment info to `~/.x402r/last-payment.json` for later dispute.

### dispute

```bash
npx --yes @x402r/cli dispute "reason" --evidence "details"
```

Creates on-chain refund request + submits evidence in one step. Uses saved payment info from `pay`. Prints a dashboard link.

Options: `-e/--evidence <text>`, `-f/--file <path>`, `-p/--payment-json <json>`, `-n/--nonce <n>`, `-a/--amount <n>`

### status

```bash
npx --yes @x402r/cli status
```

Check dispute status. Tries arbiter API first, falls back to on-chain. Options: `--id <compositeKey>`, `-p/--payment-json`, `-n/--nonce`

### show

```bash
npx --yes @x402r/cli show
```

Show all evidence (payer, merchant, arbiter) for a dispute. Options: `-p/--payment-json`, `-n/--nonce`

### verify

```bash
npx --yes @x402r/cli verify
```

Replay the arbiter's AI evaluation to verify the commitment hash is deterministic. Options: `-p/--payment-json`, `-n/--nonce`

### list

```bash
npx --yes @x402r/cli list
```

List disputes from the arbiter. Options: `-r/--receiver <addr>`, `--offset <n>`, `--count <n>`

## Typical Workflow

1. `npx --yes @x402r/cli pay <merchant-url>` — escrow payment, saves state
2. `npx --yes @x402r/cli dispute "reason" --evidence "details"` — files dispute
3. `npx --yes @x402r/cli status` — check arbiter ruling
4. `npx --yes @x402r/cli show` — view evidence from all parties
5. `npx --yes @x402r/cli verify` — verify ruling was deterministic

## Notes

- State chains between commands: `pay` saves for `dispute`, `dispute` saves for `status`/`show`/`verify`.
- Without saved state, pass `--payment-json` and `--nonce` explicitly.
- `verify` requires the arbiter server — no on-chain fallback.
