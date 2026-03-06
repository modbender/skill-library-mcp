# Transfer checked

Transfers tokens with decimal validation. Rust only. Only for Light-to-Light transfers. Use `TransferInterface` for cross-type transfers (SPL, Token-2022, Light).

## Rust

### Action

```rust
use borsh::BorshDeserialize;
use light_client::rpc::Rpc;
use light_token_client::actions::{CreateAta, TransferChecked};
use rust_client::{setup, SetupContext};
use solana_sdk::{signature::Keypair, signer::Signer};

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let SetupContext {
        mut rpc,
        payer,
        mint,
        associated_token_account,
        decimals,
        ..
    } = setup().await;

    // Create recipient associated token account
    let recipient = Keypair::new();
    let (_signature, recipient_associated_token_account) = CreateAta {
        mint,
        owner: recipient.pubkey(),
        idempotent: true,
    }
    .execute(&mut rpc, &payer)
    .await?;

    // TransferChecked validates decimals match the mint's decimals.
    // Only use for Light->Light transfers.
    // Use TransferInterface for all other transfers (Light, SPL or Token-2022).
    let sig = TransferChecked {
        source: associated_token_account,
        mint,
        destination: recipient_associated_token_account,
        amount: 1000,
        decimals,
    }
    .execute(&mut rpc, &payer, &payer)
    .await?;

    let data = rpc
        .get_account(recipient_associated_token_account)
        .await?
        .ok_or("Account not found")?;
    let token = light_token_interface::state::Token::deserialize(&mut &data.data[..])?;
    println!("Balance: {} Tx: {sig}", token.amount);

    Ok(())
}
```

### Instruction

```rust
use borsh::BorshDeserialize;
use light_client::rpc::Rpc;
use light_token::instruction::{
    get_associated_token_address, CreateAssociatedTokenAccount, TransferChecked,
};
use rust_client::{setup, SetupContext};
use solana_sdk::{signature::Keypair, signer::Signer};

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Setup creates mint and associated token account with tokens
    let SetupContext {
        mut rpc,
        payer,
        mint,
        associated_token_account,
        decimals,
        ..
    } = setup().await;

    let transfer_amount = 400_000u64;

    // Create recipient associated token account
    let recipient = Keypair::new();
    let recipient_associated_token_account = get_associated_token_address(&recipient.pubkey(), &mint);

    let create_associated_token_account_instruction = CreateAssociatedTokenAccount::new(payer.pubkey(), recipient.pubkey(), mint)
        .instruction()?;

    rpc.create_and_send_transaction(&[create_associated_token_account_instruction], &payer.pubkey(), &[&payer])
        .await?;

    // TransferChecked validates decimals match the mint's decimals
    // Only use for Light->Light transfers.
    // Use TransferInterface for all other transfers (Light, SPL or Token-2022).
    let transfer_instruction = TransferChecked {
        source: associated_token_account,
        mint,
        destination: recipient_associated_token_account,
        amount: transfer_amount,
        decimals,
        authority: payer.pubkey(),
        max_top_up: None,
        fee_payer: None,
    }
    .instruction()?;

    let sig = rpc
        .create_and_send_transaction(&[transfer_instruction], &payer.pubkey(), &[&payer])
        .await?;

    let data = rpc
        .get_account(recipient_associated_token_account)
        .await?
        .ok_or("Account not found")?;
    let token = light_token_interface::state::Token::deserialize(&mut &data.data[..])?;
    println!("Balance: {} Tx: {sig}", token.amount);

    Ok(())
}
```

## Links

- [Docs](https://zkcompression.com/light-token/cookbook/transfer-checked)
- [Action example](https://github.com/Lightprotocol/examples-light-token/blob/main/rust-client/actions/transfer_checked.rs)
- [Instruction example](https://github.com/Lightprotocol/examples-light-token/blob/main/rust-client/instructions/transfer_checked.rs)
