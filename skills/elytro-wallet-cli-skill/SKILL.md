---
name: elytro-cli-usage
description: >
  How to operate the Elytro CLI — an ERC-4337 smart account wallet for developers.
  Covers the full happy-path lifecycle: wallet initialization, account creation/activation,
  transaction building/sending/simulating, on-chain queries, security hooks (2FA),
  and configuration management. Use this skill whenever you need to interact with
  Elytro smart accounts from the command line, manage ERC-4337 UserOperations,
  query balances or token holdings, send ETH or call contracts via UserOps, or set up
  2FA security hooks. Also use it when working with the `elytro` CLI binary,
  or any task involving smart account wallets on Ethereum, Optimism, Arbitrum, or
  their testnets.
---

# Elytro CLI Usage Guide

This document teaches an AI agent how to operate the Elytro CLI — a command-line tool
for managing ERC-4337 smart account wallets. Published as `@elytro/cli` on npm.

The target audience is an autonomous agent (e.g. OpenClaw) that needs to drive the CLI
end-to-end without human hand-holding. Every command, flag, and output format is
documented here so the agent can plan multi-step workflows and parse structured output.

---

## Installation

```bash
npm install -g @elytro/cli
```

This installs the `elytro` binary globally. Verify with:

```bash
elytro --version
```

Requires **Node.js 24+** (`node -v` to check).

After installation, all commands are invoked as:

```bash
elytro [command] [subcommand] [options]
```

### Environment Variables

| Variable             | Purpose                              | When Required                          |
|----------------------|--------------------------------------|----------------------------------------|
| `ELYTRO_ALCHEMY_KEY` | Alchemy RPC — higher rate limits     | Optional (public RPC used if absent)   |
| `ELYTRO_PIMLICO_KEY` | Pimlico bundler/paymaster            | Optional (public bundler if absent)    |
| `ELYTRO_ENV`         | `development` or `production` (default) | Optional                            |

Public endpoints work out of the box for basic usage. Set keys via
`elytro config set alchemy-key <KEY>` / `elytro config set pimlico-key <KEY>` for
production reliability.

---

## Wallet Lifecycle (Happy Path)

A typical first-time flow looks like this:

```
init → account create → (fund the address) → account activate → tx send / query
```

Each step depends on the previous one. The sections below walk through every command
in the order you would use them.

---

## 1. Initialize the Wallet

```bash
elytro init
```

Creates a 256-bit device key at `~/.elytro/.device-key` (chmod 600) and generates
an EOA signing key encrypted in `~/.elytro/keyring.json`. No password is needed —
the device key on disk is the access control.

**Idempotent**: running `init` twice prints "Wallet already initialized" and exits
cleanly (exit code 0).

**What happens internally**: device key → encrypt EOA private key → write vault to
disk. On every subsequent CLI invocation the device key is loaded automatically and
the keyring is unlocked in memory.

---

## 2. Account Management

### Create an Account

```bash
elytro account create --chain <chainId> [--alias <name>]
```

- `--chain` (required): numeric chain ID. Supported chains:
  - `1` — Ethereum mainnet
  - `10` — Optimism
  - `42161` — Arbitrum One
  - `11155111` — Sepolia (testnet)
  - `11155420` — Optimism Sepolia (testnet)
- `--alias` (optional): human-readable name like `"my-test"`. If omitted, a random
  two-word alias is generated (e.g. `"swift-panda"`).

The command computes a **counterfactual address** via CREATE2 (the contract is not
deployed yet) and registers the account with the Elytro backend for sponsorship
eligibility. The same owner can have multiple accounts on the same chain (each gets
a unique index).

**Output**: alias, contract address, chain name, deployment status.

### List Accounts

```bash
elytro account list                    # all accounts
elytro account list [alias|address]    # single account lookup
elytro account list --chain <chainId>  # filter by chain
```

Prints a table with columns: active marker (`→`), alias, full address (42 chars),
chain name, deployed status, recovery status.

### Account Info (On-Chain)

```bash
elytro account info [alias|address]
```

Fetches live on-chain data: balance, deployment status, recovery status, block
explorer link. Defaults to the current account if no argument is given.

**Requires RPC access** — will fail if the node is unreachable.

### Switch Active Account

```bash
elytro account switch [alias|address]
```

Changes which account is "current" for subsequent commands. If no argument is given,
an interactive selector is shown (not suitable for non-interactive agents — always
pass the alias or address).

After switching, the SDK and wallet client are re-initialized to the new account's
chain. The command also fetches and displays the new account's balance and status.

### Activate (Deploy On-Chain)

```bash
elytro account activate [alias|address] [--no-sponsor]
```

