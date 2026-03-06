# CIFER SDK — Full API Reference

## SDK Initialization

### createCiferSdk(config) — Async with Auto-Discovery (Recommended)

```javascript
import { createCiferSdk } from 'cifer-sdk';

const sdk = await createCiferSdk({
  blackboxUrl: 'https://cifer-blackbox.ternoa.dev:3010',
  // Optional: override chain RPC or controller address
  chainOverrides: {
    1: { rpcUrl: 'https://my-rpc.example.com' },
  },
});

sdk.getSupportedChainIds();       // [1, 11155111, 752025]
sdk.getControllerAddress(1);      // '0xA60a2...'
sdk.getRpcUrl(1);                 // 'https://ethereum-rpc.publicnode.com'
sdk.blackboxUrl;                  // 'https://cifer-blackbox.ternoa.dev:3010'
sdk.readClient;                   // ReadClient instance for all SDK calls
```

### createCiferSdkSync(config) — Synchronous, No Discovery

```javascript
import { createCiferSdkSync, RpcReadClient } from 'cifer-sdk';

const readClient = new RpcReadClient({
  rpcUrlByChainId: { 1: 'https://ethereum-rpc.publicnode.com' },
});

const sdk = createCiferSdkSync({
  blackboxUrl: 'https://cifer-blackbox.ternoa.dev:3010',
  readClient,
  chainOverrides: {
    1: {
      rpcUrl: 'https://ethereum-rpc.publicnode.com',
      secretsControllerAddress: '0xA60a2f3fAb81411803F15acd6099e4fa6f625C30',
    },
  },
});
```

---

## Supported Chains

| Chain           | ID         | Native Token | Block Time |
|-----------------|------------|--------------|------------|
| Ethereum        | 1          | ETH          | ~12s       |
| Ethereum Sepolia| 11155111   | SepoliaETH   | ~12s       |
| Ternoa          | 752025     | CAPS         | ~6s        |

---

## Wallet Signer Adapters

All signers must implement:
```typescript
interface SignerAdapter {
  getAddress(): Promise<string>;
  signMessage(message: string): Promise<string>; // EIP-191 personal_sign
}
```

### Server-Side (ethers.js)
```javascript
import { Wallet } from 'ethers';
const wallet = new Wallet(process.env.PRIVATE_KEY);
const signer = {
  async getAddress() { return wallet.address; },
  async signMessage(message) { return wallet.signMessage(message); },
};
```

### Server-Side (viem)
```javascript
import { privateKeyToAccount } from 'viem/accounts';
const account = privateKeyToAccount(process.env.PRIVATE_KEY);
const signer = {
  async getAddress() { return account.address; },
  async signMessage(message) { return account.signMessage({ message }); },
};
```

### Browser (MetaMask / any EIP-1193)
```javascript
import { Eip1193SignerAdapter } from 'cifer-sdk';
await window.ethereum.request({ method: 'eth_requestAccounts' });
const signer = new Eip1193SignerAdapter(window.ethereum);
```

### Browser (WalletConnect v2)
```javascript
import { EthereumProvider } from '@walletconnect/ethereum-provider';
const provider = await EthereumProvider.init({
  projectId: 'YOUR_PROJECT_ID', chains: [1], showQrModal: true,
});
await provider.connect();
const signer = new Eip1193SignerAdapter(provider);
```

---

## keyManagement Namespace

### Read Operations

| Function | Returns | Description |
|----------|---------|-------------|
| `getSecretCreationFee(params)` | `bigint` (wei) | Fee to create a secret |
| `getSecret(params, secretId)` | `SecretState` | Full secret state |
| `isSecretReady(params, secretId)` | `boolean` | True if synced and has public key |
| `isAuthorized(params, secretId, address)` | `boolean` | True if owner or delegate |
| `getSecretsByWallet(params, wallet)` | `{ owned: bigint[], delegated: bigint[] }` | All secrets for wallet |
| `getSecretsCountByWallet(params, wallet)` | `{ ownedCount: bigint, delegatedCount: bigint }` | Counts only (gas efficient) |

