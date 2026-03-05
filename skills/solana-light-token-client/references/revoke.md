# Revoke

Revokes a delegate's spending authority.

Only the token account owner can revoke delegates.

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
    revoke,
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
    await approve(rpc, payer, mint, 500, payer, delegate.publicKey);

    const delegatedAccounts = await rpc.getCompressedTokenAccountsByDelegate(
        delegate.publicKey,
        { mint },
    );
    const tx = await revoke(rpc, payer, delegatedAccounts.items, payer);

    console.log("Tx:", tx);
})();
```

## Rust

### Action

```rust
use borsh::BorshDeserialize;
use light_client::rpc::Rpc;
use light_token_client::actions::Revoke;
use rust_client::{setup, SetupContext};
use solana_sdk::signer::Signer;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Setup creates mint and associated token account with approved delegate
    let SetupContext {
        mut rpc,
        payer,
        associated_token_account,
        ..
    } = setup().await;

    let sig = Revoke {
        token_account: associated_token_account,
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
use light_token::instruction::Revoke;
use rust_client::{setup, SetupContext};
use solana_sdk::signer::Signer;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Setup creates mint, associated token account with tokens, and approves delegate
    let SetupContext {
        mut rpc,
        payer,
        associated_token_account,
        ..
    } = setup().await;

    let revoke_instruction = Revoke {
        token_account: associated_token_account,
        owner: payer.pubkey(),
    }
    .instruction()?;

    let sig = rpc
        .create_and_send_transaction(&[revoke_instruction], &payer.pubkey(), &[&payer])
        .await?;

    let data = rpc.get_account(associated_token_account).await?.ok_or("Account not found")?;
    let token = light_token_interface::state::Token::deserialize(&mut &data.data[..])?;
    println!("Delegate: {:?} Tx: {sig}", token.delegate);

    Ok(())
}
```

## Links

- [Docs](https://zkcompression.com/light-token/cookbook/approve-revoke)
- [TS example](https://github.com/Lightprotocol/examples-light-token/blob/main/typescript-client/actions/delegate-revoke.ts)
- [Rust action example](https://github.com/Lightprotocol/examples-light-token/blob/main/rust-client/actions/revoke.rs)
- [Rust instruction example](https://github.com/Lightprotocol/examples-light-token/blob/main/rust-client/instructions/revoke.rs)
