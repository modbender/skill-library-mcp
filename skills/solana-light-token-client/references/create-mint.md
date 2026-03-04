# Create mint

Creates a Light Token mint with sponsored rent-exemption.

**Dispatch behavior**: `createMintInterface` dispatches by `programId`: `TOKEN_PROGRAM_ID` creates an SPL mint + interface PDA, `TOKEN_2022_PROGRAM_ID` creates a T22 mint + interface PDA, default (no `programId`) creates a Light Token mint.

**Mint authority**: `mintAuthority` must be a `Signer` for Light mints but can be a `PublicKey` for SPL/T22 mints.

**Metadata**: `additional_metadata` fields must be set at creation. Standard fields (`name`, `symbol`, `uri`) can be updated later. For `additional_metadata`, only existing keys can be modified or removed — new keys cannot be added after creation.

## TypeScript

### Action

```typescript
import "dotenv/config";
import { Keypair } from "@solana/web3.js";
import { createRpc } from "@lightprotocol/stateless.js";
import { createMintInterface, createTokenMetadata } from "@lightprotocol/compressed-token";
import { homedir } from "os";
import { readFileSync } from "fs";

// devnet:
const RPC_URL = `https://devnet.helius-rpc.com?api-key=${process.env.API_KEY!}`;
const rpc = createRpc(RPC_URL);
// localnet:
// const rpc = createRpc();

const payer = Keypair.fromSecretKey(
    new Uint8Array(
        JSON.parse(readFileSync(`${homedir()}/.config/solana/id.json`, "utf8"))
    )
);

(async function () {
    const { mint, transactionSignature } = await createMintInterface(
        rpc,
        payer,
        payer,
        null,
        9,
        undefined,
        undefined,
        undefined,
        createTokenMetadata("Example Token", "EXT", "https://example.com/metadata.json")
    );

    console.log("Mint:", mint.toBase58());
    console.log("Tx:", transactionSignature);
})();
```

### Instruction

```typescript
import "dotenv/config";
import {
    Keypair,
    ComputeBudgetProgram,
    PublicKey,
    Transaction,
    sendAndConfirmTransaction,
} from "@solana/web3.js";
import {
    createRpc,
    getBatchAddressTreeInfo,
    selectStateTreeInfo,
    CTOKEN_PROGRAM_ID,
} from "@lightprotocol/stateless.js";
import {
    createMintInstruction,
    createTokenMetadata,
} from "@lightprotocol/compressed-token";
import { homedir } from "os";
import { readFileSync } from "fs";

const COMPRESSED_MINT_SEED = Buffer.from("compressed_mint");

function findMintAddress(mintSigner: PublicKey): [PublicKey, number] {
    return PublicKey.findProgramAddressSync(
        [COMPRESSED_MINT_SEED, mintSigner.toBuffer()],
        CTOKEN_PROGRAM_ID,
    );
}

// devnet:
// const RPC_URL = `https://devnet.helius-rpc.com?api-key=${process.env.API_KEY!}`;
// const rpc = createRpc(RPC_URL);
// localnet:
const rpc = createRpc();

const payer = Keypair.fromSecretKey(
    new Uint8Array(
        JSON.parse(readFileSync(`${homedir()}/.config/solana/id.json`, "utf8")),
    ),
);

