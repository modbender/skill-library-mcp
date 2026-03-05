# Wallets

The light-token API matches SPL-token. Your users hold and receive tokens of the same mints, stored more efficiently.

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

## Receive tokens

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
  await sendAndConfirmTransaction(rpc, tx, [payer]);
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

## Send tokens

### Instruction

```typescript
import { Transaction } from "@solana/web3.js";
import { createTransferInterfaceInstructions } from "@lightprotocol/compressed-token/unified";

// Each inner array = one transaction. Usually just one.
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
  await sendAndConfirmTransaction(rpc, tx, [payer, owner]);
}
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

console.log(result.signatures);
console.log(result.solana);
console.log(result.compressed);
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

- [Wallets docs](https://zkcompression.com/light-token/toolkits/for-wallets)
- [GitHub examples](https://github.com/Lightprotocol/examples-light-token/tree/main/toolkits/payments-and-wallets)