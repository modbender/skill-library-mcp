---
name: x1-vault-memory
description: Backup and restore OpenClaw agent memory to IPFS with AES-256-GCM encryption and X1 blockchain CID anchoring
version: 0.2.0
author: Lokoweb3
homepage: https://github.com/Lokoweb3/x1-vault-memory
metadata:
  clawdbot:
    emoji: "🦞"
requires:
  env: ["PINATA_JWT"]
  primaryEnv: "PINATA_JWT"
  configPaths: ["x1_vault_cli/wallet.json"]
files: ["src/*"]
tags:
  - backup
  - memory
  - ipfs
  - encryption
  - x1
  - blockchain
  - restore
  - vault
---

# X1 Vault Memory

Encrypted, decentralized memory backup for OpenClaw agents — powered by IPFS and X1 blockchain.

## Required Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `PINATA_JWT` | ✅ Yes | — | Your Pinata API token for IPFS uploads. Get it at https://app.pinata.cloud |
| `X1_RPC_URL` | ❌ No | `https://rpc.mainnet.x1.xyz` | The X1 RPC endpoint. Change only if using testnet or custom endpoint |
| `x1_vault_cli/wallet.json` | ✅ Yes | — | Your X1 wallet keypair file. Used for encryption and blockchain anchoring. |

> 🔴 **SECURITY WARNING:** Use a dedicated wallet with minimal XNT. Never use your primary wallet.

---

## What It Does

Backs up your agent's brain (identity, personality, memories) with AES-256-GCM military-grade encryption, stores it on IPFS, and anchors the CID on the X1 blockchain. Only your wallet keypair can decrypt.

Pipeline: Agent Files > tar.gz > AES-256-GCM Encrypt > IPFS Upload > X1 On-Chain Anchor

### Why This Exists

Servers die. Containers get wiped. One bad rm -rf and your agent's identity is gone. X1 Vault Memory makes your agent's brain indestructible — encrypted, decentralized, and recoverable from anywhere.

### Key Features

- AES-256-GCM encryption — uses your wallet keypair as the key. Only you can decrypt.
- IPFS storage — your data lives on a decentralized network, not a single server.
- X1 blockchain anchoring — every backup CID is recorded on-chain for permanent, verifiable proof.
- Self-healing restore — one command to download, decrypt, and restore all agent files.
- Negligible cost — about 0.03 USD per year for daily backups.

### New in v1.1.2

- ✅ Security fixes: removed "curl | sh" Solana CLI install suggestion
- ✅ Declared environment variables clearly in skill metadata
- ✅ Added opt-in note for heartbeat auto-restore
- Updated package.json with required env vars in config section

### New in v1.1.0

- SHA-256 integrity verification on backup and restore
- Selective restore with --only flag to restore specific files or directories
- List command for viewing all backups with versioned rollback support

---

## Requirements

- **Node.js v18+** — run all scripts without external dependencies
- **Pinata Account** — free at https://app.pinata.cloud (500 files, 1GB included)
- **Solana Wallet** — keypair JSON file (free to create via @solana/web3.js)
- **XNT Tokens** — about 0.002 XNT per backup for on-chain fees

✅ **No Solana CLI required** — we use `@solana/web3.js` directly.

> 🔴 **SECURITY WARNING:** Use a dedicated wallet with minimal XNT. Never use your primary wallet.

---

## How to Get XNT Tokens

XNT is the native gas token of the X1 blockchain. You need a small amount for on-chain transaction fees.

1. Bridge from Solana (easiest) — https://app.bridge.x1.xyz — wrap SOL/USDC to X1, then swap for XNT on XDEX
2. Buy directly on XDEX — https://app.xdex.xyz/swap — native DEX on X1, connect your wallet and swap
3. OTC — https://otc.xonedex.xyz — peer-to-peer for larger amounts
4. Honey Badger Bot — https://t.me/HoneyBadgerCoreBot?start=ref_HEBCU2E3 — Telegram trading bot for instant swaps

