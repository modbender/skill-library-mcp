# Close token account

Closes a Light Token account and recovers rent. Rust only.

## Rust

### Instruction

```rust
use light_client::rpc::Rpc;
use light_token::instruction::{CloseAccount, LIGHT_TOKEN_PROGRAM_ID};
use rust_client::{setup_empty_associated_token_account, SetupContext};
use solana_sdk::signer::Signer;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Setup creates mint and empty associated token account (must be empty to close).
    let SetupContext {
        mut rpc,
        payer,
        associated_token_account,
        ..
    } = setup_empty_associated_token_account().await;
    let close_instruction = CloseAccount::new(LIGHT_TOKEN_PROGRAM_ID, associated_token_account, payer.pubkey(), payer.pubkey())
        .instruction()?;

    let sig = rpc
        .create_and_send_transaction(&[close_instruction], &payer.pubkey(), &[&payer])
        .await?;

    let account = rpc.get_account(associated_token_account).await?;
    println!("Closed: {} Tx: {sig}", account.is_none());

    Ok(())
}
```

## Links

- [Docs](https://zkcompression.com/light-token/cookbook/close-token-account)
- [Instruction example](https://github.com/Lightprotocol/examples-light-token/blob/main/rust-client/instructions/close.rs)
