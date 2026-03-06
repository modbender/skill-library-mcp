# Create token account

Creates a non-associated Light Token account. Rust only.

## Rust

### Instruction

```rust
use light_client::rpc::Rpc;
use light_token::instruction::CreateTokenAccount;
use rust_client::{setup_spl_mint_context, SplMintContext};
use solana_sdk::{signature::Keypair, signer::Signer};

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Setup creates mint
    // You can use Light, SPL, or Token-2022 mints to create a light token account.
    let SplMintContext {
        mut rpc,
        payer,
        mint,
    } = setup_spl_mint_context().await;

    let account = Keypair::new();

    let create_token_account_instruction =
        CreateTokenAccount::new(payer.pubkey(), account.pubkey(), mint, payer.pubkey())
            .instruction()?;

    let sig = rpc
        .create_and_send_transaction(&[create_token_account_instruction], &payer.pubkey(), &[&payer, &account])
        .await?;

    let data = rpc.get_account(account.pubkey()).await?;
    println!(
        "Account: {} exists: {} Tx: {sig}",
        account.pubkey(),
        data.is_some()
    );

    Ok(())
}
```

## Links

- [Docs](https://zkcompression.com/light-token/cookbook/create-token-account)
- [Instruction example](https://github.com/Lightprotocol/examples-light-token/blob/main/rust-client/instructions/create_token_account.rs)
