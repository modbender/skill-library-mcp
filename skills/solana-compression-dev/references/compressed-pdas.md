# Compressed PDAs

Build Solana programs with compressed Program Derived Addresses (PDAs) for rent-free accounts with persistent identification.

## Overview

| Aspect | Regular PDA | Compressed PDA |
|--------|-------------|----------------|
| 100-byte account | ~1,600,000 lamports | ~15,000 lamports |
| Rent | Required | None |
| Address derivation | `find_program_address` | `v2::derive_address` |
| State updates | In-place mutation | Consume + create new |

## Prerequisites

### Required versions

- Rust: 1.86.0+
- Solana CLI: 2.2.15+
- Anchor CLI: 0.31.1+
- ZK Compression CLI: latest (`npm install -g @lightprotocol/zk-compression-cli`)
- Node.js: 23.5.0+

### Installation

```bash
# Install ZK compression CLI
npm install -g @lightprotocol/zk-compression-cli

# Initialize new project with compression support
light init my-program
cd my-program
```

## Project structure

```
my-program/
├── Anchor.toml
├── Cargo.toml
├── programs/
│   └── my-program/
│       ├── Cargo.toml
│       └── src/
│           └── lib.rs
├── tests/
│   └── my-program.ts
└── package.json
```

### Cargo.toml dependencies

```toml
[dependencies]
anchor-lang = "0.31.1"
light-sdk = { version = "0.19.0", features = ["anchor", "v2", "anchor-discriminator", "cpi-context"] }
light-sdk-types = { version = "0.19.0", features = ["v2", "cpi-context"] }
light-sdk-macros = "0.19.0"

[dev-dependencies]
light-program-test = "0.19.0"
light-client = { version = "0.19.0", features = ["v2", "anchor"] }
```

## Program setup

### Constants

Define the CPI signer constant that the Light System Program uses to verify your program's authority:

```rust
use light_sdk::cpi::{CpiSigner};
use light_sdk::derive_light_cpi_signer;

declare_id!("YourProgramID11111111111111111111111111111");

pub const LIGHT_CPI_SIGNER: CpiSigner =
    derive_light_cpi_signer!("YourProgramID11111111111111111111111111111");
```

`derive_light_cpi_signer!` derives a PDA from your program ID. The Light System Program checks this PDA to authorize CPI calls from your program.

### Anchor account struct

Compressed account programs only need a signer in the Anchor account struct. All Light System Program accounts and Merkle tree accounts are passed via `remaining_accounts`:

```rust
#[derive(Accounts)]
pub struct GenericAnchorAccounts<'info> {
    #[account(mut)]
    pub signer: Signer<'info>,
}
```

### Account data struct

Define your compressed account data with `LightDiscriminator`:

```rust
use light_sdk::LightDiscriminator;

// #[event] makes the struct available in the Anchor IDL.
#[event]
#[derive(Clone, Debug, Default, LightDiscriminator)]
pub struct MyCompressedAccount {
    pub owner: Pubkey,
    pub message: String,
}
```

Required derive macros:
- `LightDiscriminator` - derives a unique 8-byte discriminator for the compressed account
- `Clone`, `Debug`, `Default` - standard Rust traits
- `AnchorSerialize`, `AnchorDeserialize` - added by `#[event]`

## Create

Create a new compressed account with a derived address.

`LightAccount::new_init` allocates a new compressed account with an address. The address is derived from seeds, the address tree, and your program ID - similar to `find_program_address` for regular PDAs.

