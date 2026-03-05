# Signing with Privy

Privy is an embedded wallet provider — it creates and manages wallets on behalf of users. The light-token instruction-building code is the same as any other integration. The difference is the sign-and-send flow:

1. Build unsigned transaction with light-token instructions
2. Serialize and send to Privy for signing
3. Sign with Privy SDK
4. Submit signed bytes via `sendRawTransaction()`

## Node.js

### Dependencies

```bash
npm install @privy-io/node @lightprotocol/stateless.js @lightprotocol/compressed-token @solana/web3.js
```

### Sign pattern

```typescript
import {PrivyClient} from '@privy-io/node';
import {createRpc} from '@lightprotocol/stateless.js';
import {PublicKey, Transaction} from '@solana/web3.js';
import {
  createTransferInterfaceInstruction,
  getAssociatedTokenAddressInterface,
} from '@lightprotocol/compressed-token/unified';

const connection = createRpc(process.env.HELIUS_RPC_URL!);
const privy = new PrivyClient({
  appId: process.env.PRIVY_APP_ID!,
  appSecret: process.env.PRIVY_APP_SECRET!,
});

// Build instructions (same as any other integration)
const sourceAta = getAssociatedTokenAddressInterface(mint, fromPubkey);
const destAta = getAssociatedTokenAddressInterface(mint, toPubkey);
const instruction = createTransferInterfaceInstruction(sourceAta, destAta, fromPubkey, amount);

// Build transaction
const transaction = new Transaction();
transaction.add(instruction);
const {blockhash} = await connection.getLatestBlockhash();
transaction.recentBlockhash = blockhash;
transaction.feePayer = fromPubkey;

// Serialize unsigned, sign with Privy
const signResult = await privy.wallets().solana().signTransaction(
  process.env.TREASURY_WALLET_ID!,
  {
    transaction: transaction.serialize({requireAllSignatures: false}),
    authorization_context: {
      authorization_private_keys: [process.env.TREASURY_AUTHORIZATION_KEY!]
    }
  }
);
const signedTransaction = Buffer.from((signResult as any).signed_transaction, 'base64');

// Send
const signature = await connection.sendRawTransaction(signedTransaction, {
  skipPreflight: false,
  preflightCommitment: 'confirmed'
});
```

Source: `examples-light-token/privy/nodejs-privy-light-token/src/transfer.ts`

## React

### Dependencies

```bash
npm install @privy-io/react-auth @lightprotocol/stateless.js @lightprotocol/compressed-token @solana/web3.js
```

### Sign pattern

```typescript
import { useSignTransaction } from '@privy-io/react-auth/solana';
import { createRpc } from '@lightprotocol/stateless.js';
import { PublicKey, Transaction } from '@solana/web3.js';
import {
  createTransferInterfaceInstruction,
  getAssociatedTokenAddressInterface,
} from '@lightprotocol/compressed-token/unified';

const rpc = createRpc(import.meta.env.VITE_HELIUS_RPC_URL);

// Build instructions (same as any other integration)
const sourceAta = getAssociatedTokenAddressInterface(mint, owner);
const destAta = getAssociatedTokenAddressInterface(mint, recipient);
const transferIx = createTransferInterfaceInstruction(sourceAta, destAta, owner, amount);

// Build transaction
const { blockhash } = await rpc.getLatestBlockhash();
const transaction = new Transaction();
transaction.add(transferIx);
transaction.recentBlockhash = blockhash;
transaction.feePayer = owner;

// Serialize unsigned, sign with Privy
const unsignedTxBuffer = transaction.serialize({ requireAllSignatures: false });
const signedTx = await signTransaction({
  transaction: unsignedTxBuffer,
  wallet,
  chain: 'solana:devnet',
});

// Send
const signedTxBuffer = Buffer.from(signedTx.signedTransaction);
const signature = await rpc.sendRawTransaction(signedTxBuffer, {
  skipPreflight: false,
  preflightCommitment: 'confirmed',
});
```

Source: `examples-light-token/privy/react-privy-light-token/src/hooks/useTransfer.ts`

## Key differences from wallet adapters

| | Privy | Wallet Adapter / MWA |
|---|---|---|
| **Wallet ownership** | Privy creates and holds wallets | User owns their wallet |
| **Signing** | Serialize unsigned → send to Privy API → get signed bytes | Adapter handles signing internally or via `signTransaction()` |
| **Send** | `sendRawTransaction()` with signed bytes | `sendTransaction()` (built-in) or `sendRawTransaction()` |
| **Auth** | App ID + secret (Node.js) or SDK hook (React) | Browser extension or mobile app |

## Loading compressed accounts

When the source associated token account may be compressed, prepend load instructions:

```typescript
const loadIxs = await createLoadAtaInstructions(rpc, sourceAta, owner, mint, payer);

const tx = new Transaction();
if (loadIxs.length > 0) tx.add(...loadIxs);
tx.add(transferIx);
```

Returns empty array if account is already hot (on-chain).

## Source

- [Privy Node.js example](https://github.com/Lightprotocol/examples-light-token/tree/main/privy/nodejs-privy-light-token)
- [Privy React example](https://github.com/Lightprotocol/examples-light-token/tree/main/privy/react-privy-light-token)
