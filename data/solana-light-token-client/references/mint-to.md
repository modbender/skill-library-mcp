# Mint to

Mints tokens to a Light Token account.

`mintToInterface` auto-detects the token program (SPL, Token 2022, or Light) from the mint address. `fee_payer` and `max_top_up` are optional fields to customize rent top-ups — set to `None` / `undefined` for defaults.

## TypeScript

### Action

```typescript
import "dotenv/config";
import { Keypair } from "@solana/web3.js";
import { createRpc } from "@lightprotocol/stateless.js";
import {
    createMintInterface,
    createAtaInterface,
    mintToInterface,
    getAssociatedTokenAddressInterface,
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

    const recipient = Keypair.generate();
    await createAtaInterface(rpc, payer, mint, recipient.publicKey);

    const destination = getAssociatedTokenAddressInterface(mint, recipient.publicKey);
    const tx = await mintToInterface(rpc, payer, mint, destination, payer, 1_000_000_000);

    console.log("Tx:", tx);
})();
```

### Instruction

```typescript
import "dotenv/config";
import {
    Keypair,
    ComputeBudgetProgram,
    Transaction,
    sendAndConfirmTransaction,
} from "@solana/web3.js";
import { createRpc, bn, DerivationMode } from "@lightprotocol/stateless.js";
import {
    createMintInterface,
    createAtaInterface,
    createMintToInterfaceInstruction,
    getMintInterface,
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

    const recipient = Keypair.generate();
    await createAtaInterface(rpc, payer, mint, recipient.publicKey);
    const destination = getAssociatedTokenAddressInterface(
        mint,
        recipient.publicKey,
    );

    const mintInterface = await getMintInterface(rpc, mint);

    let validityProof;
    if (mintInterface.merkleContext) {
        validityProof = await rpc.getValidityProofV2(
            [
                {
                    hash: bn(mintInterface.merkleContext.hash),
                    leafIndex: mintInterface.merkleContext.leafIndex,
                    treeInfo: mintInterface.merkleContext.treeInfo,
                    proveByIndex: mintInterface.merkleContext.proveByIndex,
                },
            ],
            [],
            DerivationMode.compressible,
        );
    }

    const ix = createMintToInterfaceInstruction(
        mintInterface,
        destination,
        payer.publicKey,
        payer.publicKey,
        1_000_000_000,
        validityProof,
    );

    const tx = new Transaction().add(
        ComputeBudgetProgram.setComputeUnitLimit({ units: 500_000 }),
        ix,
    );
    const signature = await sendAndConfirmTransaction(rpc, tx, [payer]);

    console.log("Tx:", signature);
})();
```

## Rust

### Action

```rust
use borsh::BorshDeserialize;
use light_client::rpc::Rpc;
use light_token_client::actions::{CreateAta, CreateMint, MintTo};
use rust_client::setup_rpc_and_payer;
use solana_sdk::signer::Signer;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let (mut rpc, payer) = setup_rpc_and_payer().await;

    // Create mint (payer is also mint authority)
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

    // Mint tokens (payer is mint authority)
    let sig = MintTo {
        mint,
        destination: associated_token_account,
        amount: 1_000_000,
    }
    .execute(&mut rpc, &payer, &payer)
    .await?;

    let data = rpc.get_account(associated_token_account).await?.ok_or("Account not found")?;
    let token = light_token_interface::state::Token::deserialize(&mut &data.data[..])?;
    println!("Balance: {} Tx: {sig}", token.amount);

    Ok(())
}
```

### Instruction

```rust
use borsh::BorshDeserialize;
use light_client::rpc::Rpc;
use light_token::instruction::MintTo;
use rust_client::{setup_empty_associated_token_account, SetupContext};
use solana_sdk::signer::Signer;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Setup creates mint and empty associated token account
    let SetupContext {
        mut rpc,
        payer,
        mint,
        associated_token_account,
        ..
    } = setup_empty_associated_token_account().await;

    let mint_amount = 1_000_000_000u64;

    let mint_to_instruction = MintTo {
        mint,
        destination: associated_token_account,
        amount: mint_amount,
        authority: payer.pubkey(),
        max_top_up: None,
        fee_payer: None,
    }
    .instruction()?;

    let sig = rpc
        .create_and_send_transaction(&[mint_to_instruction], &payer.pubkey(), &[&payer])
        .await?;

    let data = rpc.get_account(associated_token_account).await?.ok_or("Account not found")?;
    let token = light_token_interface::state::Token::deserialize(&mut &data.data[..])?;
    println!("Balance: {} Tx: {sig}", token.amount);

    Ok(())
}
```

## Links

- [Docs](https://zkcompression.com/light-token/cookbook/mint-to)
- [TS action example](https://github.com/Lightprotocol/examples-light-token/blob/main/typescript-client/actions/mint-to.ts)
- [TS instruction example](https://github.com/Lightprotocol/examples-light-token/blob/main/typescript-client/instructions/mint-to.ts)
- [Rust action example](https://github.com/Lightprotocol/examples-light-token/blob/main/rust-client/actions/mint_to.rs)
- [Rust instruction example](https://github.com/Lightprotocol/examples-light-token/blob/main/rust-client/instructions/mint_to.rs)
