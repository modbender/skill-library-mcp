# Wrap

Moves tokens from an SPL or Token-2022 account into a Light Token associated token account (hot balance).

## TypeScript

### Action

```typescript
import "dotenv/config";
import { Keypair } from "@solana/web3.js";
import { createRpc, bn } from "@lightprotocol/stateless.js";
import {
    createMint,
    mintTo,
    decompress,
    wrap,
    getAssociatedTokenAddressInterface,
    createAtaInterfaceIdempotent,
} from "@lightprotocol/compressed-token";
import { createAssociatedTokenAccount } from "@solana/spl-token";
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
    // Setup: Get SPL tokens (needed to wrap)
    const { mint } = await createMint(rpc, payer, payer.publicKey, 9);
    const splAta = await createAssociatedTokenAccount(
        rpc,
        payer,
        mint,
        payer.publicKey
    );
    await mintTo(rpc, payer, mint, payer.publicKey, payer, bn(1000));
    await decompress(rpc, payer, mint, bn(1000), payer, splAta);

    // Wrap SPL tokens to rent-free associated token account
    const lightTokenAta = getAssociatedTokenAddressInterface(mint, payer.publicKey);
    await createAtaInterfaceIdempotent(rpc, payer, mint, payer.publicKey);

    const tx = await wrap(rpc, payer, splAta, lightTokenAta, payer, mint, bn(500));

    console.log("Tx:", tx);
})();
```

### Instruction

```typescript
import "dotenv/config";
import { Keypair, ComputeBudgetProgram, Transaction, sendAndConfirmTransaction } from "@solana/web3.js";
import { createRpc, bn } from "@lightprotocol/stateless.js";
import {
    createMint,
    mintTo,
    decompress,
    createWrapInstruction,
    getAssociatedTokenAddressInterface,
    createAtaInterfaceIdempotent,
    getSplInterfaceInfos,
} from "@lightprotocol/compressed-token";
import { createAssociatedTokenAccount } from "@solana/spl-token";
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
    // Setup: Get SPL tokens (needed to wrap)
    const { mint } = await createMint(rpc, payer, payer.publicKey, 9);
    const splAta = await createAssociatedTokenAccount(
        rpc,
        payer,
        mint,
        payer.publicKey
    );
    await mintTo(rpc, payer, mint, payer.publicKey, payer, bn(1000));
    await decompress(rpc, payer, mint, bn(1000), payer, splAta);

    // Create wrap instruction
    const lightTokenAta = getAssociatedTokenAddressInterface(mint, payer.publicKey);
    await createAtaInterfaceIdempotent(rpc, payer, mint, payer.publicKey);

    const splInterfaceInfos = await getSplInterfaceInfos(rpc, mint);
    const splInterfaceInfo = splInterfaceInfos.find(
        (info) => info.isInitialized
    );

    if (!splInterfaceInfo) throw new Error("No SPL interface found");

    const ix = createWrapInstruction(
        splAta,
        lightTokenAta,
        payer.publicKey,
        mint,
        bn(500),
        splInterfaceInfo,
        9, // decimals - must match the mint decimals
        payer.publicKey
    );

    const tx = new Transaction().add(
        ComputeBudgetProgram.setComputeUnitLimit({ units: 200_000 }),
        ix
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
use light_token_client::actions::Wrap;
use rust_client::{setup_for_wrap, WrapContext};

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Setup creates SPL associated token account with tokens and empty Light associated token account
    let WrapContext {
        mut rpc,
        payer,
        mint,
        source_associated_token_account,
        light_associated_token_account,
        decimals,
    } = setup_for_wrap().await;

    // Wrap tokens from SPL associated token account to Light Token associated token account
    let sig = Wrap {
        source_spl_ata: source_associated_token_account,
        destination: light_associated_token_account,
        mint,
        amount: 500_000,
        decimals,
    }
    .execute(&mut rpc, &payer, &payer)
    .await?;

    let data = rpc
        .get_account(light_associated_token_account)
        .await?
        .ok_or("Account not found")?;
    let token = light_token_interface::state::Token::deserialize(&mut &data.data[..])?;
    println!("Balance: {} Tx: {sig}", token.amount);

    Ok(())
}
```

## Links

- [Docs](https://zkcompression.com/light-token/cookbook/wrap-unwrap)
- [TS action example](https://github.com/Lightprotocol/examples-light-token/blob/main/typescript-client/actions/wrap.ts)
- [TS instruction example](https://github.com/Lightprotocol/examples-light-token/blob/main/typescript-client/instructions/wrap.ts)
- [Rust action example](https://github.com/Lightprotocol/examples-light-token/blob/main/rust-client/actions/wrap.rs)