(async function () {
    const mintSigner = Keypair.generate();
    const addressTreeInfo = getBatchAddressTreeInfo();
    const stateTreeInfo = selectStateTreeInfo(await rpc.getStateTreeInfos());
    const [mintPda] = findMintAddress(mintSigner.publicKey);

    const validityProof = await rpc.getValidityProofV2(
        [],
        [{ address: mintPda.toBytes(), treeInfo: addressTreeInfo }],
    );

    const ix = createMintInstruction(
        mintSigner.publicKey,
        9,
        payer.publicKey,
        null,
        payer.publicKey,
        validityProof,
        addressTreeInfo,
        stateTreeInfo,
        createTokenMetadata(
            "Example Token",
            "EXT",
            "https://example.com/metadata.json",
        ),
    );

    const tx = new Transaction().add(
        ComputeBudgetProgram.setComputeUnitLimit({ units: 1_000_000 }),
        ix,
    );
    const signature = await sendAndConfirmTransaction(rpc, tx, [
        payer,
        mintSigner,
    ]);

    console.log("Mint:", mintPda.toBase58());
    console.log("Tx:", signature);
})();
```

## Rust

### Action

```rust
use light_client::rpc::Rpc;
use light_token_client::actions::{CreateMint, TokenMetadata};
use rust_client::setup_rpc_and_payer;
use solana_sdk::signer::Signer;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let (mut rpc, payer) = setup_rpc_and_payer().await;

    let (signature, mint) = CreateMint {
        decimals: 9,
        freeze_authority: None,
        token_metadata: Some(TokenMetadata {
            name: "Example Token".to_string(),
            symbol: "EXT".to_string(),
            uri: "https://example.com/metadata.json".to_string(),
            update_authority: Some(payer.pubkey()),
            additional_metadata: Some(vec![("type".to_string(), "example".to_string())]),
        }),
        seed: None,
    }
    .execute(&mut rpc, &payer, &payer)
    .await?;

    let data = rpc.get_account(mint).await?;
    println!("Mint: {mint} exists: {} Tx: {signature}", data.is_some());

    Ok(())
}
```

### Instruction

```rust
use light_client::{
    indexer::{AddressWithTree, Indexer},
    rpc::Rpc,
};
use light_program_test::{LightProgramTest, ProgramTestConfig};
use light_token::instruction::{
    derive_mint_compressed_address, find_mint_address, CreateMint, CreateMintParams,
    DEFAULT_RENT_PAYMENT, DEFAULT_WRITE_TOP_UP,
};
use light_token_interface::{
    instructions::extensions::{
        token_metadata::TokenMetadataInstructionData, ExtensionInstructionData,
    },
    state::AdditionalMetadata,
};
use solana_sdk::{signature::Keypair, signer::Signer};

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let mut rpc = LightProgramTest::new(ProgramTestConfig::new_v2(false, None)).await?;

    let payer = rpc.get_payer().insecure_clone();
    let mint_seed = Keypair::new();
    let decimals = 9u8;

    // Get address tree to store compressed address for when mint turns inactive
    // We must create a compressed address at creation to ensure the mint does not exist yet
    let address_tree = rpc.get_address_tree_v2();
    // Get state tree to store mint when inactive
    let output_queue = rpc.get_random_state_tree_info().unwrap().queue;

    // Derive mint addresses
    let compression_address =
        derive_mint_compressed_address(&mint_seed.pubkey(), &address_tree.tree);
    let mint = find_mint_address(&mint_seed.pubkey()).0; // on-chain Mint PDA

    // Fetch validity proof to proof address does not exist yet
    let rpc_result = rpc
        .get_validity_proof(
            vec![],
            vec![AddressWithTree {
                address: compression_address,
                tree: address_tree.tree,
            }],
            None,
        )
        .await
        .unwrap()
        .value;

    // Build CreateMintParams with token metadata extension
    let params = CreateMintParams {
        decimals,
        address_merkle_tree_root_index: rpc_result.addresses[0].root_index, // stores mint compressed address
        mint_authority: payer.pubkey(),
        proof: rpc_result.proof.0.unwrap(),
        compression_address, // address for compression when mint turns inactive
        mint,
        bump: find_mint_address(&mint_seed.pubkey()).1,
        freeze_authority: None,
        extensions: Some(vec![ExtensionInstructionData::TokenMetadata(
            TokenMetadataInstructionData {
                update_authority: Some(payer.pubkey().to_bytes().into()),
                name: b"Example Token".to_vec(),
                symbol: b"EXT".to_vec(),
                uri: b"https://example.com/metadata.json".to_vec(),
                additional_metadata: Some(vec![AdditionalMetadata {
                    key: b"type".to_vec(),
                    value: b"example".to_vec(),
                }]),
            },
        )]),
        rent_payment: DEFAULT_RENT_PAYMENT, // 24h of rent
        write_top_up: DEFAULT_WRITE_TOP_UP, // 3h of rent
    };

    // Build and send instruction (mint_seed must sign)
    let create_mint_instruction = CreateMint::new(
        params,
        mint_seed.pubkey(),
        payer.pubkey(),
        address_tree.tree,
        output_queue,
    )
    .instruction()?;

    let sig = rpc
        .create_and_send_transaction(&[create_mint_instruction], &payer.pubkey(), &[&payer, &mint_seed])
        .await?;

    let data = rpc.get_account(mint).await?;
    println!("Mint: {} exists: {} Tx: {sig}", mint, data.is_some());

    Ok(())
}
```

## Create SPL/T22 mint with interface PDA

Pass `TOKEN_PROGRAM_ID` to create an SPL mint, or `TOKEN_2022_PROGRAM_ID` for a T22 mint. Both variants register an interface PDA in the same transaction.

### TypeScript

```typescript
import "dotenv/config";
import { Keypair } from "@solana/web3.js";
import { createRpc } from "@lightprotocol/stateless.js";
import { createMintInterface } from "@lightprotocol/compressed-token";
import { TOKEN_PROGRAM_ID } from "@solana/spl-token";
import { homedir } from "os";
import { readFileSync } from "fs";

// devnet:
const RPC_URL = `https://devnet.helius-rpc.com?api-key=${process.env.API_KEY!}`;
const rpc = createRpc(RPC_URL);
// localnet:
// const rpc = createRpc();

const payer = Keypair.fromSecretKey(
    new Uint8Array(
        JSON.parse(readFileSync(`${homedir()}/.config/solana/id.json`, "utf8"))
    )
);

(async function () {
    // Creates SPL mint + SPL Interface PDA in one transaction
    const mintKeypair = Keypair.generate();
    const { mint, transactionSignature } = await createMintInterface(
        rpc,
        payer,
        payer,
        null,
        9,
        mintKeypair,
        undefined,
        TOKEN_PROGRAM_ID
    );

    console.log("Mint:", mint.toBase58());
    console.log("Tx:", transactionSignature);
})();
```

## Links

- [Docs](https://zkcompression.com/light-token/cookbook/create-mint)
- [TS action example](https://github.com/Lightprotocol/examples-light-token/blob/main/typescript-client/actions/create-mint.ts)
- [Rust action example](https://github.com/Lightprotocol/examples-light-token/blob/main/rust-client/actions/create_mint.rs)
- [Rust instruction example](https://github.com/Lightprotocol/examples-light-token/blob/main/rust-client/instructions/create_mint.rs)