All read functions take `params`: `{ chainId, controllerAddress, readClient }`.

### SecretState Object

```typescript
{
  owner: Address;           // Can transfer, delegate, encrypt, decrypt
  delegate: Address;        // Can decrypt only (zero address = none)
  isSyncing: boolean;       // True while enclave generates keys
  clusterId: number;        // Enclave cluster ID
  secretType: number;       // 1 = ML-KEM-768
  publicKeyCid: string;     // IPFS CID (empty if syncing)
}
```

### Transaction Builders

All return `TxIntent { chainId, to, data, value? }`. Execute with any wallet:

```javascript
await wallet.sendTransaction({ to: txIntent.to, data: txIntent.data, value: txIntent.value });
```

| Function | Params | Description |
|----------|--------|-------------|
| `buildCreateSecretTx({ chainId, controllerAddress, fee })` | fee from `getSecretCreationFee` | Create new secret (payable) |
| `buildSetDelegateTx({ chainId, controllerAddress, secretId, newDelegate })` | | Set/update delegate |
| `buildRemoveDelegationTx({ chainId, controllerAddress, secretId })` | | Remove delegate |
| `buildTransferSecretTx({ chainId, controllerAddress, secretId, newOwner })` | | Transfer ownership (irreversible) |

### Event Parsing

```javascript
const secretId = keyManagement.extractSecretIdFromReceipt(receipt.logs);
```

---

## blackbox.payload Namespace

### encryptPayload(params) → `{ cifer, encryptedMessage }`

```javascript
const result = await blackbox.payload.encryptPayload({
  chainId: 1,
  secretId: 3n,
  plaintext: 'message up to ~16KB',
  signer,
  readClient: sdk.readClient,
  blackboxUrl: sdk.blackboxUrl,
  outputFormat: 'hex',        // optional, default 'hex'. Also: 'base64'
});
```

### decryptPayload(params) → `{ decryptedMessage }`

```javascript
const result = await blackbox.payload.decryptPayload({
  chainId: 1,
  secretId: 3n,
  encryptedMessage: '0x...',  // from encryptPayload
  cifer: '0x...',             // from encryptPayload
  signer,                     // must be owner or delegate
  readClient: sdk.readClient,
  blackboxUrl: sdk.blackboxUrl,
  inputFormat: 'hex',         // must match outputFormat used at encryption
});
```

---

## blackbox.files Namespace

### encryptFile(params) → `{ jobId, message }`

```javascript
const job = await blackbox.files.encryptFile({
  chainId, secretId,
  file: blob,   // File or Blob
  signer, readClient: sdk.readClient, blackboxUrl: sdk.blackboxUrl,
});
```

### decryptFile(params) → `{ jobId, message }`

Accepts `.cifer` files produced by `encryptFile`.

```javascript
const job = await blackbox.files.decryptFile({
  chainId, secretId,
  file: ciferBlob,
  signer, readClient: sdk.readClient, blackboxUrl: sdk.blackboxUrl,
});
```

### decryptExistingFile(params) → `{ jobId, message }`

Decrypt from a previous encrypt job without re-uploading:

```javascript
const job = await blackbox.files.decryptExistingFile({
  chainId, secretId, encryptJobId: 'previous-job-id',
  signer, readClient: sdk.readClient, blackboxUrl: sdk.blackboxUrl,
});
```

---

## blackbox.jobs Namespace

### getStatus(jobId, blackboxUrl) → `JobInfo`

```javascript
const status = await blackbox.jobs.getStatus(jobId, sdk.blackboxUrl);
// status.status: 'pending' | 'processing' | 'completed' | 'failed' | 'expired'
// status.progress: 0-100
```

### pollUntilComplete(jobId, blackboxUrl, options?) → `JobInfo`