```rust
#![allow(unexpected_cfgs)]
#![allow(deprecated)]

use anchor_lang::{prelude::*, AnchorDeserialize, AnchorSerialize};
use light_sdk::{
    account::LightAccount,
    address::v2::derive_address,
    cpi::{v2::CpiAccounts, CpiSigner},
    derive_light_cpi_signer,
    instruction::{PackedAddressTreeInfo, ValidityProof},
    LightDiscriminator,
};
use light_sdk_types::ADDRESS_TREE_V2;

declare_id!("Hps5oaKdYWqjVZJnAxUE1uwbozwEgZZGCRA57p2wdqcS");

pub const LIGHT_CPI_SIGNER: CpiSigner =
    derive_light_cpi_signer!("Hps5oaKdYWqjVZJnAxUE1uwbozwEgZZGCRA57p2wdqcS");

#[program]
pub mod create {

    use super::*;
    use light_sdk::cpi::{
        v2::LightSystemProgramCpi, InvokeLightSystemProgram, LightCpiInstruction,
    };

    /// Creates a new compressed account
    pub fn create_account<'info>(
        ctx: Context<'_, '_, '_, 'info, GenericAnchorAccounts<'info>>,
        proof: ValidityProof,
        address_tree_info: PackedAddressTreeInfo,
        output_state_tree_index: u8,
        message: String,
    ) -> Result<()> {
        // 1. Parse remaining_accounts for Light System Program CPI
        let light_cpi_accounts = CpiAccounts::new(
            ctx.accounts.signer.as_ref(),
            ctx.remaining_accounts,
            crate::LIGHT_CPI_SIGNER,
        );

        // 2. Validate address tree
        let address_tree_pubkey = address_tree_info
            .get_tree_pubkey(&light_cpi_accounts)
            .map_err(|_| ErrorCode::AccountNotEnoughKeys)?;

        if address_tree_pubkey.to_bytes() != ADDRESS_TREE_V2 {
            msg!("Invalid address tree");
            return Err(ProgramError::InvalidAccountData.into());
        }

        // 3. Derive the compressed PDA address
        let (address, address_seed) = derive_address(
            &[b"message", ctx.accounts.signer.key().as_ref()],
            &address_tree_pubkey,
            &crate::ID,
        );

        // 4. Create the compressed account
        let mut my_compressed_account = LightAccount::<MyCompressedAccount>::new_init(
            &crate::ID,
            Some(address),
            output_state_tree_index,
        );

        // 5. Set account data
        my_compressed_account.owner = ctx.accounts.signer.key();
        my_compressed_account.message = message.clone();

        msg!(
            "Created compressed account with message: {}",
            my_compressed_account.message
        );

        // 6. Invoke Light System Program
        LightSystemProgramCpi::new_cpi(LIGHT_CPI_SIGNER, proof)
            .with_light_account(my_compressed_account)?
            .with_new_addresses(&[address_tree_info.into_new_address_params_assigned_packed(address_seed, Some(0))])
            .invoke(light_cpi_accounts)?;

        Ok(())
    }
}

#[derive(Accounts)]
pub struct GenericAnchorAccounts<'info> {
    #[account(mut)]
    pub signer: Signer<'info>,
}

// declared as event so that it is part of the idl.
#[event]
#[derive(Clone, Debug, Default, LightDiscriminator)]
pub struct MyCompressedAccount {
    pub owner: Pubkey,
    pub message: String,
}
```

### Address derivation

```rust
use light_sdk::address::v2::derive_address;

// Seeds work like regular PDAs
let (address, address_seed) = derive_address(
    &[
        b"my_prefix",           // Static seed
        user.key().as_ref(),    // Dynamic seed
    ],
    &address_tree_pubkey,       // Address tree (from CPI accounts)
    &program_id,                // Your program ID
);
```

Different address trees produce different addresses from identical seeds. Check `ADDRESS_TREE_V2` in your program:

```rust
use light_sdk_types::ADDRESS_TREE_V2;

if address_tree_pubkey.to_bytes() != ADDRESS_TREE_V2 {
    return Err(ProgramError::InvalidAccountData.into());
}
```

### Address params

Use `into_new_address_params_assigned_packed` to create address parameters for the CPI:

```rust
let new_address_params = address_tree_info
    .into_new_address_params_assigned_packed(address_seed, Some(0));
```

The second argument (`Some(0)`) assigns the address to the first `LightAccount` in the CPI (index 0).

## Update

Update an existing compressed account. The client passes the current account data and a `CompressedAccountMeta` that references the account in the state tree.

`LightAccount::new_mut` consumes the existing account hash and creates a new output hash with updated data:

```rust
use light_sdk::instruction::account_meta::CompressedAccountMeta;

/// Updates an existing compressed account's message
pub fn update_account<'info>(
    ctx: Context<'_, '_, '_, 'info, GenericAnchorAccounts<'info>>,
    proof: ValidityProof,
    current_account: MyCompressedAccount,
    account_meta: CompressedAccountMeta,
    new_message: String,
) -> Result<()> {
    let light_cpi_accounts = CpiAccounts::new(
        ctx.accounts.signer.as_ref(),
        ctx.remaining_accounts,
        crate::LIGHT_CPI_SIGNER,
    );

    // new_mut consumes input state and creates output state
    let mut my_compressed_account = LightAccount::<MyCompressedAccount>::new_mut(
        &crate::ID,
        &account_meta,
        current_account,
    )?;

    my_compressed_account.message = new_message.clone();

    msg!(
        "Updated compressed account message to: {}",
        my_compressed_account.message
    );

    LightSystemProgramCpi::new_cpi(LIGHT_CPI_SIGNER, proof)
        .with_light_account(my_compressed_account)?
        .invoke(light_cpi_accounts)?;

    Ok(())
}
```

`CompressedAccountMeta` contains:
- `tree_info: PackedStateTreeInfo` - references the existing account hash in the state tree
- `address` - the account's derived address
- `output_state_tree_index` - the state tree to store the updated account hash

## Close

Close a compressed account. The account address can be reinitialized later with `new_empty()`.

`LightAccount::new_close` consumes the existing account hash and writes a zeroed-out hash. No output data:

```rust
/// Close compressed account
pub fn close_account<'info>(
    ctx: Context<'_, '_, '_, 'info, GenericAnchorAccounts<'info>>,
    proof: ValidityProof,
    account_meta: CompressedAccountMeta,
    current_message: String,
) -> Result<()> {
    let light_cpi_accounts = CpiAccounts::new(
        ctx.accounts.signer.as_ref(),
        ctx.remaining_accounts,
        crate::LIGHT_CPI_SIGNER,
    );

    // new_close hashes input state, writes zero-value output
    let my_compressed_account = LightAccount::<MyCompressedAccount>::new_close(
        &crate::ID,
        &account_meta,
        MyCompressedAccount {
            owner: ctx.accounts.signer.key(),
            message: current_message,
        },
    )?;

    msg!("Close compressed account.");

    LightSystemProgramCpi::new_cpi(LIGHT_CPI_SIGNER, proof)
        .with_light_account(my_compressed_account)?
        .invoke(light_cpi_accounts)?;

    Ok(())
}
```

A closed account retains its address. The zero-value hash remains in the state tree and can be consumed by `new_empty()` to reinitialize.

## Burn

Burn a compressed account permanently. A burned account cannot be reinitialized.

`LightAccount::new_burn` consumes the existing account hash and produces no output state:

```rust
use light_sdk::instruction::account_meta::CompressedAccountMetaBurn;

/// Burns a compressed account permanently
pub fn burn_account<'info>(
    ctx: Context<'_, '_, '_, 'info, GenericAnchorAccounts<'info>>,
    proof: ValidityProof,
    account_meta: CompressedAccountMetaBurn,
    current_message: String,
) -> Result<()> {
    let light_cpi_accounts = CpiAccounts::new(
        ctx.accounts.signer.as_ref(),
        ctx.remaining_accounts,
        crate::LIGHT_CPI_SIGNER,
    );

    // new_burn hashes input state, creates no output state
    let my_compressed_account = LightAccount::<MyCompressedAccount>::new_burn(
        &crate::ID,
        &account_meta,
        MyCompressedAccount {
            owner: ctx.accounts.signer.key(),
            message: current_message,
        },
    )?;

    msg!("Burning compressed account permanently");

    LightSystemProgramCpi::new_cpi(LIGHT_CPI_SIGNER, proof)
        .with_light_account(my_compressed_account)?
        .invoke(light_cpi_accounts)?;

    Ok(())
}
```

Key differences from close:
- Uses `CompressedAccountMetaBurn` instead of `CompressedAccountMeta` (no `output_state_tree_index`)
- No output state tree required
- The account hash is nullified permanently with no zero-value hash written