You will also need the X1 Wallet Chrome extension: https://chromewebstore.google.com/detail/x1-wallet/kcfmcpdmlchhbikbogddmgopmjbflnae

Start with bridge + XDEX if you are coming from Solana. That is the smoothest path. Each backup costs approximately 0.002 XNT, so even a small amount goes a long way.

---

## How to Set Up Pinata and Get Your JWT Token

Pinata is the IPFS pinning service that stores your encrypted backups. The free tier is more than enough.

1. Go to https://app.pinata.cloud and click Sign Up
2. Create an account with your email or sign in with GitHub/Google
3. After login, click your profile icon in the top right corner
4. Select API Keys from the dropdown menu
5. Click the New Key button
6. Enable only the pinFileToIPFS permission (Admin access is NOT required)
7. Give the key a name like "x1-vault-memory"
8. Click Create Key
9. You will see three values: API Key, API Secret, and JWT
10. Copy the JWT token — this is your PINATA_JWT value
11. Save it somewhere safe — you will not be able to see the JWT again after closing this page

The JWT token does not expire unless you manually revoke it in the Pinata dashboard. Free tier includes 500 files and 1GB storage. Each encrypted backup is around 10-50KB, so you can store thousands of backups without paying anything.

---

## Setup

> 🔴 **SECURITY WARNING:** Use a dedicated wallet with minimal XNT. Never use your primary wallet.

### 1. Install Node dependencies

```bash
cd x1-vault-memory && npm install
```

### 2. Configure environment variables

**Option A: Using a .env file (recommended for Docker and production)**

Create a `.env` file in your project or workspace root:

```
PINATA_JWT=your_pinata_jwt_token
X1_RPC_URL=https://rpc.mainnet.x1.xyz
```

No quotes, no export keyword. Docker Compose and most Node.js apps read this format automatically.

**Option B: Using shell environment (for manual or one-time use)**

```bash
export PINATA_JWT="your_pinata_jwt_token"
export X1_RPC_URL="https://rpc.mainnet.x1.xyz"
```

Note: These values only persist for the current terminal session.

**Option C: Docker Compose environment block**

If running inside Docker, add to your docker-compose.yml environment section:

```yaml
environment:
  PINATA_JWT: ${PINATA_JWT}
  X1_RPC_URL: https://rpc.mainnet.x1.xyz
```

Then set `PINATA_JWT` in your Docker `.env` file as shown in Option A.

### 3. Create a wallet keypair (Node.js only, no CLI)

The wallet can be created programmatically using `@solana/web3.js`. Here's a quick script:

```bash
node -e "
const { Keypair } = require('@solana/web3.js');
const fs = require('fs');
const kp = Keypair.generate();
fs.writeFileSync('x1_vault_cli/wallet.json', JSON.stringify([...kp.secretKey]));
console.log('Wallet created:', kp.publicKey.toBase58());
console.log('Save the secretKey JSON array to x1_vault_cli/wallet.json');
"
```

Or use the X1 Wallet Chrome extension to generate a keypair and export the secretKey.

Keep `wallet.json` safe. This is your encryption key AND your blockchain wallet. Never commit it to GitHub.

### 4. Fund the wallet

Get your wallet address from `x1_vault_cli/wallet.json` (the public key derived from the secret key), then send XNT tokens to that address.

### 5. X1 RPC URL

Set `X1_RPC_URL` to your preferred endpoint. Default: `https://rpc.mainnet.x1.xyz`

---

## Usage

### Backup
```bash
node src/backup.js
```

Encrypts and uploads `IDENTITY.md`, `SOUL.md`, `USER.md`, `TOOLS.md`, and `memory/` directory. Records CID on X1 blockchain and logs to `vault-log.json`.

### Restore
```bash
node src/restore.js <CID>
```

Downloads from IPFS, decrypts with your wallet key, and restores all agent files.

### Selective Restore
```bash
node src/restore.js <CID> --only memory/
```

Restore only specific files or directories from a backup.

### List All Backups
```bash
node src/list.js
```

View all stored backups with timestamps, CIDs, and checksums for versioned rollback.

