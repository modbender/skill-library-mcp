# Freeze

Freezes a Light Token account. Rust only. Requires freeze authority set during mint creation.

Once frozen, the account cannot send tokens, receive tokens, or be closed until thawed.

## Rust

### Instruction

```rust
use borsh::BorshDeserialize;
use light_client::rpc::Rpc;
use light_token::instruction::Freeze;
use rust_client::{setup, SetupContext};
use solana_sdk::signer::Signer;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Setup creates mint, associated token account with tokens, and approves delegate
    let SetupContext {
        mut rpc,
        payer,
        mint,
        associated_token_account,
        ..
    } = setup().await;

    // freeze_authority must match what was set during mint creation.
    let freeze_instruction = Freeze {
        token_account: associated_token_account,
        mint,
        freeze_authority: payer.pubkey(),
    }
    .instruction()?;

    let sig = rpc
        .create_and_send_transaction(&[freeze_instruction], &payer.pubkey(), &[&payer])
        .await?;

    let data = rpc.get_account(associated_token_account).await?.ok_or("Account not found")?;
    let token = light_token_interface::state::Token::deserialize(&mut &data.data[..])?;
    println!("State: {:?} Tx: {sig}", token.state);

    Ok(())
}
```

## Links

- [Docs](https://zkcompression.com/light-token/cookbook/freeze-thaw)
- [Instruction example](https://github.com/Lightprotocol/examples-light-token/blob/main/rust-client/instructions/freeze.rs)
