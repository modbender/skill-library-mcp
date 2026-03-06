---
name: agent-wallet
description: Self-custodial Bitcoin Lightning wallet for AI agents. Use when the agent needs to send or receive bitcoin payments, check its balance, generate invoices, or manage its wallet. Supports bolt11, bolt12, LNURL, and lightning addresses. Zero config — one command to initialize.
homepage: https://docs.moneydevkit.com/agent-wallet
repository: https://github.com/moneydevkit/mdk-checkout
metadata:
  {
    "openclaw":
      {
        "emoji": "₿",
        "requires": { "bins": ["node", "npx"] },
        "install":
          [
            {
              "id": "agent-wallet-npm",
              "kind": "npm",
              "package": "@moneydevkit/agent-wallet",
              "bins": ["agent-wallet"],
              "label": "Install @moneydevkit/agent-wallet (npm)",
            },
          ],
        "security":
          {
            "secrets": ["~/.mdk-wallet/config.json (BIP39 mnemonic)"],
            "network": ["localhost:3456 (daemon HTTP server)", "MDK Lightning infrastructure via outbound connections"],
            "persistence": ["~/.mdk-wallet/ (config, payment history)"],
            "notes": "The wallet stores a BIP39 mnemonic to disk and runs a local daemon. The mnemonic controls real funds on mainnet. Back it up and restrict file permissions on ~/.mdk-wallet/."
          }
      },
  }
---

# agent-wallet

Self-custodial Lightning wallet for AI agents, built by [MoneyDevKit](https://moneydevkit.com). One command to init. All output is JSON.

**Source:** [@moneydevkit/agent-wallet on npm](https://www.npmjs.com/package/@moneydevkit/agent-wallet) · [GitHub](https://github.com/moneydevkit/mdk-checkout)

## Security & Transparency

This skill runs `@moneydevkit/agent-wallet` — an npm package published by MoneyDevKit. What it does:

- **Generates and stores a BIP39 mnemonic** at `~/.mdk-wallet/config.json` — this IS your private key. Treat it like a password.
- **Runs a local daemon** on `localhost:3456` — HTTP server for wallet operations. Binds to localhost only (not externally accessible).
- **Connects outbound** to MDK's Lightning infrastructure.
- **Persists payment history** to `~/.mdk-wallet/`.

No data is sent to external servers beyond standard Lightning protocol operations. You can verify this by inspecting the [source code](https://github.com/moneydevkit/mdk-checkout) or the published npm tarball.

**Recommended:** Pin a version (`npx @moneydevkit/agent-wallet@0.11.0`) in production.

## Quick Start

```bash
# Initialize wallet (generates mnemonic)
npx @moneydevkit/agent-wallet init

# Get balance
npx @moneydevkit/agent-wallet balance

# Create invoice
npx @moneydevkit/agent-wallet receive 1000

# Pay someone
npx @moneydevkit/agent-wallet send user@getalby.com 500
```

## How It Works

The CLI automatically starts a daemon on first command. The daemon:
- Runs a local HTTP server on `localhost:3456`
- Connects to MDK's Lightning infrastructure
- Polls for incoming payments every 30 seconds
- Persists payment history to `~/.mdk-wallet/`

No webhook endpoint needed — the daemon handles everything locally.

## Setup

### First-time initialization

```bash
npx @moneydevkit/agent-wallet init
```

This command:
1. **Generates a BIP39 mnemonic** — 12-word seed phrase that IS your wallet
2. **Creates config** at `~/.mdk-wallet/config.json`
3. **Derives a walletId** — deterministic 8-char hex ID from your mnemonic
4. **Starts the daemon** — local Lightning node on port 3456

The wallet is ready immediately. No API keys, no signup, no accounts. The agent holds its own keys.

### View existing config

```bash
npx @moneydevkit/agent-wallet init --show
```

Returns `{ "mnemonic": "...", "network": "mainnet", "walletId": "..." }`.

**Note:** `init` will refuse to overwrite an existing wallet. To reinitialize:

```bash
npx @moneydevkit/agent-wallet stop
rm -rf ~/.mdk-wallet  # WARNING: backup mnemonic first!
npx @moneydevkit/agent-wallet init
```

## Commands

All commands return JSON on stdout. Exit 0 on success, 1 on error.

| Command | Description |
|---------|-------------|
| `init` | Generate mnemonic, create config |
| `init --show` | Show config (mnemonic redacted) |
| `start` | Start the daemon |
| `balance` | Get balance in sats |
| `receive <amount>` | Generate invoice |
| `receive` | Generate variable-amount invoice |
| `receive <amount> --description "..."` | Invoice with custom description |
| `receive-bolt12` | Generate a BOLT12 offer (variable amount, reusable) |
| `send <destination> [amount]` | Pay bolt11, bolt12, lnurl, or lightning address |
| `payments` | List payment history |
| `status` | Check if daemon is running |
| `stop` | Stop the daemon |
| `restart` | Restart the daemon |

### Balance

```bash
npx @moneydevkit/agent-wallet balance
```
→ `{ "balance_sats": 3825 }`

### Receive (generate invoice)

```bash
# Fixed amount
npx @moneydevkit/agent-wallet receive 1000

# Variable amount (payer chooses)
npx @moneydevkit/agent-wallet receive

# With description
npx @moneydevkit/agent-wallet receive 1000 --description "payment for service"
```
→ `{ "invoice": "lnbc...", "payment_hash": "...", "expires_at": "..." }`

### Receive BOLT12 Offer

```bash
npx @moneydevkit/agent-wallet receive-bolt12
```
→ `{ "offer": "lno1..." }`

BOLT12 offers are reusable and don't expire — share one offer and receive unlimited payments to it. Unlike BOLT11 invoices, the payer chooses the amount.

### Send

```bash
npx @moneydevkit/agent-wallet send <destination> [amount_sats]
```

Destination auto-detection:
- **bolt11 invoice**: `lnbc10n1...` (amount encoded, no arg needed)
- **bolt12 offer**: `lno1...`
- **lightning address**: `user@example.com`
- **LNURL**: `lnurl1...`

For lightning addresses and LNURL, amount is required:
```bash
npx @moneydevkit/agent-wallet send user@getalby.com 500
```

### Payment History

```bash
npx @moneydevkit/agent-wallet payments
```
→ `{ "payments": [{ "paymentHash": "...", "amountSats": 1000, "direction": "inbound"|"outbound", "timestamp": ..., "destination": "..." }] }`

## Upgrading

```bash
# Stop the running daemon
npx @moneydevkit/agent-wallet stop

# Run with @latest to pull the newest version
npx @moneydevkit/agent-wallet@latest start
```

Your wallet config and payment history in `~/.mdk-wallet/` are preserved across upgrades.

## Usage Notes

- **Denomination**: use ₿ prefix with sats (e.g. ₿1,000 not "1,000 sats")
- **Self-custodial**: the mnemonic IS the wallet. Back it up. Lose it, lose funds.
- **Daemon**: runs a local Lightning node on `:3456`. Auto-starts, persists to disk.
- **Agent-to-agent payments**: any agent with this wallet can pay any other agent's invoice or lightning address.

## What's Next?

**Want to accept payments from customers?** Use the [moneydevkit skill](https://clawhub.ai/satbot-mdk/moneydevkit) to add checkouts to any website. Agent-wallet handles agent-to-agent payments; moneydevkit handles customer-to-agent payments. Together they give your agent full payment superpowers.
