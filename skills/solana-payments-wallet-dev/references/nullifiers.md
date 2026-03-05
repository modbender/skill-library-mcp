# Nullifier PDAs

Prevent duplicate actions (e.g., double-spend) by creating a rent-free compressed PDA that fails if it already exists.
Prepend or append the nullifier instruction to your transaction.

## Program information

| | |
|---|---|
| **Program ID** | `NFLx5WGPrTHHvdRNsidcrNcLxRruMC92E4yv7zhZBoT` |
| **Networks** | Mainnet, Devnet |
| **Source code** | [github.com/Lightprotocol/nullifier-program](https://github.com/Lightprotocol/nullifier-program/) |

## How it works

1. Derives PDA from `["nullifier", id]` seeds (where `id` is a unique 32-byte identifier — nonce, UUID, hash of payment inputs, etc.)
2. Creates an empty rent-free compressed PDA at that address
3. If the address already exists, the entire transaction fails
4. Prepend or append this instruction to your transaction

## Dependencies

### TypeScript

```bash
npm install @lightprotocol/nullifier-program @lightprotocol/stateless.js@beta
```

### Rust

```toml
[dependencies]
light-nullifier-program = "0.1.2"
light-client = "0.19.0"
```

## Quick start

### TypeScript

```typescript
import { createNullifierIx } from "@lightprotocol/nullifier-program";
import { createRpc } from "@lightprotocol/stateless.js";
import { Transaction, SystemProgram, ComputeBudgetProgram } from "@solana/web3.js";

const rpc = createRpc(RPC_URL);

// Create a unique 32-byte ID (e.g., hash of payment inputs)
const id = new Uint8Array(32);
crypto.getRandomValues(id);

// Build nullifier instruction
const nullifierIx = await createNullifierIx(rpc, payer.publicKey, id);

// Combine with your transaction
const tx = new Transaction().add(
  nullifierIx,
  SystemProgram.transfer({
    fromPubkey: payer.publicKey,
    toPubkey: recipient,
    lamports: 1_000_000,
  })
);
```

### Rust

```rust
use light_nullifier_program::sdk::{create_nullifier_ix, PROGRAM_ID};
use light_client::{LightClient, LightClientConfig};
use solana_sdk::{system_instruction, transaction::Transaction};

let mut rpc = LightClient::new(
    LightClientConfig::new("https://mainnet.helius-rpc.com/?api-key=...")
).await?;

// Create a unique 32-byte ID
let id: [u8; 32] = /* hash of payment inputs or random */;

// Build nullifier instruction
let nullifier_ix = create_nullifier_ix(&mut rpc, payer.pubkey(), id).await?;

// Combine with your transaction
let transfer_ix = system_instruction::transfer(&payer.pubkey(), &recipient, 1_000_000);
let tx = Transaction::new_signed_with_payer(
    &[nullifier_ix, transfer_ix],
    Some(&payer.pubkey()),
    &[&payer],
    recent_blockhash,
);
```

## Manual proof fetching

When you need more control, fetch the proof and build the instruction separately.

### TypeScript

```typescript
import { fetchProof, buildInstruction } from "@lightprotocol/nullifier-program";

const proofResult = await fetchProof(rpc, id);
const nullifierIx = buildInstruction(payer.publicKey, id, proofResult);

const tx = new Transaction().add(
  nullifierIx,
  SystemProgram.transfer({
    fromPubkey: payer.publicKey,
    toPubkey: recipient,
    lamports: 1_000_000,
  })
);
```

### Rust

```rust
use light_nullifier_program::sdk::{fetch_proof, build_instruction};

let proof_result = fetch_proof(&mut rpc, &id).await?;
let nullifier_ix = build_instruction(payer.pubkey(), id, proof_result);

let tx = Transaction::new_signed_with_payer(
    &[nullifier_ix, transfer_ix],
    Some(&payer.pubkey()),
    &[&payer],
    recent_blockhash,
);
```

## Check if nullifier exists

### TypeScript

```typescript
import { deriveNullifierAddress } from "@lightprotocol/nullifier-program";
import { bn } from "@lightprotocol/stateless.js";

const address = deriveNullifierAddress(id);
const account = await rpc.getCompressedAccount(bn(address.toBytes()));
const exists = account !== null;
```

### Rust

```rust
use light_nullifier_program::sdk::derive_nullifier_address;

let address = derive_nullifier_address(&id);
let account = rpc.get_compressed_account(None, Some(address)).await?;
let exists = account.value.is_some();
```

## Complete examples

### TypeScript

```typescript
import "dotenv/config";
import * as crypto from "crypto";
import { Keypair, ComputeBudgetProgram, Transaction } from "@solana/web3.js";
import { createRpc, confirmTx } from "@lightprotocol/stateless.js";
import { createNullifierIx, deriveNullifierAddress } from "@lightprotocol/nullifier-program";

const rpc = createRpc(RPC_URL);

async function main() {
  // Generate random 32-byte identifier
  const id = new Uint8Array(crypto.randomBytes(32));

  // Build nullifier instruction
  const ix = await createNullifierIx(rpc, payer.publicKey, id);

  // Send transaction
  const computeIx = ComputeBudgetProgram.setComputeUnitLimit({ units: 1_000_000 });
  const tx = new Transaction().add(computeIx, ix);
  tx.recentBlockhash = (await rpc.getRecentBlockhash()).blockhash;
  tx.feePayer = payer.publicKey;
  tx.sign(payer);

  const sig = await rpc.sendTransaction(tx, [payer]);
  await confirmTx(rpc, sig);

  const address = deriveNullifierAddress(id);

  // Wait for indexer to process
  const slot = await rpc.getSlot();
  await rpc.confirmTransactionIndexed(slot);

  // Double-spend: same id fails
  try {
    await createNullifierIx(rpc, payer.publicKey, id);
    console.error("ERROR: duplicate nullifier should have failed");
  } catch {
    console.log("Double-spend correctly rejected");
  }
}
```

Source: `nullifier-program/examples/action-create-nullifier.ts`

### Rust

```rust
use light_client::rpc::{LightClient, LightClientConfig, Rpc};
use light_nullifier_program::sdk::{create_nullifier_ix, derive_nullifier_address};
use solana_sdk::signer::Signer;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let mut rpc = get_client().await?;
    let payer = rpc.get_payer().insecure_clone();

    // must be identifier, eg, nonce/UUID/hash of payment info
    let id: [u8; 32] = rand::random();
    let nullifier_ix = create_nullifier_ix(&mut rpc, payer.pubkey(), id).await?;

    let sig = rpc
        .create_and_send_transaction(&[nullifier_ix], &payer.pubkey(), &[&payer])
        .await?;
    println!("Tx: {}", sig);

    let _address = derive_nullifier_address(&id);

    // Double spend should fail
    assert!(create_nullifier_ix(&mut rpc, payer.pubkey(), id)
        .await
        .is_err());

    Ok(())
}
```

Source: `nullifier-program/examples/rust/src/main.rs`

## Source

- [Nullifier program repository](https://github.com/Lightprotocol/nullifier-program/)
- [Nullifier PDA guide](https://zkcompression.com/compressed-pdas/guides/how-to-create-nullifier-pdas)