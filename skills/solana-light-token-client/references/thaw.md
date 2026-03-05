# Thaw

Thaws a frozen Light Token account. Rust only. Requires freeze authority set during mint creation.

If the freeze authority is revoked (set to null) on the mint, tokens can never be frozen again.

## Rust

### Instruction

```rust
use borsh::BorshDeserialize;
use light_client::rpc::Rpc;
use light_token::instruction::Thaw;
use rust_client::{setup_frozen, SetupContext};
use solana_sdk::signer::Signer;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Setup creates mint, associated token account with tokens, and freezes account
    let SetupContext {
        mut rpc,
        payer,
        mint,
        associated_token_account,
        ..
    } = setup_frozen().await;

    let thaw_instruction = Thaw {
        token_account: associated_token_account,
        mint,
        freeze_authority: payer.pubkey(),
    }
    .instruction()?;

    let sig = rpc
        .create_and_send_transaction(&[thaw_instruction], &payer.pubkey(), &[&payer])
        .await?;

    let data = rpc.get_account(associated_token_account).await?.ok_or("Account not found")?;
    let token = light_token_interface::state::Token::deserialize(&mut &data.data[..])?;
    println!("State: {:?} Tx: {sig}", token.state);

    Ok(())
}
```

## Links

- [Docs](https://zkcompression.com/light-token/cookbook/freeze-thaw)
- [Instruction example](https://github.com/Lightprotocol/examples-light-token/blob/main/rust-client/instructions/thaw.rs)
