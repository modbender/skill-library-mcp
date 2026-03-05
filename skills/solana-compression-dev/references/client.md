# Client guide

Build clients for compressed PDA programs in TypeScript and Rust.

## SDKs

| Language | Package | Description |
|----------|---------|-------------|
| TypeScript | [@lightprotocol/stateless.js](https://lightprotocol.github.io/light-protocol/stateless.js/index.html) | Client SDK for compressed accounts |
| TypeScript | [@lightprotocol/compressed-token](https://lightprotocol.github.io/light-protocol/compressed-token/index.html) | Client SDK for compressed tokens |
| Rust | [light-client](https://docs.rs/light-client) | Client SDK for compressed accounts and tokens |

## Key steps

1. **Derive a new address** or **fetch compressed account** for on-chain verification.
2. **Fetch validity proof** from the RPC that verifies a new address does not exist (create) and/or the account hash exists in the state tree (update, close, etc.).
3. **Pack accounts** with `PackedAccounts`. Instructions require Light System Program and Merkle tree accounts. `PackedAccounts` converts their pubkeys to `u8` indices pointing to accounts in the instruction.
4. **Build the instruction** with the current account data, new data, packed accounts and validity proof.

## Setup

### TypeScript

> **Note:** Use the [API documentation](https://lightprotocol.github.io/light-protocol/) to look up specific function signatures, parameters, and return types.

#### Installation

```bash
npm install --save \
    @lightprotocol/stateless.js \
    @lightprotocol/compressed-token \
    @solana/web3.js
```

#### RPC connection

`Rpc` extends Solana's web3.js `Connection` class with compression-related endpoints.

**Mainnet:**
```typescript
const rpc = createRpc('https://mainnet.helius-rpc.com/?api-key=YOUR_API_KEY');
```

**Devnet:**
```typescript
const rpc = createRpc('https://devnet.helius-rpc.com/?api-key=YOUR_API_KEY');
```

**Localnet:**
```bash
npm i -g @lightprotocol/zk-compression-cli
light test-validator
```

### Rust

#### Dependencies

```toml
[dependencies]
light-client = "0.19.0"
light-sdk = "0.19.0"
```

#### RPC connection

Connect to an RPC provider that supports ZK Compression (Helius, Triton).

**Mainnet:**
```rust
let config = LightClientConfig::new(
    "https://api.mainnet-beta.solana.com".to_string(),
    Some("https://mainnet.helius.xyz".to_string()),
    Some("YOUR_API_KEY".to_string())
);
let mut client = LightClient::new(config).await?;
client.payer = read_keypair_file("~/.config/solana/id.json")?;
```

**Devnet:**
```rust
let config = LightClientConfig::devnet(
    Some("https://devnet.helius-rpc.com".to_string()),
    Some("YOUR_API_KEY".to_string())
);
let mut client = LightClient::new(config).await?;
client.payer = read_keypair_file("~/.config/solana/id.json")?;
```

**Localnet:**
```rust
let config = LightClientConfig::local();
let mut client = LightClient::new(config).await?;
client.payer = read_keypair_file("~/.config/solana/id.json")?;
```

## Address derivation

Derive a persistent address as a unique identifier for your compressed account, similar to program-derived addresses (PDAs).

Derive addresses in two scenarios:
- **At account creation** - derive the address to create the account's persistent identifier, then pass it to `getValidityProofV0()` in the address array
- **Before building instructions** - derive the address to fetch existing accounts using `rpc.getCompressedAccount()`

### TypeScript

```typescript
const addressTree = await rpc.getAddressTreeInfoV2();
const seed = deriveAddressSeedV2(
  [Buffer.from('my-seed')]
);

const address = deriveAddressV2(
  seed,
  addressTree.tree,
  programId
);
```

### Rust

```rust
use light_sdk::address::v2::derive_address;

let address_tree_info = rpc.get_address_tree_v2();
let (address, _) = derive_address(
    &[b"my-seed"],
    &address_tree_info.tree,
    &program_id,
);
```

Like PDAs, compressed account addresses don't have a private key; they're derived from the program that owns them.

The key difference to PDAs: compressed addresses are stored in an address tree and include this tree in the address derivation. Different trees produce different addresses from identical seeds. Check the address tree in your program.

> **Note:** The protocol maintains Merkle trees. You don't need to initialize custom trees. Find the [pubkeys for Merkle trees here](https://www.zkcompression.com/resources/addresses-and-urls).

## Validity proof

Transactions with compressed accounts must include a validity proof:
- To **create** a compressed account, prove the **new address doesn't already exist** in the address tree.
- In **other instructions**, prove the **compressed account hash exists** in a state tree.
- **Combine multiple addresses and hashes in one proof** to optimize compute cost and instruction data.

> **Note:** Fetch a validity proof from your RPC provider that supports ZK Compression (Helius, Triton).

### Create proof

Prove that the new address does not exist in the address tree.

#### TypeScript

```typescript
const proof = await rpc.getValidityProofV0(
  [],
  [{
    address: bn(address.toBytes()),
    tree: addressTree.tree,
    queue: addressTree.queue
  }]
);
```

Parameters:
- Specify the new address, `tree` and `queue` pubkeys from the address tree `TreeInfo`.
- When creating an account you don't reference a compressed account hash in the hash array (`[]`). The account doesn't exist in a state Merkle tree yet.

Returns:
- The proof that the new address does not exist in the address tree.
- `rootIndices` array with root index that points to the root in the address tree accounts root history array.

#### Rust

```rust
let rpc_result = rpc
    .get_validity_proof(
        vec![],
        vec![AddressWithTree {
          address: *address,
          tree: address_tree_info.tree
        }],
        None,
    )
    .await?
    .value;
```

Parameters:
- Specify the new address and `tree` pubkey from the address tree `TreeInfo`. The `queue` pubkey is only required in TypeScript.

Returns `ValidityProofWithContext`:
- The proof that the new address does not exist in the address tree.
- `addresses` with the public key and metadata of the address tree to pack accounts.

### Update, close, reinit, burn proof

Prove that the compressed account hash exists in the state tree.

#### TypeScript

```typescript
const proof = await rpc.getValidityProofV0(
  [{
    hash: compressedAccount.hash,
    tree: compressedAccount.treeInfo.tree,
    queue: compressedAccount.treeInfo.queue
  }],
  []
);
```

#### Rust

```rust
let rpc_result = rpc
    .get_validity_proof(
        vec![compressed_account.hash],
        vec![],
        None,
    )
    .await?
    .value;
```

> **Note:** You don't specify the address for update, close, reinitialize, and burn instructions. The proof verifies the account hash exists in the state tree. The validity proof structure is identical; the difference is in your program's instruction handler.

### Combined proofs

Prove in a single proof:
- multiple addresses,
- multiple account hashes, or
- a combination of addresses and account hashes.

|              |                   |
| ----------------------- | --------------------------------------------------- |
| Account hash-only        | 1 to 8 hashes                                     |
| Address-only      | 1 to 8 addresses                                  |
| Mixed (hash + address)  | Any combination of 1 to 4 account hashes and 1 or 4 new addresses |

Advantages of combined proofs:
- You only add one 128-byte validity proof to your instruction data.
- This can optimize your transaction's size to stay inside the 1232-byte instruction data limit.
- Compute unit consumption is 100k CU per `ValidityProof` verification by the Light System Program.

#### TypeScript

```typescript
const proof = await rpc.getValidityProofV0(
  [{
    hash: compressedAccount.hash,
    tree: compressedAccount.treeInfo.tree,
    queue: compressedAccount.treeInfo.queue
  }],
  [{
    address: bn(address.toBytes()),
    tree: addressTree.tree,
    queue: addressTree.queue
  }]
);
```

#### Rust

```rust
let rpc_result = rpc
    .get_validity_proof(
        vec![compressed_account.hash],
        vec![AddressWithTree {
          address: *address,
          tree: address_tree_info.tree
        }],
        None,
    )
    .await?
    .value;
```

## PackedAccounts

To interact with a compressed account you need system accounts (Light System Program) and Merkle tree accounts. `PackedAccounts` converts pubkeys to `u8` indices pointing to accounts in the instruction.

```
                                  PackedAccounts
                  ┌--------------------------------------------┐
[custom accounts] [pre accounts][system accounts][tree accounts]
                        ↑              ↑               ↑
                     Signers,      Light System    State trees,
                    fee payer        accounts     address trees,
```

Append `PackedAccounts` after your program-specific accounts (in Anchor: `remaining_accounts`).

### Create

#### TypeScript

```typescript
// 1. Initialize helper
const packedAccounts = new PackedAccounts();

// 2. Add light system accounts
const systemAccountConfig = SystemAccountMetaConfig.new(programId);
packedAccounts.addSystemAccounts(systemAccountConfig);

// 3. Get indices for tree accounts
const addressMerkleTreePubkeyIndex = packedAccounts.insertOrGet(addressTree);
const addressQueuePubkeyIndex = packedAccounts.insertOrGet(addressQueue);

const packedAddressTreeInfo = {
  rootIndex: proofRpcResult.rootIndices[0],
  addressMerkleTreePubkeyIndex,
  addressQueuePubkeyIndex,
};

// 4. Get index for output state tree
const stateTreeInfos = await rpc.getStateTreeInfos();
const outputStateTree = selectStateTreeInfo(stateTreeInfos).tree;
const outputStateTreeIndex = packedAccounts.insertOrGet(outputStateTree);

// 5. Convert to Account Metas
const { remainingAccounts } = packedAccounts.toAccountMetas();
```

#### Rust

```rust
// 1. Initialize helper
let mut remaining_accounts = PackedAccounts::default();

// 2. Add system accounts
let config = SystemAccountMetaConfig::new(program_id);
remaining_accounts.add_system_accounts(config)?;

// 3. Get indices for tree accounts
let packed_accounts = rpc_result.pack_tree_infos(&mut remaining_accounts);

// 4. Get index for output state tree
let output_state_tree_info = rpc.get_random_state_tree_info()?;
let output_state_tree_index
  = output_state_tree_info.pack_output_tree_index(&mut remaining_accounts)?;

// 5. Convert to Account Metas
let (remaining_accounts_metas, _, _) = remaining_accounts.to_account_metas();
```

### Update, close, reinit, burn

#### TypeScript

```typescript
// 1. Initialize helper
const packedAccounts = new PackedAccounts();

// 2. Add system accounts
const systemAccountConfig = SystemAccountMetaConfig.new(programId);
packedAccounts.addSystemAccounts(systemAccountConfig);

// 3. Get indices for tree accounts
const merkleTreePubkeyIndex
  = packedAccounts.insertOrGet(compressedAccount.treeInfo.tree);
const queuePubkeyIndex
  = packedAccounts.insertOrGet(compressedAccount.treeInfo.queue);

const packedInputAccounts = {
  merkleTreePubkeyIndex,
  queuePubkeyIndex,
  leafIndex: proofRpcResult.leafIndices[0],
  rootIndex: proofRpcResult.rootIndices[0],
};

const outputStateTreeIndex
  = packedAccounts.insertOrGet(outputStateTree);

// 4. Convert to Account Metas
const { remainingAccounts } = packedAccounts.toAccountMetas();
```

#### Rust

```rust
// 1. Initialize helper
let mut remaining_accounts = PackedAccounts::default();

// 2. Add system accounts
let config = SystemAccountMetaConfig::new(program_id);
remaining_accounts.add_system_accounts(config)?;

// 3. Get indices for tree accounts
let packed_tree_accounts = rpc_result
    .pack_tree_infos(&mut remaining_accounts)
    .state_trees // includes output_state_tree_index
    .unwrap();

// 4. Convert to Account Metas
let (remaining_accounts_metas, _, _) = remaining_accounts.to_account_metas();
```

### Tree account requirements

| Instruction | Address tree | State tree (includes nullifier queue) | Output queue |
|-------------|:---:|:---:|:---:|
| Create | Yes | - | Yes |
| Update / Close / Reinit | - | Yes | Yes |
| Burn | - | Yes | - |

- **Address tree**: only used to derive and store a new address.
- **State tree**: used to reference the existing compressed account hash. Not used by create. The state tree and nullifier queue are combined into a single account.
- **Output queue**: stores compressed account hashes. A forester node updates the state tree asynchronously.
  - **Create only** - choose any available queue.
  - **Update/Close/Reinit** - use the queue of the existing compressed account.
  - **Mixed instructions (create + update in same tx)** - use the queue from the existing account.
  - **Burn** - do not include an output queue.

## Instruction data

Build instruction data with the validity proof, tree account indices, and account data.

### Create

#### TypeScript

```typescript
const proof = {
  0: proofRpcResult.compressedProof,
};

const instructionData = {
  proof,
  addressTreeInfo: packedAddressTreeInfo,
  outputStateTreeIndex: outputStateTreeIndex,
  message,
};
```

1. Include `proof` to prove the address does not exist in the address tree
2. Specify Merkle trees to store address and account hash
3. Pass initial account data

#### Rust

```rust
let instruction_data = create::instruction::CreateAccount {
    proof: rpc_result.proof,
    address_tree_info: packed_accounts.address_trees[0],
    output_state_tree_index: output_state_tree_index,
    message,
}
.data();
```

### Update

#### TypeScript

```typescript
const instructionData = {
  proof,
  accountMeta: {
    treeInfo: packedStateTreeInfo,
    address: compressedAccount.address,
    outputStateTreeIndex: outputStateTreeIndex
  },
  currentMessage: currentAccount.message,
  newMessage,
};
```

1. Include `proof` to prove the account hash exists in the state tree
2. Specify the existing account's address, its `packedStateTreeInfo` and the output state tree
3. Pass current account data and new data

> **Note:** Use the state tree of the existing compressed account as output state tree.

#### Rust

```rust
let instruction_data = update::instruction::UpdateAccount {
    proof: rpc_result.proof,
    current_account,
    account_meta: CompressedAccountMeta {
        tree_info: packed_tree_accounts.packed_tree_infos[0],
        address: compressed_account.address.unwrap(),
        output_state_tree_index: packed_tree_accounts.output_tree_index,
    },
    new_message,
}
.data();
```

### Close

#### TypeScript

```typescript
const instructionData = {
  proof,
  accountMeta: {
    treeInfo: packedStateTreeInfo,
    address: compressedAccount.address,
    outputStateTreeIndex: outputStateTreeIndex
  },
  currentMessage: currentAccount.message,
};
```

#### Rust

```rust
let instruction_data = close::instruction::CloseAccount {
    proof: rpc_result.proof,
    account_meta: CompressedAccountMeta {
        tree_info: packed_tree_accounts.packed_tree_infos[0],
        address: compressed_account.address.unwrap(),
        output_state_tree_index: packed_tree_accounts.output_tree_index,
    },
    current_message,
}
.data();
```

### Reinitialize

#### TypeScript

```typescript
const instructionData = {
  proof,
  accountMeta: {
    treeInfo: packedStateTreeInfo,
    address: compressedAccount.address,
    outputStateTreeIndex: outputStateTreeIndex
  },
};
```

Reinitialize creates an account with default-initialized values (`Pubkey` as all zeros, numbers as `0`, strings as empty). To set custom values, update the account in the same or a separate transaction.

#### Rust

```rust
let instruction_data = reinit::instruction::ReinitAccount {
    proof: rpc_result.proof,
    account_meta: CompressedAccountMeta {
        tree_info: packed_tree_accounts.packed_tree_infos[0],
        address: compressed_account.address.unwrap(),
        output_state_tree_index: packed_tree_accounts.output_tree_index,
    },
}
.data();
```

### Burn

#### TypeScript

```typescript
const instructionData = {
  proof,
  accountMeta: {
    treeInfo: packedStateTreeInfo,
    address: compressedAccount.address
  },
  currentMessage: currentAccount.message,
};
```

No `outputStateTreeIndex` - burn permanently removes the account.

#### Rust

```rust
let instruction_data = burn::instruction::BurnAccount {
    proof: rpc_result.proof,
    account_meta: CompressedAccountMetaBurn {
        tree_info: packed_tree_accounts.packed_tree_infos[0],
        address: compressed_account.address.unwrap(),
    },
    current_message,
}
.data();
```

> **Warning:** When creating or updating multiple accounts in a single transaction, use one output state tree. Minimize the number of different trees per transaction to keep instruction data light.

## Build and send instruction

Combine your program-specific accounts with `PackedAccounts`.

### TypeScript

```typescript
//             Accounts
// ┌-------------------------------┐
// .accounts()    .remainingAccounts()
// [custom]         [PackedAccounts]

const instruction = await program.methods
  .yourInstruction(instructionData)
  .accounts({
    signer: signer.publicKey,
  })
  .remainingAccounts(remainingAccounts)
  .instruction();
```

### Rust

```rust
//          Accounts
// ┌---------------------------------┐
// [custom accounts]  [PackedAccounts]
let accounts = [vec![AccountMeta::new(payer.pubkey(), true)], remaining_accounts].concat();

let instruction = Instruction {
    program_id: program_id,
    accounts,
    data: instruction_data,
};
```

## Full code examples

Find all [full code examples with Rust and TypeScript tests here](https://github.com/Lightprotocol/program-examples/tree/main/basic-operations/anchor) for:
- **create** - initialize a new compressed account
- **update** - modify data of an existing compressed account
- **close** - close a compressed account (it can be initialized again)
- **reinit** - reinitialize a closed account
- **burn** - permanently delete a compressed account (it cannot be initialized again)
