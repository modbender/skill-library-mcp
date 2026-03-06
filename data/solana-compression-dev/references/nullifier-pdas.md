# Nullifier PDAs

Create rent-free nullifier PDAs to prevent duplicate actions (double spending, replay attacks).

## Overview

| | |
|---|---|
| **Program ID** | `NFLx5WGPrTHHvdRNsidcrNcLxRruMC92E4yv7zhZBoT` |
| **Networks** | Mainnet, Devnet |
| **Source code** | [github.com/Lightprotocol/nullifier-program](https://github.com/Lightprotocol/nullifier-program/) |
| **Example Tx** | [Solana Explorer](https://explorer.solana.com/tx/38fA6kbKRcYb5XSez9ffQzfCcMbMHcaJGseCogShNXC5SemQsEo88ZMSPCLP9xv9PG8qSJnhWvWFqSYJnfBMLrpB) |

> **Note:** For the usage example source code, see [create_nullifier.rs](https://github.com/Lightprotocol/examples-light-token/blob/main/rust-client/actions/create_nullifier.rs#L25).

## How it works

1. Derives PDA from `["nullifier", id]` seeds (where `id` is your unique identifier, e.g. a nonce, uuid, hash of signature)
2. Creates an empty rent-free PDA at that address
3. If the address exists, the whole transaction fails
4. Prepend or append this instruction to your transaction

## Dependencies

### Rust

```toml
[dependencies]
light-nullifier-program = "0.1.2"
light-client = "0.19.0"
```

### TypeScript

```bash
npm install @lightprotocol/nullifier-program @lightprotocol/stateless.js@beta
```

## Using the helper

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

### TypeScript

```typescript
import { createNullifierIx } from "@lightprotocol/nullifier-program";
import { createRpc } from "@lightprotocol/stateless.js";
import { Transaction, SystemProgram, ComputeBudgetProgram } from "@solana/web3.js";

const rpc = createRpc("https://mainnet.helius-rpc.com/?api-key=...");

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

## Manual proof fetching

If you need more control over proof fetching and instruction building:

### Rust

```rust
use light_nullifier_program::sdk::{fetch_proof, build_instruction};

// Step 1: Fetch proof
let proof_result = fetch_proof(&mut rpc, &id).await?;

// Step 2: Build instruction
let nullifier_ix = build_instruction(payer.pubkey(), id, proof_result);

// Add to transaction
let tx = Transaction::new_signed_with_payer(
    &[nullifier_ix, transfer_ix],
    Some(&payer.pubkey()),
    &[&payer],
    recent_blockhash,
);
```

### TypeScript

```typescript
import { fetchProof, buildInstruction } from "@lightprotocol/nullifier-program";

// Step 1: Fetch proof
const proofResult = await fetchProof(rpc, id);

// Step 2: Build instruction
const nullifierIx = buildInstruction(payer.publicKey, id, proofResult);

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

## Check if nullifier exists

### Rust

```rust
use light_nullifier_program::sdk::derive_nullifier_address;

let address = derive_nullifier_address(&id);
let account = rpc.get_compressed_account(None, Some(address)).await?;
let exists = account.value.is_some();
```

### TypeScript

```typescript
import { deriveNullifierAddress } from "@lightprotocol/nullifier-program";
import { bn } from "@lightprotocol/stateless.js";

const address = deriveNullifierAddress(id);
const account = await rpc.getCompressedAccount(bn(address.toBytes()));
const exists = account !== null;
```

This is a reference implementation. Fork the program as you see fit.
