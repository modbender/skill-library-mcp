---
name: archon-cashu
description: Cashu ecash operations integrated with Archon DID for P2PK-locked tokens. Send and receive sats using DID-derived pubkeys, backup wallets to vault. Use for Cashu token operations, DID-locked payments, or ecash wallet management.
metadata:
  openclaw:
    requires:
      env:
        - ARCHON_WALLET_PATH
        - ARCHON_PASSPHRASE
        - ARCHON_CASHU_CONFIG
      bins:
        - node
        - npx
        - cashu
      anyBins:
        - curl
        - jq
    primaryEnv: ARCHON_CASHU_CONFIG
    emoji: "🥜"
---

# Archon Cashu - DID-Integrated Ecash

Cashu ecash operations using your Archon DID for P2PK-locked tokens. Send sats that only the recipient's DID can unlock.

## Prerequisites

- Archon identity configured (`~/.archon.env`)
- Cashu CLI installed (`pip install cashu` or similar)
- Config file at `~/.config/archon/cashu.env` (or `ARCHON_CASHU_CONFIG`)

## Configuration

```bash
./scripts/cashu/config.sh
```

Sets up Cashu wallet and optional LNBITS integration.

## Operations

### Check Balance

```bash
./scripts/cashu/balance.sh
```

### Send Tokens (Unlocked)

```bash
./scripts/cashu/send-unlocked.sh <amount>
```

Returns a Cashu token anyone can redeem.

### Send Tokens (DID-Locked)

```bash
./scripts/cashu/send.sh <amount> <recipient-did>
```

Locks tokens to recipient's DID-derived pubkey (P2PK). Only they can unlock.

### Receive Tokens

```bash
./scripts/cashu/receive.sh <token>
```

### Mint Tokens (Lightning)

```bash
./scripts/cashu/mint.sh <amount>
```

Creates Lightning invoice to mint new tokens.

### Lock/Unlock Tokens

```bash
./scripts/cashu/lock.sh <amount> <did>
```

### Backup Wallet to Vault

```bash
./scripts/cashu/backup.sh [vault-did]
```

### npub.cash Setup

```bash
./scripts/cashu/npub-cash-setup.sh
```

Configure npub.cash integration for Nostr zaps.

## Security Notes

1. **Wallet location**: `~/.cashu` by default (configurable via `CASHU_WALLET_DIR`)

2. **P2PK locking**: DID-locked tokens use your DID's secp256k1 key for cryptographic locking

3. **LNBITS integration**: Optional — for auto-paying invoices during mint operations
