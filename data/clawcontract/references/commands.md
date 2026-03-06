# ClawContract CLI Commands

## Table of Contents

- [generate](#generate)
- [analyze](#analyze)
- [deploy](#deploy)
- [verify](#verify)
- [full](#full)
- [interact](#interact)
- [list](#list)
- [delete](#delete)

---

## generate

```bash
clawcontract generate "<description>"
```

Creates a Solidity contract from a natural language description and writes it to `./contracts/`.

Override output directory with `--output <dir>`.

Example:

```bash
clawcontract generate "ERC-20 token called VibeToken with 1M supply and burn functionality"
```

---

## analyze

```bash
clawcontract analyze <file>
```

Runs security analysis on a Solidity file using Slither (falls back to regex-based analysis if Python/Slither is unavailable).

Example:

```bash
clawcontract analyze ./contracts/VibeToken.sol
```

---

## deploy

```bash
clawcontract deploy <file> --chain <chain>
```

Compiles and deploys the contract to the specified chain. Shows gas estimation and deploys automatically. `PRIVATE_KEY` must be set in the environment or `.env` — the CLI will error if it is missing.

Supported chains: `bsc-mainnet`, `bsc-testnet`, `opbnb-mainnet`, `opbnb-testnet`.

Default chain: `bsc-testnet`.

Deployment to mainnet chains shows an extra warning message.

Example:

```bash
clawcontract deploy ./contracts/VibeToken.sol --chain bsc-testnet
```

---

## verify

```bash
clawcontract verify <address> --file <file> --chain <chain>
```

Verifies deployed contract source on BscScan or opBNBScan. Requires `BSCSCAN_API_KEY`.

Example:

```bash
clawcontract verify 0xAbC123...def --file ./contracts/VibeToken.sol --chain bsc-testnet
```

---

## full

```bash
clawcontract full "<description>" --chain <chain>
```

Runs the complete pipeline in one command: generate → analyze → deploy → verify.

If high-severity issues are found during analysis, the AI automatically attempts to fix them (up to 3 attempts) before proceeding.

Optional flags:
- `--skip-deploy` — stop after analysis, do not deploy or verify (useful for review before deploying)
- `--skip-fix` — do not auto-fix high-severity issues found during analysis

Example:

```bash
clawcontract full "staking contract for BNB with 10% APY" --chain bsc-testnet
```

---

## interact

```bash
clawcontract interact <address> <function> [args...] --chain <chain> [--value <wei>] [--file <source.sol>]
```

Calls a function on a deployed contract. Read-only functions (`view`/`pure`) execute without gas. State-changing functions execute as signed transactions.

ABI is resolved from stored deployment metadata or from `--file` if provided.

Use `--value <wei>` to send BNB with payable function calls.

Examples:

```bash
clawcontract interact 0xABC... name --chain bsc-testnet
clawcontract interact 0xABC... transfer 0xDEF... 1000 --chain bsc-testnet
clawcontract interact 0xABC... fundTrade 1 --value 100000000000000 --chain bsc-testnet
```

---

## list

```bash
clawcontract list [--chain <chain>] [--json]
```

Lists all stored deployment records. Shows address, contract name, chain, deployer, and deployment date.

Use `--chain <chain>` to filter by a specific chain. Use `--json` for machine-readable output (ABI excluded for brevity).

Examples:

```bash
clawcontract list
clawcontract list --chain bsc-testnet
clawcontract list --json
```

---

## delete

```bash
clawcontract delete <address> [--force]
```

Removes a deployment record from the local store. Shows deployment details and asks for confirmation. Orphaned ABI files are automatically cleaned up. Use `--force` to skip the confirmation prompt.

Examples:

```bash
clawcontract delete 0xABC...def
clawcontract delete 0xABC...def --force
```

---

## Notes

- Default chain is `bsc-testnet` if `--chain` is not specified.
- Generated contracts are written to `./contracts/` by default (override with `--output <dir>`).
- All commands except `delete` are fully non-interactive. `delete` prompts for confirmation unless `--force` is passed.
- Deployment metadata is saved to `.deployments/` in the contracts directory (directory-based store with deduplicated ABIs and fast index). Legacy `.deployments.json` files are auto-migrated.
