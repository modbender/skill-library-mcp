# Payments

The light-token API matches SPL-token. Your users receive the same stablecoin, stored more efficiently.

| Creation cost     | SPL                 | light-token          |
| :---------------- | :------------------ | :------------------- |
| **Token Account** | ~2,000,000 lamports | ~**11,000** lamports |

## API comparison

| Operation | SPL | light-token (action / instruction) |
|-----------|-----|-------------------------------------|
| Receive | `getOrCreateAssociatedTokenAccount()` | `loadAta()` / `createLoadAtaInstructions()` |
| Transfer | `createTransferInstruction()` | `transferInterface()` / `createTransferInterfaceInstructions()` |
| Get balance | `getAccount()` | `getAtaInterface()` |
| Tx history | `getSignaturesForAddress()` | `rpc.getSignaturesForOwnerInterface()` |
| Wrap from SPL | N/A | `wrap()` / `createWrapInstruction()` |
| Unwrap to SPL | N/A | `unwrap()` / `createUnwrapInstructions()` |
| Register SPL mint | N/A | `createSplInterface()` / `LightTokenProgram.createSplInterface()` |
| Create mint | `createMint()` | `createMintInterface()` |

Full code examples: [payments-and-wallets](https://github.com/Lightprotocol/examples-light-token/tree/main/toolkits/payments-and-wallets)

## Setup

```bash
npm install @lightprotocol/compressed-token@beta @lightprotocol/stateless.js@beta @solana/web3.js @solana/spl-token
```

```typescript
import { createRpc } from "@lightprotocol/stateless.js";

import {
  createLoadAtaInstructions,
  loadAta,
  createTransferInterfaceInstructions,
  transferInterface,
  createUnwrapInstructions,
  unwrap,
  getAssociatedTokenAddressInterface,
  getAtaInterface,
  wrap,
} from "@lightprotocol/compressed-token/unified";

const rpc = createRpc(RPC_ENDPOINT);
```

## Register SPL mint

Before using light-token interface functions with an existing SPL mint, register it:

### Check if already registered

```typescript
import { getSplInterfaceInfos } from "@lightprotocol/compressed-token";

const infos = await getSplInterfaceInfos(rpc, mint);
const isRegistered = infos.some((i) => i.isInitialized);
```

### Register existing SPL mint (instruction)

```typescript
import { Transaction, sendAndConfirmTransaction } from "@solana/web3.js";
import { LightTokenProgram } from "@lightprotocol/compressed-token";
import { TOKEN_PROGRAM_ID } from "@solana/spl-token";

const ix = await LightTokenProgram.createSplInterface({
  feePayer: payer.publicKey,
  mint,
  tokenProgramId: TOKEN_PROGRAM_ID,
});

const tx = new Transaction().add(ix);
await sendAndConfirmTransaction(rpc, tx, [payer]);
```

### Register existing SPL mint (action)

```typescript
import { createSplInterface } from "@lightprotocol/compressed-token";

await createSplInterface(rpc, payer, mint);
```

### Create new SPL mint with interface

```typescript
import { createMintInterface } from "@lightprotocol/compressed-token/unified";
import { TOKEN_PROGRAM_ID } from "@solana/spl-token";

const { mint } = await createMintInterface(
  rpc, payer, payer, null, 9, undefined, undefined, TOKEN_PROGRAM_ID
);
```

## Receive payments

Load creates the associated token account if needed and loads any compressed state into it. Share the associated token account address with the sender.

> **About loading**: Light tokens reduce account rent ~200x by auto-compressing inactive accounts. Before any action, the SDK detects compressed state and adds instructions to load it back on-chain. This almost always fits in a single atomic transaction. APIs return `TransactionInstruction[][]` so the same loop handles the rare multi-transaction case automatically.

### Instruction

```typescript
import { Transaction } from "@solana/web3.js";
import {
  createLoadAtaInstructions,
  getAssociatedTokenAddressInterface,
} from "@lightprotocol/compressed-token/unified";

const ata = getAssociatedTokenAddressInterface(mint, recipient);

// Returns TransactionInstruction[][].
// Each inner array is one transaction.
// Almost always returns just one.
const instructions = await createLoadAtaInstructions(
  rpc,
  ata,
  recipient,
  mint,
  payer.publicKey
);

for (const ixs of instructions) {
  const tx = new Transaction().add(...ixs);

  // sign and send ...
}
```

### Action

```typescript
import {
  loadAta,
  getAssociatedTokenAddressInterface,
} from "@lightprotocol/compressed-token/unified";

const ata = getAssociatedTokenAddressInterface(mint, recipient);

const sig = await loadAta(rpc, ata, recipient, mint, payer);
if (sig) console.log("Loaded:", sig);
```

## Send payments

### Instruction

```typescript
import { Transaction } from "@solana/web3.js";
import { createTransferInterfaceInstructions } from "@lightprotocol/compressed-token/unified";

// Returns TransactionInstruction[][].
// Each inner array is one transaction.
// Almost always returns just one.
const instructions = await createTransferInterfaceInstructions(
  rpc,
  payer.publicKey,
  mint,
  amount,
  owner.publicKey,
  recipient
);

for (const ixs of instructions) {
  const tx = new Transaction().add(...ixs);

  // sign and send ...
}
```

Sign all transactions in one approval:

```typescript
const transactions = instructions.map((ixs) => new Transaction().add(...ixs));

// One approval for all
const signed = await wallet.signAllTransactions(transactions);

for (const tx of signed) {
  await sendAndConfirmTransaction(rpc, tx);
}
```

Optimize sending (parallel conditional loads, then transfer):

```typescript
import {
  createTransferInterfaceInstructions,
  sliceLast,
} from "@lightprotocol/compressed-token/unified";

const instructions = await createTransferInterfaceInstructions(
  rpc,
  payer.publicKey,
  mint,
  amount,
  owner.publicKey,
  recipient
);
const { rest: loadInstructions, last: transferInstructions } = sliceLast(instructions);
// empty = nothing to load, will no-op.
await Promise.all(
  loadInstructions.map((ixs) => {
    const tx = new Transaction().add(...ixs);
    tx.sign(payer, owner);
    return sendAndConfirmTransaction(rpc, tx);
  })
);

const transferTx = new Transaction().add(...transferInstructions);
transferTx.sign(payer, owner);
await sendAndConfirmTransaction(rpc, transferTx);
```

### Action

```typescript
import {
  getAssociatedTokenAddressInterface,
  transferInterface,
} from "@lightprotocol/compressed-token/unified";

const sourceAta = getAssociatedTokenAddressInterface(mint, owner.publicKey);

// Handles loading, creates recipient associated token account, transfers.
await transferInterface(rpc, payer, sourceAta, mint, recipient, owner, amount);
```

## Show balance

```typescript
import {
  getAssociatedTokenAddressInterface,
  getAtaInterface,
} from "@lightprotocol/compressed-token/unified";

const ata = getAssociatedTokenAddressInterface(mint, owner);
const account = await getAtaInterface(rpc, ata, owner, mint);

console.log(account.parsed.amount);
```

## Transaction history

```typescript
const result = await rpc.getSignaturesForOwnerInterface(owner);

console.log(result.signatures); // Merged + deduplicated
console.log(result.solana); // On-chain txs only
console.log(result.compressed); // Compressed txs only
```

Use `getSignaturesForAddressInterface(address)` for address-specific rather than owner-wide history.

## Wrap from SPL

### Instruction

```typescript
import { Transaction } from "@solana/web3.js";
import { getAssociatedTokenAddressSync } from "@solana/spl-token";
import {
  createWrapInstruction,
  getAssociatedTokenAddressInterface,
} from "@lightprotocol/compressed-token/unified";
import { getSplInterfaceInfos } from "@lightprotocol/compressed-token";

const splAta = getAssociatedTokenAddressSync(mint, owner.publicKey);
const tokenAta = getAssociatedTokenAddressInterface(mint, owner.publicKey);

const splInterfaceInfos = await getSplInterfaceInfos(rpc, mint);
const splInterfaceInfo = splInterfaceInfos.find((i) => i.isInitialized);

const tx = new Transaction().add(
  createWrapInstruction(
    splAta,
    tokenAta,
    owner.publicKey,
    mint,
    amount,
    splInterfaceInfo,
    decimals,
    payer.publicKey
  )
);
```

### Action helper

```typescript
import { getAssociatedTokenAddressSync } from "@solana/spl-token";
import {
  wrap,
  getAssociatedTokenAddressInterface,
} from "@lightprotocol/compressed-token/unified";

const splAta = getAssociatedTokenAddressSync(mint, owner.publicKey);
const tokenAta = getAssociatedTokenAddressInterface(mint, owner.publicKey);

await wrap(rpc, payer, splAta, tokenAta, owner, mint, amount);
```

## Unwrap to SPL

### Instruction

```typescript
import { Transaction } from "@solana/web3.js";
import { getAssociatedTokenAddressSync } from "@solana/spl-token";
import { createUnwrapInstructions } from "@lightprotocol/compressed-token/unified";

const splAta = getAssociatedTokenAddressSync(mint, owner.publicKey);

// Each inner array = one transaction. Handles loading + unwrapping together.
const instructions = await createUnwrapInstructions(
  rpc,
  splAta,
  owner.publicKey,
  mint,
  amount,
  payer.publicKey
);

for (const ixs of instructions) {
  const tx = new Transaction().add(...ixs);
  await sendAndConfirmTransaction(rpc, tx, [payer, owner]);
}
```

### Action

```typescript
import { getAssociatedTokenAddressSync } from "@solana/spl-token";
import { unwrap } from "@lightprotocol/compressed-token/unified";

const splAta = getAssociatedTokenAddressSync(mint, owner.publicKey);

await unwrap(rpc, payer, splAta, owner, mint, amount);
```

## Source

- [Payments docs](https://zkcompression.com/light-token/toolkits/for-payments)
- [GitHub examples](https://github.com/Lightprotocol/examples-light-token/tree/main/toolkits/payments-and-wallets)