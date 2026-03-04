---
name: sequence-builder
description: "Manage Sequence smart wallets, projects, API keys, ERC20 transfers, and query blockchain data using the Sequence Builder CLI. Use when user asks about creating wallets, sending tokens, checking balances, managing Sequence projects, or interacting with EVM blockchains."
homepage: https://github.com/0xsequence/builder-cli
metadata:
  clawdbot:
    emoji: "⛓️"
    os:
      - darwin
      - linux
    requires:
      bins:
        - node
        - npx
---

# Sequence Builder CLI

CLI for Sequence Builder — designed for AI agents and automation. Create wallets, authenticate, manage projects, query blockchain data, and send ERC20 transfers from the command line.

All commands support `--json` for machine-readable output. Always use `--json` when parsing results programmatically.

## Prerequisites

- Node.js 18+
- A Sequence Builder account (created automatically on first login)

## Quick Start

```bash
# 1. Create a wallet
npx @0xsequence/builder-cli create-wallet --json

# 2. Login with the private key from step 1
npx @0xsequence/builder-cli login -k <private-key> --json

# 3. Create a project and get an access key
npx @0xsequence/builder-cli projects create "My Project" --json

# 4. Get wallet addresses (EOA + Sequence smart wallet)
npx @0xsequence/builder-cli wallet-info -k <private-key> -a <access-key> --json

# 5. Fund the Sequence wallet via the Trails link from step 4

# 6. Send an ERC20 transfer
npx @0xsequence/builder-cli transfer \
  -k <private-key> -a <access-key> \
  -t <token-address> -r <recipient> \
  -m <amount> -c <chain-id> --json
```

## Encrypted Key Storage

Set `SEQUENCE_PASSPHRASE` to auto-encrypt and store the private key locally. Once stored, you no longer need to pass `-k` on every command.

```bash
export SEQUENCE_PASSPHRASE="your-strong-secret"
npx @0xsequence/builder-cli create-wallet --json
# Private key is now encrypted in ~/.sequence-builder/config.json
# All subsequent commands will use the stored key automatically
```

## Understanding Wallet Addresses

This CLI uses **Sequence Smart Wallets** for transfers:

- **EOA Address** — Standard Ethereum address from your private key. Used for login and project ownership.
- **Sequence Wallet Address** — Smart contract wallet that can pay gas fees with ERC20 tokens (no native token needed). Used for transfers.

**Always send tokens to the Sequence Wallet Address** for use with the `transfer` command. Use `wallet-info` to see both addresses.

## Command Reference

### create-wallet

Generate a new EOA keypair.

```bash
npx @0xsequence/builder-cli create-wallet --json
```

JSON output:
```json
{
  "privateKey": "0x4c0883a...",
  "address": "0x89D9F8f...",
  "keyStored": true
}
```

### wallet-info

Show EOA and Sequence smart wallet addresses.

```bash
npx @0xsequence/builder-cli wallet-info -k <private-key> -a <access-key> --json
```

Options:
- `-k, --private-key <key>` — Wallet private key (optional if stored)
- `-a, --access-key <key>` — Project access key (required)

JSON output:
```json
{
  "eoaAddress": "0x742BDb3...",
  "sequenceWalletAddress": "0xA71506...",
  "fundingUrl": "https://demo.trails.build/..."
}
```

### login

Authenticate with Sequence Builder.

```bash
npx @0xsequence/builder-cli login -k <private-key> --json
```

Options:
- `-k, --private-key <key>` — Wallet private key (optional if stored)
- `-e, --email <email>` — Email to associate with the account
- `--env <environment>` — Environment: `prod` (default) or `dev`
- `--api-url <url>` — Custom API URL

JSON output:
```json
{
  "success": true,
  "address": "0x742BDb3...",
  "expiresAt": "2026-02-07T12:00:00Z"
}
```

### projects

Manage Sequence Builder projects. Requires login.

```bash
# List all projects
npx @0xsequence/builder-cli projects --json

# Create a new project
npx @0xsequence/builder-cli projects create "My Game" --json

# Create with specific chains
npx @0xsequence/builder-cli projects create "My Game" --chain-ids 137,8453 --json

# Get project details
npx @0xsequence/builder-cli projects get <project-id> --json
```

### apikeys

Manage API keys for a project. Requires login.

