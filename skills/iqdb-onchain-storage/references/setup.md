# Environment Setup

## Prerequisites

- **Node.js 18+** — `node --version`
- **Solana CLI** — `solana --version`
- **A Solana wallet** — Keypair JSON file

## Install Solana CLI

```bash
# macOS/Linux
sh -c "$(curl -sSfL https://release.anza.xyz/stable/install)"

# Windows — download installer and run with admin privileges
# https://release.anza.xyz/stable/solana-install-init-x86_64-pc-windows-msvc.exe
```

Add to PATH: `export PATH="$HOME/.local/share/solana/install/active_release/bin:$PATH"`

## Configure for Devnet

```bash
solana config set --url https://api.devnet.solana.com
solana-keygen new --no-bip39-passphrase -o ~/.config/solana/id.json
solana config set --keypair ~/.config/solana/id.json
solana airdrop 2
```

If airdrop fails (rate-limited), use the web faucet at faucet.solana.com.

## Install Dependencies

### New SDK (Mainnet)

```bash
npm install @iqlabs-official/solana-sdk @solana/web3.js
```

The new SDK supports both CJS and ESM. CJS is recommended for compatibility with existing IQDB tooling.

### Legacy SDK (Devnet)

```bash
npm install @iqlabsteam/iqdb @coral-xyz/anchor @solana/web3.js hanlock
```

**Important (legacy only):** Set `"type": "commonjs"` in package.json (or use `.cjs` file extension). The legacy IQDB SDK uses dynamic `require()` internally and does not support ESM.

## New SDK Setup (Mainnet)

```javascript
// setup.cjs
const { Connection } = require('@solana/web3.js');

// Buffer monkey-patch — required on Node v24
// SDK's toSeedBytes() returns Uint8Array, but Anchor Borsh encoder requires Buffer
const seedModule = require('@iqlabs-official/solana-sdk/dist/sdk/utils/seed');
const origFn = seedModule.toSeedBytes;
if (!seedModule._patched) {
  seedModule.toSeedBytes = (v) => Buffer.from(origFn(v));
  seedModule._patched = true;
}

const { IQDBContract, IQDBWriter, IQDBReader } = require('@iqlabs-official/solana-sdk');

const RPC = process.env.ANCHOR_PROVIDER_URL || 'https://solana-rpc.publicnode.com';
const connection = new Connection(RPC, 'confirmed');

// Program ID: 9KLLchQVJpGkw4jPuUmnvqESdR7mtNCYr3qS4iQLabs
const contract = new IQDBContract(connection);
const writer = new IQDBWriter(connection);
const reader = new IQDBReader(connection);

module.exports = { contract, writer, reader, connection };
```

### Required Environment Variables

```bash
ANCHOR_WALLET=/path/to/keypair.json                    # Required — Solana keypair for signing
ANCHOR_PROVIDER_URL=https://solana-rpc.publicnode.com   # Recommended — primary RPC
```

## Legacy SDK Setup (Devnet)

```javascript
// setup.cjs
// Set NETWORK_URL before importing to ensure reads use the same RPC as writes
const RPC = process.env.ANCHOR_PROVIDER_URL || 'https://api.devnet.solana.com';
process.env.NETWORK_URL = RPC;

const { createIQDB } = require('@iqlabsteam/iqdb');

const iqdb = createIQDB();

async function init() {
  await iqdb.ensureRoot();
  console.log('IQDB ready.');
}

module.exports = { iqdb, init };
```

### Required Environment Variables (Legacy)

```bash
ANCHOR_WALLET=/path/to/keypair.json        # Required — Solana keypair for signing
ANCHOR_PROVIDER_URL=https://api.devnet.solana.com  # Required — RPC endpoint
```

**RPC Note:** The standard `api.devnet.solana.com` aggressively rate-limits. The SDK includes a built-in Helius devnet RPC as fallback. For production use, get a dedicated RPC from Helius, Alchemy, or QuickNode.

## Mainnet Checklist

1. Use `https://solana-rpc.publicnode.com` as primary RPC (handles rapid reads without 429s)
2. Use `https://api.mainnet-beta.solana.com` as fallback only
3. Add 2-3 second delays between write transactions to avoid rate limiting
4. Apply Buffer monkey-patch before any SDK calls (Node v24 — `Uint8Array` is not a `Buffer` subclass)
5. Use a funded wallet (real SOL)
6. Test all operations on devnet first
7. Budget for rent costs (~0.012 SOL per 100 tables)
8. Row data must stay under ~120 bytes per write (client-side limit)
9. Omit empty optional fields to save row space (`ci: ""` wastes 7 bytes)
