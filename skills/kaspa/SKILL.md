---
name: kaspa-wallet
description: >
  Simple wallet for Kaspa blockchain. Send KAS, check balances, generate payment URIs.
  Self-custody CLI wallet with JSON output for automation.
keywords:
  - kaspa
  - kas
  - wallet
  - payments
  - transfer
  - balance
  - cryptocurrency
  - blockdag
allowed-tools:
  - Bash
  - Read
  - Write
  - Glob
  - Grep
  - Task
user-invocable: true
---

# Kaspa Wallet Skill

Simple self-custody wallet for Kaspa blockchain.

## Overview

```
┌─────────────────────────────────────────────────────────┐
│                     KASPA WALLET                        │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐ │
│  │   Balance   │  │    Send     │  │  Payment URIs   │ │
│  │   Check     │  │    KAS      │  │   Generator     │ │
│  └─────────────┘  └─────────────┘  └─────────────────┘ │
│           │                │                   │        │
│           └────────────────┴───────────────────┘        │
│                         │                               │
│              ┌──────────▼──────────┐                    │
│              │   Kaspa Python SDK  │                    │
│              │   (wRPC Client)     │                    │
│              └─────────────────────┘                    │
│                         │                               │
│         ┌───────────────┼───────────────┐               │
│         ▼               ▼               ▼               │
│    ┌─────────┐    ┌──────────┐    ┌──────────┐         │
│    │ Mainnet │    │ Testnet  │    │  Custom  │         │
│    │  wRPC   │    │   wRPC   │    │   RPC    │         │
│    └─────────┘    └──────────┘    └──────────┘         │
└─────────────────────────────────────────────────────────┘
```

## Features

| Feature | Description |
|---------|-------------|
| **Send KAS** | Transfer KAS to any Kaspa address |
| **Balance Check** | Check balance of any address |
| **Payment URIs** | Generate `kaspa:` payment request URIs |
| **Fee Estimates** | Get current network fee tiers |
| **Network Info** | Check node sync status and blocks |
| **Wallet Generation** | Generate new mnemonic phrases |

## Quick Start

### Installation

```bash
python3 install.py
```

**Requirements:** Python 3.8+ with pip. Works on macOS, Linux, Windows.

**Troubleshooting install:**
- If pip fails: `pip install kaspa` manually, or try `KASPA_PYTHON=python3.12 python3 install.py`
- If venv missing: `sudo apt install python3-venv` (Ubuntu/Debian)
- To reinstall: `rm -rf .venv && python3 install.py`

### CLI Usage

```bash
# Check balance
./kaswallet.sh balance
./kaswallet.sh balance kaspa:qrc8y...

# Send payment
./kaswallet.sh send kaspa:qrc8y... 0.5
./kaswallet.sh send kaspa:qrc8y... max

# Generate payment URI
./kaswallet.sh uri kaspa:q... 1.5 "coffee payment"

# Network info
./kaswallet.sh info

# Fee estimates
./kaswallet.sh fees

# Generate new wallet
./kaswallet.sh generate-mnemonic
```

### Payment URI Format

## Architecture

```
kaspa-wallet/
├── SKILL.md
├── README.md
├── install.py              # Auto-installer with venv
├── kaswallet.sh            # CLI wrapper script
├── requirements.txt
└── scripts/
    └── kaswallet.py        # Main wallet logic
```

## Configuration

```bash
# Environment variables (one required)
export KASPA_PRIVATE_KEY="64-character-hex-string"
# OR
export KASPA_MNEMONIC="your twelve or twenty four word seed phrase"

# Optional
export KASPA_NETWORK="mainnet"              # mainnet (default), testnet-10
export KASPA_RPC_URL="wss://..."            # Custom RPC endpoint
export KASPA_RPC_CONNECT_TIMEOUT_MS="30000" # Connection timeout (default: 15000)
```

## Core Functions

### Check Balance

```bash
./kaswallet.sh balance                    # Your wallet balance
./kaswallet.sh balance kaspa:qrc8y...     # Any address balance
```

**Output:**
```json
{"address": "kaspa:q...", "balance": "1.5", "sompi": "150000000", "network": "mainnet"}
```

### Send KAS

```bash
./kaswallet.sh send <address> <amount>           # Send specific amount
./kaswallet.sh send <address> max                # Send entire balance
./kaswallet.sh send <address> <amount> priority  # Priority fee tier
```

**Output (success):**
```json
{"status": "sent", "txid": "abc123...", "from": "kaspa:q...", "to": "kaspa:q...", "amount": "0.5", "fee": "0.0002"}
```

