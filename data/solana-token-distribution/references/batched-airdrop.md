# Batched Airdrop (10,000+ recipients)

For large-scale distributions with retry logic and blockhash management.

## Create Instruction Batches

```typescript
import {
  CompressedTokenProgram,
  TokenPoolInfo,
  selectTokenPoolInfo,
} from "@lightprotocol/compressed-token";
import {
  bn,
  selectStateTreeInfo,
  StateTreeInfo,
} from "@lightprotocol/stateless.js";
import {
  ComputeBudgetProgram,
  TransactionInstruction,
  PublicKey,
} from "@solana/web3.js";

interface CreateAirdropParams {
  amount: number | bigint;
  recipients: PublicKey[];
  payer: PublicKey;
  sourceTokenAccount: PublicKey;
  mint: PublicKey;
  stateTreeInfos: StateTreeInfo[];
  tokenPoolInfos: TokenPoolInfo[];
  maxRecipientsPerInstruction?: number;   // default: 5
  maxInstructionsPerTransaction?: number; // default: 3
  computeUnitLimit?: number;              // default: 500_000
  computeUnitPrice?: number;
}

export async function createAirdropInstructions({
  amount,
  recipients,
  payer,
  sourceTokenAccount,
  mint,
  stateTreeInfos,
  tokenPoolInfos,
  maxRecipientsPerInstruction = 5,
  maxInstructionsPerTransaction = 3,
  computeUnitLimit = 500_000,
  computeUnitPrice,
}: CreateAirdropParams): Promise<TransactionInstruction[][]> {
  const batches: TransactionInstruction[][] = [];
  const amountBn = bn(amount.toString());

  for (
    let i = 0;
    i < recipients.length;
    i += maxRecipientsPerInstruction * maxInstructionsPerTransaction
  ) {
    const instructions: TransactionInstruction[] = [];

    instructions.push(
      ComputeBudgetProgram.setComputeUnitLimit({ units: computeUnitLimit })
    );
    if (computeUnitPrice) {
      instructions.push(
        ComputeBudgetProgram.setComputeUnitPrice({ microLamports: computeUnitPrice })
      );
    }

    const treeInfo = selectStateTreeInfo(stateTreeInfos);
    const tokenPoolInfo = selectTokenPoolInfo(tokenPoolInfos);

    for (let j = 0; j < maxInstructionsPerTransaction; j++) {
      const startIdx = i + j * maxRecipientsPerInstruction;
      const recipientBatch = recipients.slice(
        startIdx,
        startIdx + maxRecipientsPerInstruction
      );

      if (recipientBatch.length === 0) break;

      instructions.push(
        await CompressedTokenProgram.compress({
          payer,
          owner: payer,
          source: sourceTokenAccount,
          toAddress: recipientBatch,
          amount: recipientBatch.map(() => amountBn),
          mint,
          tokenPoolInfo,
          outputStateTreeInfo: treeInfo,
        })
      );
    }

    if (instructions.length > (computeUnitPrice ? 2 : 1)) {
      batches.push(instructions);
    }
  }

  return batches;
}
```

## Background Blockhash Updater

```typescript
import { Rpc } from "@lightprotocol/stateless.js";

export let currentBlockhash: string;

export async function updateBlockhash(
  connection: Rpc,
  signal: AbortSignal
): Promise<void> {
  const { blockhash } = await connection.getLatestBlockhash();
  currentBlockhash = blockhash;

  (function updateInBackground() {
    if (signal.aborted) return;
    const timeoutId = setTimeout(async () => {
      if (signal.aborted) return;
      try {
        const { blockhash } = await connection.getLatestBlockhash();
        currentBlockhash = blockhash;
      } catch (error) {
        console.error("Failed to update blockhash:", error);
      }
      updateInBackground();
    }, 30_000);

    signal.addEventListener("abort", () => clearTimeout(timeoutId));
  })();
}
```

## Sign and Send with Retry