## Reinitialize

Reinitialize a previously closed account at the same address.

`LightAccount::new_empty` reconstructs the closed account's zero-value hash as input and creates output state with default values:

```rust
/// Reinitialize closed compressed account
pub fn reinit_account<'info>(
    ctx: Context<'_, '_, '_, 'info, GenericAnchorAccounts<'info>>,
    proof: ValidityProof,
    account_meta: CompressedAccountMeta,
) -> Result<()> {
    let light_cpi_accounts = CpiAccounts::new(
        ctx.accounts.signer.as_ref(),
        ctx.remaining_accounts,
        crate::LIGHT_CPI_SIGNER,
    );

    // new_empty reconstructs zero-value input hash, creates default output
    let my_compressed_account = LightAccount::<MyCompressedAccount>::new_empty(
        &crate::ID,
        &account_meta,
    )?;

    msg!("Reinitializing closed compressed account");

    LightSystemProgramCpi::new_cpi(LIGHT_CPI_SIGNER, proof)
        .with_light_account(my_compressed_account)?
        .invoke(light_cpi_accounts)?;

    Ok(())
}
```

`new_empty()` initializes all fields to defaults: `Pubkey` as all zeros, numbers as `0`, strings as empty.

To set custom values, chain with `new_mut()` in the same or a separate transaction:

1. Reinitialize with `new_empty()` to create the account with defaults
2. Update with `new_mut()` to set custom values

> **Note:** Reinitialize only works on closed accounts (zero-value hash). Burned accounts cannot be reinitialized.

## Account data structures

### Required traits

```rust
use light_sdk::LightDiscriminator;

#[event]  // Makes struct available in Anchor IDL
#[derive(Clone, Debug, Default, LightDiscriminator)]
pub struct GamePlayer {
    pub wallet: Pubkey,
    pub game_id: [u8; 32],
    pub score: u64,
    pub level: u8,
}
```

- `LightDiscriminator` derives a unique 8-byte discriminator used by the Light System Program to identify the account type
- `#[event]` exposes the struct in the Anchor IDL for client deserialization
- `Default` is required for `new_empty()` (reinitialize)

## Multiple accounts in one transaction

Create multiple compressed accounts in a single transaction using a batch pattern:

```rust
pub fn batch_create<'info>(
    ctx: Context<'_, '_, '_, 'info, GenericAnchorAccounts<'info>>,
    proof: ValidityProof,
    address_tree_infos: Vec<PackedAddressTreeInfo>,
    output_state_tree_index: u8,
    count: u8,
) -> Result<()> {
    let light_cpi_accounts = CpiAccounts::new(
        ctx.accounts.signer.as_ref(),
        ctx.remaining_accounts,
        crate::LIGHT_CPI_SIGNER,
    );

    let mut accounts = Vec::new();
    let mut address_params = Vec::new();

    for i in 0..count {
        let tree_pubkey = address_tree_infos[i as usize]
            .get_tree_pubkey(&light_cpi_accounts)
            .map_err(|_| ErrorCode::AccountNotEnoughKeys)?;

        let (address, seed) = derive_address(
            &[b"batch", &[i]],
            &tree_pubkey,
            &crate::ID,
        );

        address_params.push(
            address_tree_infos[i as usize]
                .into_new_address_params_assigned_packed(seed, Some(i))
        );

        let mut account = LightAccount::<MyCompressedAccount>::new_init(
            &crate::ID,
            Some(address),
            output_state_tree_index,
        );
        account.owner = ctx.accounts.signer.key();
        accounts.push(account);
    }

    let mut cpi = LightSystemProgramCpi::new_cpi(LIGHT_CPI_SIGNER, proof)
        .with_new_addresses(&address_params);

    for account in accounts {
        cpi = cpi.with_light_account(account)?;
    }

    cpi.invoke(light_cpi_accounts)?;

    Ok(())
}
```

The `Some(i)` parameter in `into_new_address_params_assigned_packed` assigns each address to its corresponding `LightAccount` by index.

## Testing

### Rust integration test