Deploys the smart contract wallet on-chain via a UserOperation. This is an actual
on-chain transaction — the address must have ETH (or sponsorship must succeed) to
pay for gas.

Steps: build deploy UserOp → estimate gas (with fakeBalance) → request sponsorship
→ sign → send to bundler → wait for receipt → mark deployed locally.

`--no-sponsor` forces the account to self-pay gas (skips paymaster).

**Important**: The account address is funded *before* activation. The address is
deterministic (CREATE2), so you can send ETH to it even though the contract doesn't
exist yet.

---

## 3. Transactions

All transaction commands use the unified `--tx` flag:

```
--tx "to:0xAddress,value:0.1,data:0xAbcDef"
```

Rules:
- `to` is always required (valid Ethereum address).
- At least one of `value` or `data` must be present.
- `value` is in human-readable ETH (e.g. `"0.001"`, not wei).
- `data` is hex-encoded calldata starting with `0x`, must be even length.
- Multiple `--tx` flags create a **batch** (packed into `executeBatch`).
- Order is preserved.

### Send a Transaction

```bash
# ETH transfer
elytro tx send --tx "to:0xRecipient,value:0.001"

# Contract call
elytro tx send --tx "to:0xContract,data:0xa9059cbb..."

# Batch (two operations in one UserOp)
elytro tx send --tx "to:0xA,value:0.1" --tx "to:0xB,data:0xab"

# From a specific account
elytro tx send my-alias --tx "to:0xAddr,value:0.01"

# Skip sponsorship
elytro tx send --tx "to:0xAddr,value:0.01" --no-sponsor

# Skip SecurityHook 2FA
elytro tx send --tx "to:0xAddr,value:0.01" --no-hook

# Send a pre-built UserOp
elytro tx send --userop '{"sender":"0x...","callData":"0x...",...}'
```

The send pipeline: resolve account → balance pre-check → build UserOp via SDK →
fee data → estimate gas (fakeBalance: true) → sponsor → confirmation prompt → sign
→ send to bundler → wait for receipt.

**Output includes**: tx hash, block number, gas cost, sponsor status, explorer link.

**Exit codes**: 0 on success, 1 on any error or if execution reverted.

### Build (Unsigned UserOp)

```bash
elytro tx build --tx "to:0xAddr,value:0.1"
```

Same pipeline as `send` but stops before signing. Outputs the full UserOp as JSON
(with bigints serialized as hex strings). Useful for inspection or piping into
`tx send --userop`.

### Simulate

```bash
elytro tx simulate --tx "to:0xAddr,value:0.1"
```

Dry-run that shows: transaction type, gas breakdown (callGasLimit,
verificationGasLimit, preVerificationGas), max gas cost in ETH, sponsor status,
current balance, and warnings if balance is insufficient. Does not sign or send.

For contract calls, also checks whether the target address has deployed code.

---

## 4. Queries

All query commands output structured JSON: `{ "success": true, "result": {...} }`
on success, or `{ "success": false, "error": { "code": ..., "message": ... } }` on
failure. Error codes follow JSON-RPC conventions.

### Balance

```bash
# Native ETH balance
elytro query balance [alias|address]

# ERC-20 token balance
elytro query balance [alias|address] --token 0xTokenAddress
```

### Token Holdings

```bash
elytro query tokens [alias|address]
```

Uses Alchemy's `alchemy_getTokenBalances` RPC to list all ERC-20 tokens held by
the account, with symbol, decimals, and formatted balance. Requires an Alchemy key
for best results (public RPC may not support this method).

### Transaction Receipt

```bash
elytro query tx <hash>
```

Looks up a transaction by hash on the current account's chain. Returns status,
block number, from, to, gas used. Note: if the tx is on a different chain, it won't
be found — there's no cross-chain lookup yet.

### Chain Info

```bash
elytro query chain
```

Shows current chain ID, name, block number, gas price, RPC endpoint (with API keys
masked), bundler URL, and block explorer.

### Address Inspection

```bash
elytro query address <0xAddress>
```

Checks any address: reports whether it's an EOA or contract, its ETH balance, and
(if contract) the code size in bytes.

---

## 5. Security (2FA & Spending Limits)

The SecurityHook is an on-chain module that adds 2FA (email OTP) and daily spending
limits to accounts. All security commands require the account to be deployed.

### Status

```bash
elytro security status
```

Shows: hook installed (yes/no), hook address, capabilities (UserOp validation,
signature validation), force-uninstall state, email binding, daily spending limit.

### Install 2FA

```bash
elytro security 2fa install [--capability <1|2|3>]
```

Capabilities: 1 = signature only, 2 = UserOp only, 3 = both (default).

### Uninstall 2FA