### Heartbeat Check
```bash
node src/heartbeat.js
```

Monitors agent file integrity. If critical files are missing or corrupted, automatically triggers a restore from the latest backup.

> ⚠️ **Opt-in Only** — Heartbeat auto-restore must be explicitly scheduled via cron. It is NOT automatic.
> 
> **Add to crontab:**
> ```bash
> 0 */6 * * * cd /path/to/workspace && node x1-vault-memory/src/heartbeat.js >> /var/log/vault-heartbeat.log 2>&1
> ```
> 
> **Note:** Heartbeat auto-restore is disabled by default and must be explicitly enabled via cron.

### Dry Run
```bash
node src/backup.js --dry-run
```

Shows which files would be backed up without uploading or spending tokens.

---

## Error Handling

- Pinata is down — backup fails with connection error. Retry later, local files are untouched.
- X1 RPC fails — IPFS upload succeeds but on-chain anchor fails. CID is still logged locally in `vault-log.json`. Re-anchor when RPC recovers.
- Invalid wallet — encryption fails before upload. Check `wallet.json` path and format (must be JSON array of bytes).
- Insufficient XNT — on-chain transaction rejected. Fund wallet with more XNT tokens.
- CID not found on restore — check Pinata dashboard, re-pin if needed.
- Checksum mismatch — SHA-256 verification failed. Backup may be corrupted. Try restoring from a previous version using `list.js`.

---

## Where Data Is Stored

- **IPFS** — encrypted blob on Pinata IPFS network
- **X1 Blockchain** — CID recorded as on-chain transaction (permanent, verifiable)
- **vault-log.json** — local log of all backup CIDs with timestamps and checksums
- **Only your wallet keypair can decrypt the data**

---

## Security

- AES-256-GCM authenticated encryption derived from your wallet secret key
- SHA-256 integrity checksums on every backup and restore
- Only your keypair can decrypt — even if someone finds the CID, data stays private
- Stored on IPFS, not a single server
- CID anchored on X1 blockchain for tamper-proof records
- Never share your `wallet.json` or `PINATA_JWT`

> 🔴 **SECURITY WARNING:** Use a dedicated wallet with minimal XNT. Never use your primary wallet.

---

## Automation

Weekly backup via cron:
```bash
0 2 * * 0 cd /path/to/workspace && node x1-vault-memory/src/backup.js >> /var/log/vault-backup.log 2>&1
```

Heartbeat check every 6 hours (opt-in):
```bash
0 */6 * * * cd /path/to/workspace && node x1-vault-memory/src/heartbeat.js >> /var/log/vault-heartbeat.log 2>&1
```

---

## Files Backed Up

- `IDENTITY.md` — agent name, persona, vibe
- `SOUL.md` — personality, instructions, expertise
- `USER.md` — user profile and preferences
- `TOOLS.md` — environment-specific notes
- `memory/*.md` — daily memory logs

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Encryption | AES-256-GCM (authenticated encryption) |
| Integrity | SHA-256 checksums |
| IPFS Storage | Pinata API (JWT auth) |
| Blockchain | X1 Mainnet (SVM-compatible L1) |
| Wallet | @solana/web3.js (Node.js, no CLI needed) |
| Runtime | Node.js v18+ |

---

## Links

- GitHub: https://github.com/Lokoweb3/x1-vault-memory
- X1 Explorer: https://explorer.mainnet.x1.xyz
- X1 Bridge: https://app.bridge.x1.xyz
- XDEX: https://app.xdex.xyz/swap
- X1 Wallet: https://chromewebstore.google.com/detail/x1-wallet/kcfmcpdmlchhbikbogddmgopmjbflnae
- Honey Badger Bot: https://t.me/HoneyBadgerCoreBot?start=ref_HEBCU2E3
- Pinata: https://app.pinata.cloud

Built by [Lokoweb3](https://github.com/Lokoweb3)

---

[GitHub Repository](https://github.com/Lokoweb3/x1-vault-memory) | [OpenClaw Docs](https://docs.openclaw.ai)