```javascript
const final = await blackbox.jobs.pollUntilComplete(jobId, sdk.blackboxUrl, {
  intervalMs: 2000,       // poll every 2s (default)
  maxAttempts: 60,        // give up after 60 polls (default)
  onProgress: (job) => console.log(`${job.progress}%`),
  abortSignal: controller.signal,  // optional AbortSignal
});
```

### download(jobId, params) → `Blob`

For **encrypt** jobs (no auth):
```javascript
const blob = await blackbox.jobs.download(jobId, { blackboxUrl: sdk.blackboxUrl });
```

For **decrypt** jobs (auth required):
```javascript
const blob = await blackbox.jobs.download(jobId, {
  blackboxUrl: sdk.blackboxUrl,
  chainId, secretId, signer, readClient: sdk.readClient,
});
```

### list(params) → `{ jobs: JobInfo[], count }`

```javascript
const result = await blackbox.jobs.list({
  chainId, signer, readClient: sdk.readClient,
  blackboxUrl: sdk.blackboxUrl,
  includeExpired: false,
});
```

### deleteJob(jobId, params) / dataConsumption(params)

Mark job for cleanup or check usage stats.

---

## flows Namespace (High-Level)

Flows combine multiple operations. Support `plan` (dry run) and `execute` modes.

### createSecretAndWaitReady(ctx)

```javascript
import { flows } from 'cifer-sdk';

const result = await flows.createSecretAndWaitReady({
  signer, readClient: sdk.readClient, blackboxUrl: sdk.blackboxUrl,
  chainId: 1,
  controllerAddress: sdk.getControllerAddress(1),
  txExecutor: async (intent) => {
    const tx = await wallet.sendTransaction({
      to: intent.to, data: intent.data, value: intent.value,
    });
    return { hash: tx.hash, waitReceipt: () => tx.wait() };
  },
  logger: console.log,
});

if (result.success) {
  console.log('Secret ID:', result.data.secretId);
}
```

### encryptFileJobFlow / decryptFileJobFlow

```javascript
const result = await flows.encryptFileJobFlow(ctx, { secretId, file: blob });
if (result.success) {
  // result.data.encryptedFile is a Blob
}
```

---

## Error Hierarchy

| Error | Code | When |
|-------|------|------|
| `ConfigError` | CONFIG_ERROR | Bad config, discovery failed |
| `BlockStaleError` | AUTH_ERROR | Block too old (auto-retried 3x) |
| `SecretNotReadyError` | BLACKBOX_ERROR | Secret still syncing |
| `SecretNotFoundError` | KEY_MANAGEMENT_ERROR | Secret ID doesn't exist |
| `NotAuthorizedError` | KEY_MANAGEMENT_ERROR | Signer not owner/delegate |
| `EncryptionError` | BLACKBOX_ERROR | Encrypt API failed |
| `DecryptionError` | BLACKBOX_ERROR | Decrypt API failed |
| `PayloadTooLargeError` | COMMITMENTS_ERROR | Message > 16KB |

Use type guards:
```javascript
import { isCiferError, isBlockStaleError } from 'cifer-sdk';
```

---

## Constants

```javascript
CIFER_ENVELOPE_BYTES = 1104   // Fixed size of cifer field (ML-KEM ciphertext + tag)
MAX_PAYLOAD_BYTES = 16384     // Max encrypted message (16KB)
```

---

## Node.js Blob/File Handling

In Node.js 18+, `Blob` is global. For file encryption:

```javascript
import { readFile, writeFile } from 'fs/promises';

// Reading a file into a Blob
const buffer = await readFile('input.pdf');
const blob = new Blob([buffer], { type: 'application/pdf' });

// Saving a Blob back to file
const resultBlob = await blackbox.jobs.download(jobId, params);
const resultBuffer = Buffer.from(await resultBlob.arrayBuffer());
await writeFile('output.pdf', resultBuffer);
```
