# Burn checked

Burns tokens with decimal validation. Rust only.

Burn permanently destroys tokens and decreases the mint's supply. Only the token account owner (or approved delegate) can burn tokens.

## Rust

### Instruction

```rust
use borsh::BorshDeserialize;
use light_client::rpc::Rpc;
use light_token::instruction::BurnChecked;
use rust_client::{setup, SetupContext};
use solana_sdk::signer::Signer;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Setup creates mint and associated token account with tokens
    let SetupContext {
        mut rpc,
        payer,
        mint,
        ata,
        decimals,
        ..
    } = setup().await;

    let burn_amount = 400_000u64;

    // BurnChecked validates that decimals match the mint
    let burn_ix = BurnChecked {
        source: ata,
        mint,
        amount: burn_amount,
        decimals,
        authority: payer.pubkey(),
        max_top_up: None,
        fee_payer: None,
    }
    .instruction()?;

    let sig = rpc
        .create_and_send_transaction(&[burn_ix], &payer.pubkey(), &[&payer])
        .await?;

    let data = rpc.get_account(ata).await?.ok_or("Account not found")?;
    let token = light_token_interface::state::Token::deserialize(&mut &data.data[..])?;
    println!("Balance: {} Tx: {sig}", token.amount);

    Ok(())
}
```

## Links

- [Docs](https://zkcompression.com/light-token/cookbook/burn)
- [Instruction example](https://github.com/Lightprotocol/examples-light-token/blob/main/rust-client/instructions/burn_checked.rs)
