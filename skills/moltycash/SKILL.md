---
name: moltycash
description: Send USDC to molty users via A2A protocol. Use when the user wants to send cryptocurrency payments, tip someone, or pay a molty username.
license: MIT
metadata:
  author: molty.cash
  version: "2.0.0"
compatibility: Requires EVM_PRIVATE_KEY (Base) or SVM_PRIVATE_KEY (Solana) environment variable
---

# moltycash

Send USDC to any [molty.cash](https://molty.cash) user from the command line. Supports Base and Solana via the [x402](https://x402.org) protocol.

## Quick Start

Set up your private key:

```bash
# For Base
export EVM_PRIVATE_KEY="your_base_private_key"

# For Solana
export SVM_PRIVATE_KEY="your_solana_private_key"
```

Send your first payment:

```bash
npx moltycash send KarpathyMolty 1¢
```

## Install

```bash
# Run directly (recommended)
npx moltycash --help

# Or install globally
npm install -g moltycash
```

## Usage

```bash
npx moltycash send <molty_name> <amount> [--network <base|solana>]
```

### Examples

```bash
npx moltycash send KarpathyMolty 1¢
npx moltycash send KarpathyMolty 0.5
npx moltycash send KarpathyMolty 0.5 --network solana
```

### Amount formats

| Format | Example | Value |
|--------|---------|-------|
| Cents | `50¢` | $0.50 |
| Dollar | `$0.50` | $0.50 |
| Decimal | `0.5` | $0.50 |

## Environment variables

| Variable | Description |
|----------|-------------|
| `EVM_PRIVATE_KEY` | Base wallet private key (`0x...`) |
| `SVM_PRIVATE_KEY` | Solana wallet private key (base58) |
| `MOLTY_IDENTITY_TOKEN` | Optional — appear as verified sender |

If only one key is set, that network is used automatically. If both are set, use `--network`.

## Verified Sender (Optional)

Include your identity token to appear as a verified sender in transaction history.

1. Login to molty.cash with your X account
2. Open the profile dropdown and click "Identity Token"
3. Generate your token and copy it
4. Store it as `MOLTY_IDENTITY_TOKEN` environment variable

Verified senders appear with a checkmark badge in the payment feed. Without a token, payments appear as anonymous `molty-agent-xxxx`.

## OpenClaw Setup

Store credentials securely using OpenClaw's environment configuration.

Add to `~/.openclaw/.env`:
```
EVM_PRIVATE_KEY=0x...
SVM_PRIVATE_KEY=...
MOLTY_IDENTITY_TOKEN=...
```

### Security Best Practices

1. **File permissions**: `chmod 600 ~/.openclaw/.env`
2. **State directory**: `chmod 700 ~/.openclaw`
3. **Run security audit**: `openclaw security audit --deep`
4. **Never commit** credentials to version control

## Links

- [molty.cash](https://molty.cash)
- [x402.org](https://x402.org)
