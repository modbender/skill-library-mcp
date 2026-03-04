---
name: elytro-cli
description: >
  TypeScript CLI that initializes Elytro ERC-4337 vaults, manages counterfactual smart accounts, and builds/sends sponsored UserOperations; use whenever an agent must drive Elytro wallets end-to-end.
license: Proprietary
compatibility: Requires Node.js >=24, npm or Bun, git, and network access to Ethereum RPC providers plus Pimlico/Elytro backends.
metadata:
  upstream: https://github.com/Elytro-eth/Elytro-cli
---

# Elytro Smart Account CLI

Skill slug suggestion: `elytro-cli`

## Overview

This skill installs and drives the Elytro ERC‑4337 Smart Account CLI so an agent can initialize a vault, create/activate counterfactual wallets, and build/sent sponsored UserOperations across Ethereum mainnet, Optimism, Arbitrum, and Sepolia testnets. For any agent-facing production workflow, set `ELYTRO_ENV=production` so the CLI talks to the live backend. It wraps the TypeScript CLI stored at `https://github.com/Elytro-eth/Elytro-cli` (replace with the final public repo URL) and exposes runnable commands such as `elytro account create`, `elytro account activate`, and `elytro tx send`.

## Prerequisites

- Node.js ≥ 20 (CLI is built/tested on Node 24 and also works with Bun).
- Git for cloning the public repository.
- Network access to your preferred Ethereum RPC providers and the Pimlico bundler.
- Optional: Bun (if you prefer Bun to run scripts).

## Environment Variables

| Variable                      | Required | Description                                                                                                                            |
| ----------------------------- | -------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| `ELYTRO_ENV`                  | Optional | `production` (default) or `development`, controls GraphQL endpoint. Use `production` for any real user workflow.                       |
| `ELYTRO_PIMLICO_KEY`          | Optional | Pimlico API key. When unset, the CLI automatically falls back to `https://public.pimlico.io/v2/{chainId}/rpc`.                         |
| `ELYTRO_ALCHEMY_KEY`          | Optional | Alchemy project key. When unset, use the overrides below or the built-in public RPCs (best for low-volume dev).                        |
| `ELYTRO_RPC_URL_<CHAIN_ID>`   | Optional | Full JSON-RPC URL override per chain ID (e.g. `ELYTRO_RPC_URL_1=https://mainnet.infura.io/v3/...`).                                    |
| `ELYTRO_RPC_URL_<CHAIN_SLUG>` | Optional | Override per slug (slug derived from Alchemy network name: `ETH_MAINNET`, `ETH_SEPOLIA`, `OPT_MAINNET`, `OPT_SEPOLIA`, `ARB_MAINNET`). |

Copy `.env.example` to `.env` (or `.env.production`) and fill in secrets, or export the variables directly before running commands.

## Installation Steps

```bash
git clone https://github.com/Elytro-eth/Elytro-cli.git
cd elytro-cli
npm install
# optionally: npm run build && npm link (for a global `elytro` command)
```

For Bun users:

```bash
git clone https://github.com/Elytro-eth/Elytro-cli.git
cd elytro-cli
bun install
```

## Command Reference

All commands run via `npm run dev -- <command>` during development, or `node dist/index.js <command>` after building. Examples:

### Bootstrap the vault

```bash
npm run dev -- init
```

Creates `~/.elytro/.device-key` and encrypted `keyring.json`. Must be run once per machine.

### Create a counterfactual account

```bash
npm run dev -- account create --chain 11155111 --alias test-wallet
```

Registers the account with Elytro backend so sponsorships are allowed. Supports chain IDs 1 (Ethereum), 10 (Optimism), 42161 (Arbitrum), 11155111 (Sepolia), 11155420 (Optimism Sepolia) by default; additional chains can be added via `account add`.

### Activate (deploy) an account

```bash
npm run dev -- account activate --account test-wallet
```

Builds a deploy UserOperation, requests Pimlico gas pricing and sponsorship, signs with the device key, submits to the bundler, and prints the tx hash/explorer link.

### Send a transaction

```bash
npm run dev -- tx send --to 0xabc... --value 0.01 --chain 11155111 --account test-wallet
```

Supports ETH transfers, ERC‑20 transfers via `--token <symbol>` / `--amount`, and arbitrary calldata via `--data`. Use `tx simulate` first to verify sponsorship + balances without broadcasting.

### Build UserOperation JSON

```bash
npm run dev -- tx build --to 0xabc... --value 0.01 --account test-wallet --chain 10
```

Outputs the unsigned UserOp JSON for offline review or `tx send --userop`.

## Skill Workflow

1. **Install dependencies** using Node or Bun.
2. **Configure env vars** (`.env.example` or exported). At minimum set `ELYTRO_ENV`, `ELYTRO_PIMLICO_KEY`, and either `ELYTRO_ALCHEMY_KEY` or custom `ELYTRO_RPC_URL_*` values (Infura, QuickNode, etc.). Without keys the CLI uses public RPCs/bundlers with lower rate limits.
3. **Initialize the vault** (`elytro init`). This generates device key + encrypted keyring under `~/.elytro/`.
4. **Create and activate accounts** per chain. Use `account list`, `account info`, and `account switch` to manage multiples.
5. **Build/simulate/send transactions** via `elytro tx …` commands.
6. **Backup** `~/.elytro/` if needed; never commit those files.

## Testing & Verification

- Run `npm run dev -- account list` to confirm the CLI boots and reads the device key.
- Use Sepolia or Optimism Sepolia for smoke tests (`ELYTRO_ENV=development`, `ELYTRO_RPC_URL_11155111=…`).
- `npm run test` executes the smoke test harness (if provided) with `.env.test`.

## Packaging Notes

- Do not upload `node_modules/` or `dist/`; Clawhub agents will install dependencies on demand.
- Include this `SKILL.md`, `AGENT_SKILLS.md`, and any helper scripts (`install.sh`, `run-account.sh`) in the upload folder.
- Ensure `.env.example` keeps placeholder values only.
