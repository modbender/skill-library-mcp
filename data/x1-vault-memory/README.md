# 🦞 X1 Vault Memory

**Decentralized, encrypted memory backup for OpenClaw AI agents — powered by X1 blockchain and IPFS.**

---

## Required Configuration

| Variable | Required | Details |
|----------|----------|---------|
| `PINATA_JWT` | ✅ Yes | Set in container `.env` - Your Pinata API token for IPFS uploads |
| `x1_vault_cli/wallet.json` | ✅ Yes | Dedicated wallet only, NOT your main wallet |
| `X1_RPC_URL` | ❌ No | Defaults to `https://rpc.mainnet.x1.xyz` |

> 🔴 **SECURITY WARNING:** Use a dedicated wallet with minimal XNT. Never use your primary wallet.

---

## What Is This?

An OpenClaw skill that backs up your AI agent's identity and memory files to IPFS with encrypted storage and on-chain CID references on the X1 blockchain.

Your agent's brain — personality, knowledge, memories — encrypted with your wallet key, stored on decentralized infrastructure, and recoverable from anywhere.

**No more losing your agent when a server dies.**

---

## How It Works
```
Agent Files → tar.gz → Encrypt (AES-256-GCM) → Upload (IPFS/Pinata) → Record CID (X1 Blockchain)
```

1. **Bundle** — Compresses agent files (IDENTITY.md, SOUL.md, USER.md, TOOLS.md, memory/) into a tar.gz
2. **Encrypt** — Encrypts the archive with your wallet's secret key using AES-256-GCM
3. **Upload** — Pushes the encrypted blob to IPFS via Pinata's API
4. **Record** — Stores the IPFS CID on the X1 blockchain via Memo Program
5. **Track** — Logs the CID and timestamp to vault-log.json

Only your wallet keypair can decrypt. Even if someone finds the CID, your data stays private.

---

## Requirements

