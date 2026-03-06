# Create associated token account

Creates a Light Token associated token account for a given mint and owner.

Light associated token account address is derived from `[owner, light_token_program_id, mint]`. Light associated token accounts are on-chain accounts like SPL associated token accounts, but the Light Token Program sponsors the rent-exemption cost. Use `createAtaInterfaceIdempotent` (TS) or `.idempotent()` (Rust) to skip if the associated token account already exists.

## TypeScript

### Action

```typescript
import "dotenv/config";
import { Keypair } from "@solana/web3.js";
import { createRpc } from "@lightprotocol/stateless.js";
import {
    createMintInterface,
    createAtaInterface,
} from "@lightprotocol/compressed-token";
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
    const { mint } = await createMintInterface(rpc, payer, payer, null, 9);

    const owner = Keypair.generate();
    const ata = await createAtaInterface(rpc, payer, mint, owner.publicKey);

    console.log("ATA:", ata.toBase58());
})();
```

### Instruction

```typescript
import "dotenv/config";
import {
    Keypair,
    Transaction,
    sendAndConfirmTransaction,
} from "@solana/web3.js";
import { createRpc, LIGHT_TOKEN_PROGRAM_ID } from "@lightprotocol/stateless.js";
import {
    createMintInterface,
    createAssociatedTokenAccountInterfaceInstruction,
    getAssociatedTokenAddressInterface,
} from "@lightprotocol/compressed-token";
import { homedir } from "os";
import { readFileSync } from "fs";

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
    const { mint } = await createMintInterface(rpc, payer, payer, null, 9);

    const owner = Keypair.generate();
    const associatedToken = getAssociatedTokenAddressInterface(
        mint,
        owner.publicKey,
    );

    const ix = createAssociatedTokenAccountInterfaceInstruction(
        payer.publicKey,
        associatedToken,
        owner.publicKey,
        mint,
        LIGHT_TOKEN_PROGRAM_ID,
    );

    const tx = new Transaction().add(ix);
    const signature = await sendAndConfirmTransaction(rpc, tx, [payer]);

    console.log("ATA:", associatedToken.toBase58());
    console.log("Tx:", signature);
})();
```

## Rust

### Action

```rust
use light_token_client::actions::{CreateAta, CreateMint};
use rust_client::setup_rpc_and_payer;
use solana_sdk::signer::Signer;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let (mut rpc, payer) = setup_rpc_and_payer().await;

    // Create mint
    let (_signature, mint) = CreateMint {
        decimals: 9,
        freeze_authority: None,
        token_metadata: None,
        seed: None,
    }
    .execute(&mut rpc, &payer, &payer)
    .await?;

    // Create associated token account
    let (_signature, associated_token_account) = CreateAta {
        mint,
        owner: payer.pubkey(),
        idempotent: true,
    }
    .execute(&mut rpc, &payer)
    .await?;

    println!("Associated token account: {associated_token_account}");

    Ok(())
}
```

### Instruction

```rust
use light_client::rpc::Rpc;
use light_token::instruction::{get_associated_token_address, CreateAssociatedTokenAccount};
use rust_client::{setup_spl_mint_context, SplMintContext};
use solana_sdk::{signature::Keypair, signer::Signer};

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // You can use Light, SPL, or Token-2022 mints to create a Light associated token account.
    let SplMintContext {
        mut rpc,
        payer,
        mint,
    } = setup_spl_mint_context().await;

    let owner = Keypair::new();

    let create_associated_token_account_instruction =
        CreateAssociatedTokenAccount::new(payer.pubkey(), owner.pubkey(), mint).instruction()?;

    let sig = rpc
        .create_and_send_transaction(&[create_associated_token_account_instruction], &payer.pubkey(), &[&payer])
        .await?;

    let associated_token_account = get_associated_token_address(&owner.pubkey(), &mint);
    let data = rpc.get_account(associated_token_account).await?;
    println!("Associated token account: {associated_token_account} exists: {} Tx: {sig}", data.is_some());

    Ok(())
}
```

### Idempotent

```rust
use light_token::instruction::CreateAssociatedTokenAccount;

let create_ata_ix = CreateAssociatedTokenAccount::new(
    payer.pubkey(),
    payer.pubkey(),
    mint,
)
.idempotent()
.instruction()?;
```

## Links

- [Docs](https://zkcompression.com/light-token/cookbook/create-ata)
- [TS action example](https://github.com/Lightprotocol/examples-light-token/blob/main/typescript-client/actions/create-ata.ts)
- [TS instruction example](https://github.com/Lightprotocol/examples-light-token/blob/main/typescript-client/instructions/create-ata.ts)
- [Rust action example](https://github.com/Lightprotocol/examples-light-token/blob/main/rust-client/actions/create_associated_token_account.rs)
- [Rust instruction example](https://github.com/Lightprotocol/examples-light-token/blob/main/rust-client/instructions/create_associated_token_account.rs)
