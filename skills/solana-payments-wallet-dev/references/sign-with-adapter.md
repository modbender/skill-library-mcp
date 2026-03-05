# Signing with wallet adapters

All wallet adapters follow the same pattern:

1. `createRpc()` for RPC connection
2. Build instructions with unified API (`getAssociatedTokenAddressInterface`, `createTransferInterfaceInstruction`, etc.)
3. Sign with adapter
4. Send transaction

For embedded wallet providers (Privy), see [sign-with-privy.md](sign-with-privy.md).

## Wallet Adapter (React)

### Dependencies

```bash
npm install @solana/wallet-adapter-react @solana/wallet-adapter-react-ui @lightprotocol/stateless.js @lightprotocol/compressed-token @solana/web3.js
```

### Sign pattern

```typescript
import { useConnection, useWallet } from '@solana/wallet-adapter-react';
import { createRpc } from '@lightprotocol/stateless.js';
import { PublicKey, Transaction } from '@solana/web3.js';
import {
  createTransferInterfaceInstruction,
  getAssociatedTokenAddressInterface,
} from '@lightprotocol/compressed-token/unified';

const { connection } = useConnection();
const { publicKey, sendTransaction } = useWallet();
const rpc = createRpc(connection.rpcEndpoint);

// Build instructions (same as any other adapter)
const sourceAta = getAssociatedTokenAddressInterface(mint, publicKey);
const destinationAta = getAssociatedTokenAddressInterface(mint, recipientPubkey);
const ix = createTransferInterfaceInstruction(sourceAta, destinationAta, publicKey, amount);

// Build transaction
const {
  context: { slot: minContextSlot },
  value: { blockhash, lastValidBlockHeight },
} = await connection.getLatestBlockhashAndContext();

const transaction = new Transaction({
  feePayer: publicKey,
  recentBlockhash: blockhash,
}).add(ix);

// sendTransaction handles signing internally — no manual serialization
const signature = await sendTransaction(transaction, connection, { minContextSlot });
await connection.confirmTransaction({ blockhash, lastValidBlockHeight, signature });
```

Source: `wallet-adapter/packages/starter/light-example/src/components/SendForm.tsx`

## Mobile Wallet Adapter (React Native)

### Dependencies

```bash
npm install @solana-mobile/mobile-wallet-adapter-protocol-kit @lightprotocol/stateless.js @lightprotocol/compressed-token @solana/web3.js
```

### Sign pattern

```typescript
import { transact } from '@solana-mobile/mobile-wallet-adapter-protocol-kit';
import { createRpc } from '@lightprotocol/stateless.js';
import { PublicKey, Transaction } from '@solana/web3.js';
import {
  createTransferInterfaceInstruction,
  getAssociatedTokenAddressInterface,
  createLoadAtaInstructions,
} from '@lightprotocol/compressed-token/unified';

const rpc = createRpc(RPC_URL);

await transact(async wallet => {
  const freshAccount = await authorizeSession(wallet);
  const ownerPubkey = new PublicKey(freshAccount.address);

  // Build instructions (same as any other adapter)
  const sourceAta = getAssociatedTokenAddressInterface(mint, ownerPubkey);
  const destinationAta = getAssociatedTokenAddressInterface(mint, recipient);

  // Load source associated token account if compressed
  const loadIxs = await createLoadAtaInstructions(rpc, sourceAta, ownerPubkey, mint, ownerPubkey);
  const transferIx = createTransferInterfaceInstruction(sourceAta, destinationAta, ownerPubkey, amount);

  // Build transaction
  const { blockhash, lastValidBlockHeight } = await rpc.getLatestBlockhash();
  const tx = new Transaction();
  if (loadIxs.length > 0) tx.add(...loadIxs);
  tx.add(transferIx);
  tx.recentBlockhash = blockhash;
  tx.feePayer = ownerPubkey;

  // Serialize unsigned, sign with MWA
  const unsigned = tx.serialize({ requireAllSignatures: false });
  const [signedBytes] = await wallet.signTransactions({ transactions: [unsigned] });

  // Send
  const signature = await rpc.sendRawTransaction(signedBytes, {
    skipPreflight: false,
    preflightCommitment: 'confirmed',
  });
  await rpc.confirmTransaction({ blockhash, lastValidBlockHeight, signature });
});
```

Source: `mobile-wallet-adapter/examples/example-react-native-app/components/LightTokenTransferButton.tsx`

## Mobile Wallet Adapter (Web)

### Sign pattern

```typescript
import { useWallet } from '@solana/wallet-adapter-react';
import { createRpc } from '@lightprotocol/stateless.js';
import { PublicKey, Transaction } from '@solana/web3.js';
import {
  createTransferInterfaceInstruction,
  getAssociatedTokenAddressInterface,
  createLoadAtaInstructions,
} from '@lightprotocol/compressed-token/unified';

const { publicKey, signTransaction } = useWallet();
const rpc = createRpc(RPC_URL);

// Build instructions (same as any other adapter)
const sourceAta = getAssociatedTokenAddressInterface(mint, publicKey);
const destinationAta = getAssociatedTokenAddressInterface(mint, recipient);

// Load source associated token account if compressed
const loadIxs = await createLoadAtaInstructions(rpc, sourceAta, publicKey, mint, publicKey);
const transferIx = createTransferInterfaceInstruction(sourceAta, destinationAta, publicKey, amount);

// Build transaction
const { blockhash, lastValidBlockHeight } = await rpc.getLatestBlockhash();
const tx = new Transaction();
if (loadIxs.length > 0) tx.add(...loadIxs);
tx.add(transferIx);
tx.recentBlockhash = blockhash;
tx.feePayer = publicKey;

// Sign Transaction object directly, then serialize
const signedTx = await signTransaction(tx);
const signedBytes = signedTx.serialize();

// Send
const signature = await rpc.sendRawTransaction(signedBytes, {
  skipPreflight: false,
  preflightCommitment: 'confirmed',
});
await rpc.confirmTransaction({ blockhash, lastValidBlockHeight, signature });
```

Source: `mobile-wallet-adapter/examples/example-web-app/components/LightTokenTransferButton.tsx`

## Key differences

| Adapter | Serialization | Sign method | Send method |
| ------- | ------------- | ----------- | ----------- |
| Wallet Adapter | none (handled internally) | `sendTransaction(tx, connection)` | built-in |
| MWA React Native | serialize unsigned → bytes | `wallet.signTransactions()` | `sendRawTransaction()` |
| MWA Web | none (Transaction object) | `signTransaction(tx)` | `sendRawTransaction()` |

## Loading compressed accounts

When the source associated token account may be compressed, prepend load instructions:

```typescript
const loadIxs = await createLoadAtaInstructions(rpc, sourceAta, owner, mint, payer);

const tx = new Transaction();
if (loadIxs.length > 0) tx.add(...loadIxs);
tx.add(transferIx);
```

Returns empty array if account is already hot (on-chain).