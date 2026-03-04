# Approve

Delegates token spending authority to another account.

Each token account can have only one delegate at a time; a new approval overwrites the previous one. Only the token account owner can approve delegates.

## TypeScript

### Action

```typescript
import "dotenv/config";
import { Keypair } from "@solana/web3.js";
import { createRpc } from "@lightprotocol/stateless.js";
import {
    createMintInterface,
    mintToCompressed,
    approve,
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
    await mintToCompressed(rpc, payer, mint, payer, [{ recipient: payer.publicKey, amount: 1000n }]);

    const delegate = Keypair.generate();
    const tx = await approve(
        rpc,
        payer,
        mint,
        500,
        payer,
        delegate.publicKey,
    );

    console.log("Tx:", tx);
})();
```

## Rust

### Action

```rust
use borsh::BorshDeserialize;
use light_client::rpc::Rpc;
use light_token_client::actions::Approve;
use rust_client::{setup, SetupContext};
use solana_sdk::{signature::Keypair, signer::Signer};

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Setup creates mint and associated token account with tokens
    let SetupContext {
        mut rpc,
        payer,
        associated_token_account,
        ..
    } = setup().await;

    let delegate = Keypair::new();

    let sig = Approve {
        token_account: associated_token_account,
        delegate: delegate.pubkey(),
        amount: 500_000,
        owner: Some(payer.pubkey()),
    }
    .execute(&mut rpc, &payer)
    .await?;

    let data = rpc.get_account(associated_token_account).await?.ok_or("Account not found")?;
    let token = light_token_interface::state::Token::deserialize(&mut &data.data[..])?;
    println!("Delegate: {:?} Tx: {sig}", token.delegate);

    Ok(())
}
```

### Instruction

```rust
use borsh::BorshDeserialize;
use light_client::rpc::Rpc;
use light_token::instruction::Approve;
use rust_client::{setup, SetupContext};
use solana_sdk::{signature::Keypair, signer::Signer};

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Setup creates mint and associated token account with tokens
    let SetupContext {
        mut rpc,
        payer,
        associated_token_account,
        ..
    } = setup().await;

    let delegate = Keypair::new();
    let delegate_amount = 500_000u64;

    let approve_instruction = Approve {
        token_account: associated_token_account,
        delegate: delegate.pubkey(),
        owner: payer.pubkey(),
        amount: delegate_amount,
    }
    .instruction()?;

    let sig = rpc
        .create_and_send_transaction(&[approve_instruction], &payer.pubkey(), &[&payer])
        .await?;

    let data = rpc.get_account(associated_token_account).await?.ok_or("Account not found")?;
    let token = light_token_interface::state::Token::deserialize(&mut &data.data[..])?;
    println!("Delegate: {:?} Tx: {sig}", token.delegate);

    Ok(())
}
```

## Links

- [Docs](https://zkcompression.com/light-token/cookbook/approve-revoke)
- [TS example](https://github.com/Lightprotocol/examples-light-token/blob/main/typescript-client/actions/delegate-approve.ts)
- [Rust action example](https://github.com/Lightprotocol/examples-light-token/blob/main/rust-client/actions/approve.rs)
- [Rust instruction example](https://github.com/Lightprotocol/examples-light-token/blob/main/rust-client/instructions/approve.rs)
