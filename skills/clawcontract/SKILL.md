---
name: clawcontract
description: AI-powered smart contract generator, analyzer, and deployer for BNB Chain (BSC/opBNB). Use when you need to generate Solidity from natural language, run security analysis, compile and deploy contracts, verify source on BscScan/opBNBScan, interact with deployed contracts, or run the full generate→analyze→deploy→verify pipeline. Supports bsc-mainnet, bsc-testnet, opbnb-mainnet, opbnb-testnet.
homepage: https://github.com/cvpfus/clawcontract
metadata: {"openclaw":{"requires":{"bins":["clawcontract"],"env":["CLAWCONTRACT_OPENROUTER_API_KEY","CLAWCONTRACT_PRIVATE_KEY","CLAWCONTRACT_BSCSCAN_API_KEY"]},"install":[{"id":"clawcontract","kind":"node","package":"clawcontract","bins":["clawcontract"],"label":"Install clawcontract (npm)"}]}}
---

# ClawContract

Generate, analyze, deploy, and verify smart contracts on BNB Chain via CLI.

**Source & install:** <https://github.com/cvpfus/clawcontract> — clone the repo, run `pnpm install && pnpm build && npm link`.

## Quick Start

Generate a contract:

    clawcontract generate "escrow contract for peer to peer trades with dispute resolution and timeout auto release"

Full pipeline (generate → analyze → deploy → verify):

    clawcontract full "escrow contract for peer to peer trades with dispute resolution and timeout auto release" --chain bsc-testnet

Deploy an existing contract:

    clawcontract deploy ./contracts/VibeToken.sol --chain bsc-testnet

Interact with a deployed contract:

    clawcontract interact 0xABC... name --chain bsc-testnet

List deployment records:

    clawcontract list
    clawcontract list --chain bsc-testnet

Delete a deployment record:

    clawcontract delete 0xABC...def

## References

- **Full command reference (all flags, examples, notes):** See `{baseDir}/references/commands.md`

## Supported Chains

| Key | Chain | Testnet |
|-----|-------|---------|
| `bsc-mainnet` | BNB Smart Chain | No |
| `bsc-testnet` | BNB Smart Chain Testnet | Yes |
| `opbnb-mainnet` | opBNB | No |
| `opbnb-testnet` | opBNB Testnet | Yes |

Default: `bsc-testnet`.

## Env Vars

Configure via `docker-compose.yml` or set directly in the environment.

| Variable | Required | Purpose |
|----------|----------|---------|
| `CLAWCONTRACT_OPENROUTER_API_KEY` | Yes | AI contract generation |
| `CLAWCONTRACT_PRIVATE_KEY` | For deploy | Wallet for deployment — must be supplied by user |
| `CLAWCONTRACT_BSCSCAN_API_KEY` | For verify | Contract verification on BscScan/opBNBScan |
| `CLAWCONTRACT_OPENROUTER_MODEL` | No | Model override (default: anthropic/claude-sonnet-4-20250514) |

## Artifacts

The CLI writes the following files to disk during normal operation:

| Path | When | Contents |
|------|------|----------|
| `contracts/*.sol` | `generate`, `full` | Generated Solidity source |
| `.deployments/*.json` | `deploy`, `full` | Deployment metadata (address, chain, tx hash) |

## Safety

- **No auto-generated keys.** `CLAWCONTRACT_PRIVATE_KEY` must be explicitly provided by the user via environment variable. The CLI will not generate or persist a private key on its own.
- **Mainnet warning (non-blocking).** Deployment to mainnet chains prints a bold warning about real costs but does **not** block on a prompt — the deploy proceeds automatically. This is by design: the CLI targets agent-driven pipelines where stdin is unavailable. Users control mainnet exposure by choosing `--chain` explicitly (default is `bsc-testnet`).
- **`delete` confirmation prompt.** `delete` is the sole interactive command — it shows deployment details and asks `Remove this deployment? (y/N)`. Use `--force` to skip the prompt (agent-friendly). This is safe because `delete` only removes local metadata; it cannot affect on-chain state.
- **Automatic fix attempts.** During `full`, if high-severity issues are found the AI attempts to fix and re-analyze (up to 3 rounds). This means the agent may modify generated source before deploy. Mitigations:
  - Use `--skip-fix` to disable auto-fix entirely.
  - Use `--skip-deploy` to review the final source and analysis before any on-chain action.
  - Fixes only target the generated file in `contracts/`; no other files are modified.
- **Accidental live-deploy risk.** Because `CLAWCONTRACT_PRIVATE_KEY` is mandatory for deploy and the default chain is `bsc-testnet`, accidental mainnet deploys require the user to **both** set a funded mainnet key **and** explicitly pass `--chain bsc-mainnet` or `--chain opbnb-mainnet`. Neither can happen silently.
- Prefer testnet chains and throwaway keys for initial trials.