```bash
# Normal uninstall (requires hook authorization / OTP)
elytro security 2fa uninstall

# Force uninstall — start countdown (bypass hook)
elytro security 2fa uninstall --force

# Execute force uninstall after safety delay
elytro security 2fa uninstall --force --execute
```

### Email Management

```bash
# Bind email for OTP delivery
elytro security email bind user@example.com

# Change bound email
elytro security email change newemail@example.com
```

Both require OTP verification (code sent to the email).

### Spending Limit

```bash
# View current limit
elytro security spending-limit

# Set daily limit (in USD)
elytro security spending-limit 100
```

Setting a limit requires OTP verification.

---

## 6. Configuration

```bash
# Show current config (endpoints, keys, chain)
elytro config show

# Set an API key
elytro config set alchemy-key YOUR_KEY
elytro config set pimlico-key YOUR_KEY

# Remove a key (revert to public endpoint)
elytro config remove alchemy-key
```

---

## Structured Output Parsing

For **tx** and **query** commands, all output follows this shape:

```json
// Success
{ "success": true, "result": { "account": "swift-panda", "balance": "0.1", ... } }

// Error
{ "success": false, "error": { "code": -32001, "message": "Insufficient balance", "data": { ... } } }
```

An agent can parse stdout as JSON to determine success/failure programmatically.
Non-JSON output (headings, spinners, info lines) goes to stderr.

The `account` commands use human-readable display output (not JSON), but the alias
and address are always shown.

---

## Multi-Step Workflow Examples

### Example 1: Fresh Setup + Send ETH on OP Sepolia

```bash
elytro init
elytro account create --chain 11155420 --alias test-1
# → Note the address, fund it with testnet ETH from a faucet
elytro account activate test-1
elytro tx send --tx "to:0xRecipientAddress,value:0.001"
```

### Example 2: Query All Token Balances

```bash
elytro config set alchemy-key YOUR_KEY
elytro query tokens test-1
```

### Example 3: Batch Transaction

```bash
elytro tx send \
  --tx "to:0xAlice,value:0.01" \
  --tx "to:0xBob,value:0.02" \
  --tx "to:0xContract,data:0xa9059cbb000000000000000000000000..."
```

All three operations are packed into a single UserOp (executeBatch) and executed
atomically.

### Example 4: Simulate Before Sending

```bash
elytro tx simulate --tx "to:0xAddr,value:0.5"
# Check the output: gas cost, sponsor status, balance warnings
# If everything looks good:
elytro tx send --tx "to:0xAddr,value:0.5"
```

### Example 5: Install 2FA and Set Spending Limit

```bash
elytro security 2fa install
elytro security email bind agent@example.com
# Enter OTP from email
elytro security spending-limit 50
# Enter OTP to confirm
elytro security status
```

---

## Storage Layout

All state lives in `~/.elytro/`:

```
~/.elytro/
├── .device-key       # 32-byte binary, chmod 600
├── keyring.json      # AES-GCM encrypted EOA private key vault
├── accounts.json     # Account list (alias, address, chainId, index, owner, deployed)
├── config.json       # Chain config, current chain, API endpoints
└── user-keys.json    # User-provided API keys (alchemy, pimlico)
```

Deleting `~/.elytro/` resets everything. The on-chain contracts are unaffected — you
would just lose local key material and need to re-import or re-initialize.

---

## Supported Chains

| Chain ID   | Name              | Network    |
|------------|-------------------|------------|
| 1          | Ethereum          | Mainnet    |
| 10         | Optimism          | Mainnet    |
| 42161      | Arbitrum One      | Mainnet    |
| 11155111   | Sepolia           | Testnet    |
| 11155420   | Optimism Sepolia  | Testnet    |

Default chain (when no account is selected): Optimism Sepolia (11155420).

---

## Key Invariants for Agents

1. **Always `init` before anything else.** Every other command needs a device key.
2. **Always `account create` before `activate` or `tx`.** There must be a local account record.
3. **Always `activate` before `tx send`.** Transactions require a deployed contract.
4. **Fund the address before `activate` if sponsorship might fail.** The CREATE2 address is deterministic — send ETH to it pre-deployment.
5. **Sponsor covers gas, not value.** If sending ETH, the account needs that ETH.
6. **Chain is per-account.** Switching accounts may change the active chain. All chain-sensitive operations auto-initialize to the account's chain.
7. **Interactive prompts exist in `tx send` (confirmation) and security commands (OTP).** For fully non-interactive usage, the agent would need to handle stdin or use `tx build` + external signing.
8. **Parse JSON output from `query` and `tx` commands.** Success/failure is in the `success` field; error details are in `error.code` and `error.message`.