```rust
#![cfg(feature = "test-sbf")]

use anchor_lang::AnchorDeserialize;
use light_program_test::{
    program_test::LightProgramTest, AddressWithTree, Indexer, ProgramTestConfig, Rpc, RpcError,
};
use light_sdk::{
    address::v2::derive_address,
    instruction::{PackedAccounts, SystemAccountMetaConfig},
};
use create::MyCompressedAccount;
use solana_sdk::{
    instruction::{AccountMeta, Instruction},
    signature::{Keypair, Signature, Signer},
};

#[tokio::test]
async fn test_create() {
    let config = ProgramTestConfig::new(true, Some(vec![("create", create::ID)]));
    let mut rpc = LightProgramTest::new(config).await.unwrap();
    let payer = rpc.get_payer().insecure_clone();

    let address_tree_info = rpc.get_address_tree_v2();

    let (address, _) = derive_address(
        &[b"message", payer.pubkey().as_ref()],
        &address_tree_info.tree,
        &create::ID,
    );

    create_compressed_account(&mut rpc, &payer, &address, "Hello, compressed world!".to_string())
        .await
        .unwrap();

    let compressed_account = rpc
        .get_compressed_account(address, None)
        .await
        .unwrap()
        .value
        .unwrap();
    let data = &compressed_account.data.as_ref().unwrap().data;
    let account = MyCompressedAccount::deserialize(&mut &data[..]).unwrap();
    assert_eq!(account.owner, payer.pubkey());
    assert_eq!(account.message, "Hello, compressed world!");
}

async fn create_compressed_account(
    rpc: &mut LightProgramTest,
    payer: &Keypair,
    address: &[u8; 32],
    message: String,
) -> Result<Signature, RpcError> {
    let config = SystemAccountMetaConfig::new(create::ID);
    let mut remaining_accounts = PackedAccounts::default();
    remaining_accounts.add_system_accounts_v2(config)?;

    let address_tree_info = rpc.get_address_tree_v2();

    let rpc_result = rpc
        .get_validity_proof(
            vec![],
            vec![AddressWithTree {
                address: *address,
                tree: address_tree_info.tree,
            }],
            None,
        )
        .await?
        .value;
    let packed_accounts = rpc_result.pack_tree_infos(&mut remaining_accounts);

    let output_state_tree_index = rpc
        .get_random_state_tree_info()?
        .pack_output_tree_index(&mut remaining_accounts)?;

    let (remaining_accounts, _, _) = remaining_accounts.to_account_metas();

    let instruction = Instruction {
        program_id: create::ID,
        accounts: [
            vec![AccountMeta::new(payer.pubkey(), true)],
            remaining_accounts,
        ]
        .concat(),
        data: {
            use anchor_lang::InstructionData;
            create::instruction::CreateAccount {
                proof: rpc_result.proof,
                address_tree_info: packed_accounts.address_trees[0],
                output_state_tree_index: output_state_tree_index,
                message,
            }
            .data()
        },
    };

    rpc.create_and_send_transaction(&[instruction], &payer.pubkey(), &[payer])
        .await
}
```

### TypeScript integration test