| Requirement | Details |
|-------------|---------|
| **Node.js** | v18+ |
| **Pinata Account** | Free at [app.pinata.cloud](https://app.pinata.cloud) |
| **XNT Tokens** | ~0.002 XNT per backup for on-chain fees |
| **OpenClaw** | Running instance with workspace access |

✅ **No Solana CLI required** — we use `@solana/web3.js` directly.

---

## Installation

### For OpenClaw Agents

1. Clone into your OpenClaw workspace:
```bash
cd /home/node/.openclaw/workspace
git clone https://github.com/Lokoweb3/x1-vault-memory.git
cd x1-vault-memory
npm install
```

2. Add environment variables to your `.env` file:
```bash
echo "PINATA_JWT=your_token_here" >> ~/openclaw/.env
echo "X1_RPC_URL=https://rpc.mainnet.x1.xyz" >> ~/openclaw/.env
```

3. Add to `docker-compose.yml` environment:
```yaml
environment:
  PINATA_JWT: ${PINATA_JWT}
  X1_RPC_URL: ${X1_RPC_URL}
```

4. Restart the container:
```bash
cd ~/openclaw
docker compose down && docker compose up -d
```

5. Tell your agent about the skill:
> "You have a new skill called x1-vault-memory. You can backup your memory with node x1-vault-memory/src/backup.js and restore with node x1-vault-memory/src/restore.js CID. Save this to your memory."

---

## Setup

### 1. Create a Wallet Keypair

**Note:** Use Node.js only. No Solana CLI needed.

```bash
node -e "
const { Keypair } = require('@solana/web3.js');
const fs = require('fs');
const kp = Keypair.generate();
fs.writeFileSync('x1_vault_cli/wallet.json', JSON.stringify([...kp.secretKey]));
console.log('Wallet created:', kp.publicKey.toBase58());
"
```

**Or use X1 Wallet Chrome extension** to generate a keypair and export the secretKey JSON.

Keep `wallet.json` safe. This is your encryption key. Never commit it to GitHub.

> 🔴 **SECURITY WARNING:** Use a dedicated wallet with minimal XNT. Never use your primary wallet.

### 2. Fund Your Wallet

Send XNT tokens to your wallet address. You need ~0.002 XNT per backup transaction.

> 🔴 **SECURITY WARNING:** Use a dedicated wallet with minimal XNT. Never use your primary wallet.

---

## Usage

### Backup
```bash
node x1-vault-memory/src/backup.js
```

Output:
```
Archive checksum: a1b2c3d4e5f6...
Backup uploaded, CID: QmExampleCID123456789abcdefghijklmnopqrstuv
X1 Transaction: 5h1XWikXsqVoDEnK54DbG5Jurxnwqf5puVD5FL28JByCBhatCk7X2mnMCyipLvYmsNDjdrvvmDtQZpPRZuwWqccV
Explorer: https://explorer.mainnet.x1.xyz/tx/...
Logged backup CID to vault-log.json
```

**Features:**
- ✅ SHA-256 checksum generated before encryption
- ✅ Checksum stored in encrypted payload for integrity verification
- ✅ CID anchored to X1 blockchain with transaction hash

### Restore
```bash
# Full restore
node x1-vault-memory/src/restore.js <CID>

# Selective restore (only memory folder)
node x1-vault-memory/src/restore.js <CID> --only memory/
```

**Features:**
- ✅ Automatic integrity verification (checksum must match)
- ✅ Aborts with error if archive is corrupted
- ✅ Selective restore — restore specific paths without overwriting identity files

### List Backups
```bash
node x1-vault-memory/src/list.js
```

Shows numbered list of all backups with timestamps and anchor status.

### Heartbeat Check
```bash
node x1-vault-memory/src/heartbeat.js
```

Self-healing check:
- Verifies SOUL.md and memory/ exist and aren't empty
- Auto-restores from latest backup if issues detected

> ⚠️ **Opt-in Only** — Heartbeat auto-restore must be explicitly scheduled via cron. It is NOT automatic.
> 
> **Add to crontab:**
> ```bash
> 0 */6 * * * cd /path/to/workspace && node x1-vault-memory/src/heartbeat.js >> /var/log/vault-heartbeat.log 2>&1
> ```
> 
> **Note:** Heartbeat auto-restore is disabled by default and must be explicitly enabled via cron.

### Shell Wrappers
```bash
bash x1-vault-memory/scripts/backup.sh
bash x1-vault-memory/scripts/restore.sh <CID>
```

---

## CID Tracking

Every backup is logged to vault-log.json:
```json
[
  {
    "timestamp": "2026-02-16T09:48:38.207Z",
    "cid": "QmExampleCID123456789abcdefghijklmnopqrstuv"
  }
]
```

CIDs are also recorded on-chain. Check your wallet's transaction history on the [X1 Explorer](https://explorer.mainnet.x1.xyz).

---

## Automation

### Weekly Backup (Sundays at 2am)
```bash
0 2 * * 0 cd /path/to/workspace && node x1-vault-memory/src/backup.js >> /var/log/vault-backup.log 2>&1
```

### Heartbeat Check (Opt-in)
```bash
# Must be explicitly added to crontab - NOT automatic
0 */6 * * * cd /path/to/workspace && node x1-vault-memory/src/heartbeat.js >> /var/log/vault-heartbeat.log 2>&1
```

---

## Files Backed Up

| File | Purpose |
|------|---------|
| IDENTITY.md | Agent name, persona, vibe |
| SOUL.md | Personality, instructions, expertise |
| USER.md | User profile and preferences |
| TOOLS.md | Environment-specific notes |
| memory/*.md | Daily memory logs |

---

## Security

- 🔐 Encrypted with AES-256-GCM using your wallet's secret key
- 🔑 Only your keypair can decrypt
- 📡 Stored on IPFS, not a single server
- ⛓️ CID recorded on X1 blockchain via Memo Program for permanence
- 🚫 Never share your wallet.json or PINATA_JWT

> 🔴 **SECURITY WARNING:** Use a dedicated wallet with minimal XNT. Never use your primary wallet.

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Encryption | AES-256-GCM |
| IPFS Storage | Pinata API (JWT auth) |
| Blockchain | X1 (SVM-compatible L1) |
| Runtime | Node.js |
| Archiving | tar (npm) |
| Wallet | @solana/web3.js (Node.js, no CLI needed) |

---

## About X1

[X1](https://x1.xyz) is a high-performance, SVM-compatible Layer-1 blockchain.

- **Docs:** [docs.x1.xyz](https://docs.x1.xyz)
- **Explorer:** [explorer.mainnet.x1.xyz](https://explorer.mainnet.x1.xyz)
- **Testnet RPC:** https://rpc.testnet.x1.xyz
- **Mainnet RPC:** https://rpc.mainnet.x1.xyz

---

## License

MIT

---

**Built by [Lokoweb3](https://github.com/Lokoweb3) with Loko_AI 🦞**

---

[**GitHub Repository**](https://github.com/Lokoweb3/x1-vault-memory) | [**Documentation**](https://docs.openclaw.ai)