```bash
# List all API keys
npx @0xsequence/builder-cli apikeys <project-id> --json

# Get the default API key
npx @0xsequence/builder-cli apikeys default <project-id> --json
```

### transfer

Send an ERC20 token transfer using the Sequence smart wallet. Gas fees are paid with the same token being transferred — no native token needed.

```bash
npx @0xsequence/builder-cli transfer \
  -k <private-key> \
  -a <access-key> \
  -t <token-address> \
  -r <recipient-address> \
  -m <amount> \
  -c <chain-id> \
  --json
```

Options:
- `-k, --private-key <key>` — Wallet private key (optional if stored)
- `-a, --access-key <key>` — Project access key (required)
- `-t, --token <address>` — ERC20 token contract address (required)
- `-r, --recipient <address>` — Recipient address (required)
- `-m, --amount <amount>` — Amount in token units, e.g. `10.5` (required)
- `-c, --chain-id <chainId>` — Chain ID (required)

JSON output:
```json
{
  "success": true,
  "transactionHash": "0xabc123...",
  "from": "0xA71506...",
  "to": "0x123456...",
  "token": "0x833589...",
  "amount": "10.5",
  "symbol": "USDC",
  "chainId": 8453
}
```

### indexer

Query blockchain data using the Sequence Indexer.

```bash
# Get token balances
npx @0xsequence/builder-cli indexer balances <address> \
  -a <access-key> -c <chain-id> --include-metadata --json

# Get native token balance (ETH, MATIC, etc.)
npx @0xsequence/builder-cli indexer native-balance <address> \
  -a <access-key> -c <chain-id> --json

# Get transaction history
npx @0xsequence/builder-cli indexer history <address> \
  -a <access-key> -c <chain-id> --limit 20 --json

# Get token contract info
npx @0xsequence/builder-cli indexer token-info <contract-address> \
  -a <access-key> -c <chain-id> --json
```

## Supported Networks

| Network | Chain ID |
|---------|----------|
| Ethereum | 1 |
| Polygon | 137 |
| Base | 8453 |
| Arbitrum | 42161 |
| Optimism | 10 |
| BSC | 56 |
| Avalanche | 43114 |

Full list: https://status.sequence.info/

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General error |
| 10 | Not logged in |
| 11 | Invalid private key |
| 20 | Insufficient funds |
| 30 | No projects found |
| 31 | Project not found |
| 40 | API error |

## Common Workflows

### Full setup from scratch

```bash
export SEQUENCE_PASSPHRASE="my-secret"
npx @0xsequence/builder-cli create-wallet --json
# Save the output — privateKey and address
npx @0xsequence/builder-cli login --json
npx @0xsequence/builder-cli projects create "My App" --json
# Note the accessKey from the output
npx @0xsequence/builder-cli wallet-info -a <access-key> --json
# Fund the sequenceWalletAddress via the fundingUrl
```

### Check balance then transfer

```bash
# Check balance first
npx @0xsequence/builder-cli indexer balances <your-sequence-wallet> \
  -a <access-key> -c 8453 --json

# Send transfer
npx @0xsequence/builder-cli transfer \
  -a <access-key> -t <token> -r <recipient> -m 10 -c 8453 --json
```

### Multi-chain balance check

```bash
# Check across multiple chains
npx @0xsequence/builder-cli indexer balances <address> -a <key> -c 1 --json
npx @0xsequence/builder-cli indexer balances <address> -a <key> -c 137 --json
npx @0xsequence/builder-cli indexer balances <address> -a <key> -c 8453 --json
```

## Configuration

Stored in `~/.sequence-builder/config.json`:
- JWT token for authentication
- Environment settings (prod/dev)
- Encrypted private key (when `SEQUENCE_PASSPHRASE` is set)

## Troubleshooting

**"Not logged in" error:** Run `login` first. JWT tokens expire — re-run login if expired.

**"Invalid private key" error:** Key must be a 64-character hex string (with or without `0x` prefix). If using stored key, verify `SEQUENCE_PASSPHRASE` is correct.

**"Insufficient balance" error:** Send tokens to the **Sequence Wallet Address** (not the EOA). Use `wallet-info` to get the correct address.

**Transfer fails:** Ensure the Sequence wallet has enough of the token being transferred. The same token is used to pay gas fees.