**Output (error):**
```json
{"error": "Storage mass exceeds maximum", "errorCode": "STORAGE_MASS_EXCEEDED", "hint": "...", "action": "consolidate_utxos"}
```

### Network Info

```bash
./kaswallet.sh info
```

**Output:**
```json
{"network": "mainnet", "url": "wss://...", "blocks": 12345678, "synced": true, "version": "1.0.0"}
```

### Fee Estimates

```bash
./kaswallet.sh fees
```

**Output:**
```json
{"network": "mainnet", "low": {"feerate": 1.0, "estimatedSeconds": 60}, "economic": {...}, "priority": {...}}
```

### Generate New Wallet

```bash
./kaswallet.sh generate-mnemonic
```

**Output:**
```json
{"mnemonic": "word1 word2 word3 ... word24"}
```

### Payment URI

```bash
./kaswallet.sh uri                          # Your address
./kaswallet.sh uri kaspa:q... 1.5 "payment" # With amount and message
```

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| `STORAGE_MASS_EXCEEDED` | Amount too small for current UTXOs | Send `max` to yourself first to consolidate |
| `NO_UTXOS` | No spendable outputs | Wait for confirmations or fund wallet |
| `INSUFFICIENT_FUNDS` | Balance too low | Check balance, reduce amount |
| `RPC_TIMEOUT` | Network slow | Retry or increase timeout |
| `NO_CREDENTIALS` | Missing wallet key | Set KASPA_PRIVATE_KEY or KASPA_MNEMONIC |
| `SDK_NOT_INSTALLED` | Kaspa SDK missing | Run `python3 install.py` |

## Payment Flow

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Sender    │     │ Kaspa Wallet│     │  Recipient  │
└──────┬──────┘     └──────┬──────┘     └──────┬──────┘
       │                   │                   │
       │  1. Initiate      │                   │
       │──────────────────▶│                   │
       │                   │                   │
       │                   │  2. Execute       │
       │                   │  KAS Transfer     │
       │                   │─────────────────▶│
       │                   │                   │
       │                   │  3. Confirm       │
       │                   │◀──────────────────│
       │  4. Success       │                   │
       │◀──────────────────│                   │
       │                   │                   │
```

## Common Workflows

### Consolidate UTXOs (Fix Storage Mass Error)

When sending fails with `STORAGE_MASS_EXCEEDED`:

```bash
# 1. Get your address
./kaswallet.sh balance
# Returns: {"address": "kaspa:qYOUR_ADDRESS...", ...}

# 2. Send max to yourself (consolidates UTXOs)
./kaswallet.sh send kaspa:qYOUR_ADDRESS... max

# 3. Now send the original amount (will work)
./kaswallet.sh send kaspa:qRECIPIENT... 0.5
```

### Check Transaction Status

After sending, use the `txid` to verify on a block explorer:
- Mainnet: `https://explorer.kaspa.org/txs/{txid}`
- Testnet: `https://explorer-tn10.kaspa.org/txs/{txid}`

### Switch Networks

```bash
# Testnet
export KASPA_NETWORK="testnet-10"
./kaswallet.sh info

# Back to mainnet
export KASPA_NETWORK="mainnet"
./kaswallet.sh info
```

## Units

- **KAS**: Human-readable unit (e.g., 1.5 KAS)
- **sompi**: Smallest unit, 1 KAS = 100,000,000 sompi

All command inputs accept KAS. Outputs include both KAS and sompi where relevant.

## Security Notes

- **Private keys**: Never expose in logs or error messages
- **Mnemonics**: Passed via environment variables only
- **No disk storage**: Wallet does not store credentials
- **Fresh connections**: Each command establishes new RPC connection
- **Address format**: Validate Kaspa addresses (`kaspa:q...` format)

## Comparison with Traditional Wallets

| Feature | Traditional Wallet | Kaspa Wallet CLI |
|---------|-------------------|------------------|
| Setup | GUI install | `python3 install.py` |
| Interface | Desktop app | CLI + JSON output |
| Automation | Limited | Full (JSON parsing) |
| Custody | Varies | Self-custody |
| Agent-friendly | No | Yes |

## Roadmap

- [ ] QR code generation for addresses
- [ ] Payment links
- [ ] Transaction history
- [ ] Multi-address support
- [ ] Batch payments
- [ ] Telegram bot integration

## Resources

- [Kaspa Docs](https://docs.kaspa.org/)
- [Kaspa Explorer](https://explorer.kaspa.org/)
- [kaspa-py SDK](https://github.com/aspect-build/kaspa-py)
