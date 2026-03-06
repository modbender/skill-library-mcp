---
name: cifer-sdk
description: Implement quantum-resistant encryption using the CIFER SDK (cifer-sdk npm package). Covers SDK initialization, wallet setup, secret creation, text encryption/decryption, and file encryption/decryption on any supported chain (Ethereum, Sepolia, Ternoa). Use when the user mentions CIFER, cifer-sdk, quantum-resistant encryption, ML-KEM, secret creation, or encrypted payloads/files with blockchain.
---

# CIFER SDK — Complete Integration Guide

## Overview

CIFER SDK provides quantum-resistant encryption (ML-KEM-768 + AES-256-GCM) for blockchain apps. Secrets are on-chain key pairs: public key on IPFS, private key sharded across enclaves.

**Package**: `cifer-sdk` (npm)
**Chains**: Ethereum Mainnet (1), Sepolia (11155111), Ternoa (752025)
**Blackbox URL**: `https://cifer-blackbox.ternoa.dev:3010`

For the full API reference, see [reference.md](reference.md).

---

## Quick Setup

```bash
npm install cifer-sdk ethers dotenv
```

`package.json` must have `"type": "module"` for ESM imports.

```javascript
import 'dotenv/config';
import { createCiferSdk, keyManagement, blackbox } from 'cifer-sdk';
import { Wallet, JsonRpcProvider } from 'ethers';
```

---

## Step 1: Initialize SDK

```javascript
const sdk = await createCiferSdk({
  blackboxUrl: 'https://cifer-blackbox.ternoa.dev:3010',
});

const chainId = 1; // Ethereum Mainnet (or 11155111 for Sepolia, 752025 for Ternoa)
const controllerAddress = sdk.getControllerAddress(chainId);
const rpcUrl = sdk.getRpcUrl(chainId);
```

`sdk.getSupportedChainIds()` returns all available chains.

## Step 2: Create Wallet Signer (Server-Side)

```javascript
const provider = new JsonRpcProvider(rpcUrl);
const wallet = new Wallet(process.env.PRIVATE_KEY, provider);

// Signer adapter — this is what the SDK expects
const signer = {
  async getAddress() { return wallet.address; },
  async signMessage(message) { return wallet.signMessage(message); },
};
```

For browser wallets, use the built-in adapter instead:
```javascript
import { Eip1193SignerAdapter } from 'cifer-sdk';
const signer = new Eip1193SignerAdapter(window.ethereum);
```

## Step 3: Create a Secret

A secret costs a fee in native token. Check balance first.

```javascript
const fee = await keyManagement.getSecretCreationFee({
  chainId, controllerAddress, readClient: sdk.readClient,
});

const txIntent = keyManagement.buildCreateSecretTx({ chainId, controllerAddress, fee });

const tx = await wallet.sendTransaction({
  to: txIntent.to,
  data: txIntent.data,
  value: txIntent.value,
});
const receipt = await tx.wait();
const secretId = keyManagement.extractSecretIdFromReceipt(receipt.logs);
```

## Step 4: Wait for Secret Sync

After creation, the enclave cluster generates keys (~30-120s on mainnet).

```javascript
let ready = false;
while (!ready) {
  ready = await keyManagement.isSecretReady(
    { chainId, controllerAddress, readClient: sdk.readClient },
    secretId,
  );
  if (!ready) await new Promise(r => setTimeout(r, 5000));
}
```

Or read the full state:
```javascript
const state = await keyManagement.getSecret(
  { chainId, controllerAddress, readClient: sdk.readClient },
  secretId,
);
// state.owner, state.delegate, state.isSyncing, state.publicKeyCid
```

## Step 5: Encrypt Text

```javascript
const encrypted = await blackbox.payload.encryptPayload({
  chainId,
  secretId,
  plaintext: 'Your secret message',
  signer,
  readClient: sdk.readClient,
  blackboxUrl: sdk.blackboxUrl,
});
// Returns: { cifer, encryptedMessage }
```

## Step 6: Decrypt Text

Caller must be secret owner or delegate.

```javascript
const decrypted = await blackbox.payload.decryptPayload({
  chainId,
  secretId,
  encryptedMessage: encrypted.encryptedMessage,
  cifer: encrypted.cifer,
  signer,
  readClient: sdk.readClient,
  blackboxUrl: sdk.blackboxUrl,
});
// Returns: { decryptedMessage }
```

## Step 7: Encrypt File

File operations are async jobs. Works with `Blob` in Node.js 18+.

```javascript
import { readFile, writeFile } from 'fs/promises';

const buffer = await readFile('myfile.pdf');
const blob = new Blob([buffer], { type: 'application/pdf' });

// Start encrypt job
const job = await blackbox.files.encryptFile({
  chainId, secretId, file: blob, signer,
  readClient: sdk.readClient, blackboxUrl: sdk.blackboxUrl,
});

// Poll until done
const status = await blackbox.jobs.pollUntilComplete(job.jobId, sdk.blackboxUrl, {
  intervalMs: 2000,
  maxAttempts: 120,
  onProgress: (j) => console.log(`${j.progress}%`),
});

// Download encrypted .cifer file (no auth needed for encrypt jobs)
const encBlob = await blackbox.jobs.download(job.jobId, { blackboxUrl: sdk.blackboxUrl });
await writeFile('myfile.pdf.cifer', Buffer.from(await encBlob.arrayBuffer()));
```

