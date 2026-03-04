---
name: base-wallet
description: "🔐 Base Wallet - Crypto Identity for AI Agents. Create wallets, sign messages (SIWE), send transactions programmatically. No browser extensions, no human intervention. The foundation for autonomous Web3 agents."
---

# 🔐 Base Wallet - Crypto Identity for AI Agents

> Every autonomous agent needs a wallet. Create one without human help.

**TL;DR:** Programmatic wallet creation on Base/Ethereum. SIWE auth, balance checks, transactions.

## Why Base Wallet?

- **True autonomy** — Your agent creates and controls its own wallet
- **No browser needed** — Pure CLI, no extensions or popups
- **SIWE ready** — Sign-In with Ethereum for Web3 services
- **Secure by default** — Environment variables, no plaintext keys

Create and manage Base chain (Ethereum-compatible) wallets programmatically.

---

## ⚠️ Security First

| ✅ DO | ❌ DON'T |
|-------|----------|
| Use **environment variables** for private keys | Store private keys in plain text files |
| Set wallet files to **chmod 600** | Commit wallet files to git |
| Use `--env` mode (recommended) | Use `console.log(privateKey)` |
| Back up mnemonics **offline** | Share private keys or mnemonics |

---

## Quick Start

### Create a New Wallet (Recommended)

```bash
# Output as environment variable format (safest)
node scripts/create-wallet.js --env

# Output example:
# export WALLET_ADDRESS="0x..."
# export PRIVATE_KEY="0x..."
```

Then copy to your shell or `.env` file.

### Create with File Storage (Opt-in)

```bash
# Only if you need file-based storage
node scripts/create-wallet.js --managed my-agent
```

⚠️ This stores private key in `~/.openclaw/wallets/my-agent.json`

---

## Usage Examples

### Load Wallet from Environment

```javascript
const { ethers } = require('ethers');

// ✅ SECURE: Load from environment variable
const wallet = new ethers.Wallet(process.env.PRIVATE_KEY);
console.log('Address:', wallet.address);
// ❌ NEVER: console.log('Private Key:', wallet.privateKey);
```

### Load from Mnemonic

```javascript
const wallet = ethers.Wallet.fromPhrase(process.env.MNEMONIC);
```

### Check Balance

```javascript
const provider = new ethers.JsonRpcProvider('https://mainnet.base.org');
const balance = await provider.getBalance(wallet.address);
console.log('Balance:', ethers.formatEther(balance), 'ETH');
```

### Sign Message (SIWE)

```javascript
const message = `example.com wants you to sign in with your Ethereum account:
${wallet.address}

Sign in message

URI: https://example.com
Version: 1
Chain ID: 8453
Nonce: ${nonce}
Issued At: ${new Date().toISOString()}`;

const signature = await wallet.signMessage(message);
```

### Send Transaction

```javascript
const provider = new ethers.JsonRpcProvider('https://mainnet.base.org');
const connectedWallet = wallet.connect(provider);

const tx = await connectedWallet.sendTransaction({
  to: recipientAddress,
  value: ethers.parseEther('0.001')
});

const receipt = await tx.wait();
console.log('TX Hash:', tx.hash);
```

---

## Scripts

| Script | Description |
|--------|-------------|
| `create-wallet.js --env` | Create wallet, output as env vars (recommended) |
| `create-wallet.js --managed [name]` | Create wallet, save to file (opt-in) |
| `create-wallet.js --json` | Create wallet, output as JSON |
| `basemail-register.js [name]` | Register for BaseMail email |
| `check-balance.js [address]` | Check wallet balance |

---

## BaseMail Integration

Register for a @basemail.ai email using your wallet signature.

```bash
# If using environment variable:
PRIVATE_KEY="0x..." node scripts/basemail-register.js

# If using managed wallet:
node scripts/basemail-register.js my-agent
```

---

## Network Configuration

| Network | Chain ID | RPC URL |
|---------|----------|---------|
| Base Mainnet | 8453 | https://mainnet.base.org |
| Base Sepolia | 84532 | https://sepolia.base.org |

---

## 📝 Audit Logging

Operations are logged to `~/.base-wallet/audit.log`.

---

## Secure Storage Pattern

```javascript
// ✅ Recommended: Use environment variables
const privateKey = process.env.PRIVATE_KEY;
if (!privateKey) {
  throw new Error('PRIVATE_KEY environment variable not set');
}
const wallet = new ethers.Wallet(privateKey);

// ❌ Avoid: Storing private keys in code or files
```

If you must store to file (not recommended):

```javascript
const fs = require('fs');
const path = require('path');

// Store with restricted permissions
const filepath = path.join(process.env.HOME, '.openclaw', 'wallets', 'wallet.json');
fs.writeFileSync(filepath, JSON.stringify({ 
  address: wallet.address,
  // Only store if absolutely necessary
  privateKey: wallet.privateKey
}), { mode: 0o600 }); // Owner read/write only
```

---

## .gitignore

Add to your project's `.gitignore`:

```gitignore
# Wallet files - NEVER commit!
.openclaw/
*.wallet.json
*.mnemonic
private-key*
```

---

## Dependencies

```bash
npm install ethers
```

---

## Changelog

### v1.1.0 (2026-02-08)
- 🔐 Security: Changed create-wallet.js to opt-in file storage
- ✨ Added --env mode (recommended)
- 📝 Added audit logging
- ⚠️ Removed console.log(privateKey) from examples
- 📄 Enhanced security documentation

### v1.0.0
- 🎉 Initial release