```typescript
import { Rpc, sendAndConfirmTx } from "@lightprotocol/stateless.js";
import {
  Keypair,
  PublicKey,
  TransactionMessage,
  VersionedTransaction,
} from "@solana/web3.js";
import { currentBlockhash, updateBlockhash } from "./update-blockhash";

export enum BatchResultType {
  Success = "success",
  Error = "error",
}

export type BatchResult =
  | { type: BatchResultType.Success; index: number; signature: string }
  | { type: BatchResultType.Error; index: number; error: string };

export async function* signAndSendAirdropBatches(
  batches: TransactionInstruction[][],
  payer: Keypair,
  connection: Rpc,
  maxRetries = 3
): AsyncGenerator<BatchResult> {
  const abortController = new AbortController();
  await updateBlockhash(connection, abortController.signal);

  // Lookup table for your network
  const lookupTableAddress = new PublicKey(
    "9NYFyEqPkyXUhkerbGHXUXkvb4qpzeEdHuGpgbgpH1NJ" // mainnet
    // "qAJZMgnQJ8G6vA3WRcjD9Jan1wtKkaCFWLWskxJrR5V" // devnet
  );
  const lookupTableAccount = (
    await connection.getAddressLookupTable(lookupTableAddress)
  ).value!;

  const statusMap = new Array(batches.length).fill(0); // 0 = pending

  while (statusMap.includes(0)) {
    const sends = statusMap.map(async (status, index) => {
      if (status !== 0) return;

      let retries = 0;
      while (retries < maxRetries && statusMap[index] === 0) {
        if (!currentBlockhash) {
          await new Promise((resolve) => setTimeout(resolve, 1000));
          continue;
        }

        try {
          const tx = new VersionedTransaction(
            new TransactionMessage({
              payerKey: payer.publicKey,
              recentBlockhash: currentBlockhash,
              instructions: batches[index],
            }).compileToV0Message([lookupTableAccount])
          );
          tx.sign([payer]);

          const confirmedSig = await sendAndConfirmTx(connection, tx, {
            skipPreflight: true,
            commitment: "confirmed",
          });

          if (confirmedSig) {
            statusMap[index] = 1;
            return { type: BatchResultType.Success, index, signature: confirmedSig };
          }
        } catch (e) {
          retries++;
          if (retries >= maxRetries) {
            statusMap[index] = `err: ${(e as Error).message}`;
            return { type: BatchResultType.Error, index, error: (e as Error).message };
          }
        }
      }
    });

    const results = await Promise.all(sends);
    for (const result of results) {
      if (result) yield result as BatchResult;
    }
  }

  abortController.abort();
}
```

## Main Airdrop Script

```typescript
import { Keypair, PublicKey } from "@solana/web3.js";
import { calculateComputeUnitPrice, createRpc } from "@lightprotocol/stateless.js";
import { createMint, getTokenPoolInfos } from "@lightprotocol/compressed-token";
import { getOrCreateAssociatedTokenAccount, mintTo } from "@solana/spl-token";
import { createAirdropInstructions } from "./create-instructions";
import { BatchResultType, signAndSendAirdropBatches } from "./sign-and-send";

const RPC_ENDPOINT = `https://mainnet.helius-rpc.com?api-key=${process.env.HELIUS_API_KEY}`;
const connection = createRpc(RPC_ENDPOINT);
const PAYER = Keypair.fromSecretKey(/* your key */);

const recipients = [
  // ... array of PublicKey addresses
].map((addr) => new PublicKey(addr));

(async () => {
  // Create mint
  const { mint } = await createMint(connection, PAYER, PAYER.publicKey, 9);

  // Mint supply
  const ata = await getOrCreateAssociatedTokenAccount(
    connection, PAYER, mint, PAYER.publicKey
  );
  await mintTo(connection, PAYER, mint, ata.address, PAYER.publicKey, 10e9 * 1e9);

  // Get infrastructure
  const stateTreeInfos = await connection.getStateTreeInfos();
  const tokenPoolInfos = await getTokenPoolInfos(connection, mint);

  // Create batches
  const batches = await createAirdropInstructions({
    amount: 1e6,
    recipients,
    payer: PAYER.publicKey,
    sourceTokenAccount: ata.address,
    mint,
    stateTreeInfos,
    tokenPoolInfos,
    computeUnitPrice: calculateComputeUnitPrice(10_000, 500_000),
  });

  // Execute
  for await (const result of signAndSendAirdropBatches(batches, PAYER, connection)) {
    if (result.type === BatchResultType.Success) {
      console.log(`Batch ${result.index}: ${result.signature}`);
    } else {
      console.error(`Batch ${result.index} failed: ${result.error}`);
    }
  }
})();
```

## Source

- [examples-light-token](https://github.com/Lightprotocol/examples-light-token)