```typescript
import * as anchor from "@coral-xyz/anchor";
import { Program, web3 } from "@coral-xyz/anchor";
import { Create } from "../target/types/create";
import idl from "../target/idl/create.json";
import {
  bn,
  confirmTx,
  createRpc,
  defaultTestStateTreeAccounts,
  deriveAddressV2,
  deriveAddressSeedV2,
  batchAddressTree,
  PackedAccounts,
  Rpc,
  sleep,
  SystemAccountMetaConfig,
  featureFlags,
  VERSION,
} from "@lightprotocol/stateless.js";
import * as assert from "assert";

// Force V2 mode
(featureFlags as any).version = VERSION.V2;

describe("test-anchor", () => {
  const program = anchor.workspace.Create as Program<Create>;
  const coder = new anchor.BorshCoder(idl as anchor.Idl);

  it("create compressed account", async () => {
    let signer = new web3.Keypair();
    let rpc = createRpc(
      "http://127.0.0.1:8899",
      "http://127.0.0.1:8784",
      "http://127.0.0.1:3001",
      { commitment: "confirmed" },
    );
    let lamports = web3.LAMPORTS_PER_SOL;
    await rpc.requestAirdrop(signer.publicKey, lamports);
    await sleep(2000);

    const outputStateTree = defaultTestStateTreeAccounts().merkleTree;
    const addressTree = new web3.PublicKey(batchAddressTree);

    const messageSeed = new TextEncoder().encode("message");
    const seed = deriveAddressSeedV2([messageSeed, signer.publicKey.toBytes()]);
    const address = deriveAddressV2(
      seed,
      addressTree,
      new web3.PublicKey(program.idl.address),
    );

    const txId = await createCompressedAccount(
      rpc,
      addressTree,
      address,
      program,
      outputStateTree,
      signer,
      "Hello, compressed world!",
    );
    console.log("Transaction ID:", txId);

    const slot = await rpc.getSlot();
    await rpc.confirmTransactionIndexed(slot);

    let compressedAccount = await rpc.getCompressedAccount(bn(address.toBytes()));
    let myAccount = coder.types.decode(
      "MyCompressedAccount",
      compressedAccount.data.data,
    );

    assert.ok(
      myAccount.owner.equals(signer.publicKey),
      "Owner should match signer public key"
    );
    assert.strictEqual(
      myAccount.message,
      "Hello, compressed world!",
      "Message should match the created message"
    );
  });
});

async function createCompressedAccount(
  rpc: Rpc,
  addressTree: anchor.web3.PublicKey,
  address: anchor.web3.PublicKey,
  program: anchor.Program<Create>,
  outputStateTree: anchor.web3.PublicKey,
  signer: anchor.web3.Keypair,
  message: string,
) {
  const proofRpcResult = await rpc.getValidityProofV0(
    [],
    [
      {
        tree: addressTree,
        queue: addressTree,
        address: bn(address.toBytes()),
      },
    ],
  );
  const systemAccountConfig = new SystemAccountMetaConfig(program.programId);
  let remainingAccounts = new PackedAccounts();
  remainingAccounts.addSystemAccountsV2(systemAccountConfig);

  const addressMerkleTreePubkeyIndex =
    remainingAccounts.insertOrGet(addressTree);
  const addressQueuePubkeyIndex = addressMerkleTreePubkeyIndex;
  const packedAddressTreeInfo = {
    rootIndex: proofRpcResult.rootIndices[0],
    addressMerkleTreePubkeyIndex,
    addressQueuePubkeyIndex,
  };
  const outputStateTreeIndex =
    remainingAccounts.insertOrGet(outputStateTree);
  let proof = {
    0: proofRpcResult.compressedProof,
  };
  const computeBudgetIx = web3.ComputeBudgetProgram.setComputeUnitLimit({
    units: 1000000,
  });
  let tx = await program.methods
    .createAccount(proof, packedAddressTreeInfo, outputStateTreeIndex, message)
    .accounts({
      signer: signer.publicKey,
    })
    .preInstructions([computeBudgetIx])
    .remainingAccounts(remainingAccounts.toAccountMetas().remainingAccounts)
    .signers([signer])
    .transaction();
  tx.recentBlockhash = (await rpc.getRecentBlockhash()).blockhash;
  tx.sign(signer);

  const sig = await rpc.sendTransaction(tx, [signer]);
  await confirmTx(rpc, sig);
  return sig;
}
```

## Build and deploy

```bash
# Build program
anchor build

# Run tests
cargo test-sbf

# Deploy to devnet
anchor deploy --provider.cluster devnet
```

## Operation summary

| Operation | Constructor | Input state | Output state | Meta type | Can reinit? |
|-----------|------------|-------------|--------------|-----------|-------------|
| Create | `new_init` | None | New data | N/A | N/A |
| Update | `new_mut` | Current data | Modified data | `CompressedAccountMeta` | N/A |
| Close | `new_close` | Current data | Zero values | `CompressedAccountMeta` | Yes |
| Burn | `new_burn` | Current data | None | `CompressedAccountMetaBurn` | No |
| Reinitialize | `new_empty` | Zero values | Default values | `CompressedAccountMeta` | N/A |