## Step 8: Decrypt File

```javascript
const encBuffer = await readFile('myfile.pdf.cifer');
const encBlob = new Blob([encBuffer]);

const decJob = await blackbox.files.decryptFile({
  chainId, secretId, file: encBlob, signer,
  readClient: sdk.readClient, blackboxUrl: sdk.blackboxUrl,
});

const decStatus = await blackbox.jobs.pollUntilComplete(decJob.jobId, sdk.blackboxUrl, {
  intervalMs: 2000, maxAttempts: 120,
});

// Download decrypted file (auth REQUIRED for decrypt jobs)
const decBlob = await blackbox.jobs.download(decJob.jobId, {
  blackboxUrl: sdk.blackboxUrl,
  chainId, secretId, signer, readClient: sdk.readClient,
});
await writeFile('myfile-decrypted.pdf', Buffer.from(await decBlob.arrayBuffer()));
```

---

## List Existing Secrets

```javascript
const secrets = await keyManagement.getSecretsByWallet(
  { chainId, controllerAddress, readClient: sdk.readClient },
  wallet.address,
);
// secrets.owned: bigint[]   — secrets you own
// secrets.delegated: bigint[] — secrets delegated to you
```

## Delegation

Set a delegate (can decrypt but not encrypt or modify):
```javascript
const txIntent = keyManagement.buildSetDelegateTx({
  chainId, controllerAddress, secretId, newDelegate: '0xDelegateAddress',
});
await wallet.sendTransaction({ to: txIntent.to, data: txIntent.data });
```

Remove delegation:
```javascript
const txIntent = keyManagement.buildRemoveDelegationTx({
  chainId, controllerAddress, secretId,
});
```

---

## Important Notes

- **Minimum SDK version**: Use `cifer-sdk@0.3.1` or later. Earlier versions had incorrect function selectors.
- **Payload size limit**: Text encryption max ~16KB (`encryptPayload`). Use file encryption for larger data.
- **Block freshness**: The SDK auto-retries up to 3 times if the block number becomes stale.
- **Secret sync time**: ~30-60s on Ternoa, ~60-120s on Ethereum mainnet.
- **Auth for file download**: Encrypt job downloads need no auth. Decrypt job downloads require signer + readClient.
- **Fee**: Secret creation requires a fee in native token (e.g. ~0.0005 ETH on mainnet). Query `getSecretCreationFee()` first.
- **Private keys**: Never expose private keys in frontend code. Use server-side signer for Node.js.

## Error Handling

```javascript
import { isCiferError, isBlockStaleError } from 'cifer-sdk';

try {
  await blackbox.payload.encryptPayload({ ... });
} catch (error) {
  if (isBlockStaleError(error)) {
    // RPC returning stale blocks, SDK already retried 3x
  } else if (error instanceof SecretNotReadyError) {
    // Wait and retry
  } else if (isCiferError(error)) {
    console.error(error.code, error.message);
  }
}
```

## Complete Minimal Example

```javascript
import 'dotenv/config';
import { createCiferSdk, keyManagement, blackbox } from 'cifer-sdk';
import { Wallet, JsonRpcProvider } from 'ethers';

const sdk = await createCiferSdk({ blackboxUrl: 'https://cifer-blackbox.ternoa.dev:3010' });
const chainId = 1;
const controllerAddress = sdk.getControllerAddress(chainId);
const provider = new JsonRpcProvider(sdk.getRpcUrl(chainId));
const wallet = new Wallet(process.env.PRIVATE_KEY, provider);
const signer = {
  async getAddress() { return wallet.address; },
  async signMessage(msg) { return wallet.signMessage(msg); },
};

// Create secret
const fee = await keyManagement.getSecretCreationFee({ chainId, controllerAddress, readClient: sdk.readClient });
const txIntent = keyManagement.buildCreateSecretTx({ chainId, controllerAddress, fee });
const tx = await wallet.sendTransaction({ to: txIntent.to, data: txIntent.data, value: txIntent.value });
const receipt = await tx.wait();
const secretId = keyManagement.extractSecretIdFromReceipt(receipt.logs);

// Wait for sync
let ready = false;
while (!ready) {
  ready = await keyManagement.isSecretReady({ chainId, controllerAddress, readClient: sdk.readClient }, secretId);
  if (!ready) await new Promise(r => setTimeout(r, 5000));
}

// Encrypt & decrypt
const enc = await blackbox.payload.encryptPayload({
  chainId, secretId, plaintext: 'Hello CIFER!', signer,
  readClient: sdk.readClient, blackboxUrl: sdk.blackboxUrl,
});
const dec = await blackbox.payload.decryptPayload({
  chainId, secretId, encryptedMessage: enc.encryptedMessage, cifer: enc.cifer,
  signer, readClient: sdk.readClient, blackboxUrl: sdk.blackboxUrl,
});
console.log(dec.decryptedMessage); // "Hello CIFER!"
```
