# Simple Airdrop (<10,000 recipients)

Single transaction approach for small distributions.

## Full Example

```typescript
import {
  CompressedTokenProgram,
  getTokenPoolInfos,
  selectTokenPoolInfo,
} from "@lightprotocol/compressed-token";
import {
  bn,
  buildAndSignTx,
  calculateComputeUnitPrice,
  createRpc,
  dedupeSigner,
  selectStateTreeInfo,
  sendAndConfirmTx,
} from "@lightprotocol/stateless.js";
import { ComputeBudgetProgram, Keypair, PublicKey } from "@solana/web3.js";
import { getOrCreateAssociatedTokenAccount } from "@solana/spl-token";

const RPC_ENDPOINT = "https://devnet.helius-rpc.com?api-key=YOUR_KEY";
const rpc = createRpc(RPC_ENDPOINT);
const mint = new PublicKey("YOUR_MINT_ADDRESS");

// Define recipients and amounts
const recipients = [
  new PublicKey("..."),
  new PublicKey("..."),
  new PublicKey("..."),
];

const amounts = [
  bn(20_000_000_000), // 20 tokens (9 decimals)
  bn(30_000_000_000), // 30 tokens
  bn(40_000_000_000), // 40 tokens
];

// Get infrastructure
const treeInfo = selectStateTreeInfo(await rpc.getStateTreeInfos());
const tokenPoolInfo = selectTokenPoolInfo(await getTokenPoolInfos(rpc, mint));
const sourceAta = await getOrCreateAssociatedTokenAccount(rpc, payer, mint, payer.publicKey);

// Build transaction
const units = 120_000 * recipients.length;
const instructions = [
  ComputeBudgetProgram.setComputeUnitLimit({ units }),
  ComputeBudgetProgram.setComputeUnitPrice({
    microLamports: calculateComputeUnitPrice(20_000, units),
  }),
  await CompressedTokenProgram.compress({
    payer: payer.publicKey,
    owner: payer.publicKey,
    source: sourceAta.address,
    toAddress: recipients,
    amount: amounts,
    mint,
    tokenPoolInfo,
    outputStateTreeInfo: treeInfo,
  }),
];

// Use lookup table to reduce tx size
const lut = new PublicKey("9NYFyEqPkyXUhkerbGHXUXkvb4qpzeEdHuGpgbgpH1NJ"); // mainnet
// const lut = new PublicKey("qAJZMgnQJ8G6vA3WRcjD9Jan1wtKkaCFWLWskxJrR5V"); // devnet
const lookupTable = (await rpc.getAddressLookupTable(lut)).value!;

const { blockhash } = await rpc.getLatestBlockhash();
const tx = buildAndSignTx(
  instructions,
  payer,
  blockhash,
  dedupeSigner(payer, []),
  [lookupTable]
);
const txId = await sendAndConfirmTx(rpc, tx);
console.log(`Airdrop complete: ${txId}`);
```

## Verify Distribution

```typescript
for (const recipient of recipients) {
  const accounts = await rpc.getCompressedTokenAccountsByOwner(recipient, { mint });
  const balance = accounts.items.reduce((sum, acc) => sum + Number(acc.parsed.amount), 0);
  console.log(`${recipient}: ${balance / 1e9} tokens`);
}
```

## Same Amount to All Recipients

```typescript
const amount = bn(1_000_000_000); // 1 token each

const ix = await CompressedTokenProgram.compress({
  payer: payer.publicKey,
  owner: payer.publicKey,
  source: sourceAta.address,
  toAddress: recipients,
  amount: recipients.map(() => amount), // Same amount for all
  mint,
  tokenPoolInfo,
  outputStateTreeInfo: treeInfo,
});
```

## Source

- [examples-light-token](https://github.com/Lightprotocol/examples-light-token)
