---
name: goldenclaw
description: Manage GoldenClaw (GCLAW) on Solana. Create wallet, claim from faucet, check balance, send tokens, view history. For OpenClaw AI agents.
license: MIT
metadata:
  version: 1.1.0
  commands: gclaw
  author: AgentCrypto
---

# GoldenClaw (GCLAW) Skill

Solana SPL token skill for [OpenClaw](https://openclaw.ai): wallet, faucet claims, and agent-to-agent transfers in GCLAW.

## Installation

1. Extract the skill to your `skills/` folder
2. Run `npm run build` in the skill directory (dependencies are installed automatically when the skill runs if missing)

## Commands

- `gclaw setup` – Create encrypted wallet
- `gclaw claim` – Claim GCLAW from faucet (goldenclaw.org)
- `gclaw balance` – GCLAW and SOL balance
- `gclaw address` – Your wallet address
- `gclaw send <amount> <address>` – Send GCLAW to another agent
- `gclaw donate <SOL>` – Donate SOL to main wallet (treasury)
- `gclaw history` – Transaction history
- `gclaw limits` – Spending limits
- `gclaw tokenomics` – Distribution stats

## Links

- Faucet: https://goldenclaw.org
- Website: https://goldenclaw.org
- X: https://x.com/GClaw68175
- Token: [Solscan](https://solscan.io/token/8fUqKCgQ2PHcYRnce9EPCeMKSaxd14t7323qbXnSJr4z)
