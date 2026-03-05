# CPI Pattern

Explicit CPI calls to Light Token. Standard `#[program]` and `#[derive(Accounts)]` — no macro transforms needed.

## Dependencies

Dependencies for CPI programs:

```toml
anchor-lang = "0.31.1"
light-token = { version = "0.4.0", features = ["anchor"] }
```

No `light-sdk`, `light-sdk-macros`, or `light-sdk-types` required. The `light-token` crate re-exports all CPI types from `light_token::instruction`.

## Shared pattern

Every CPI call follows the same shape:

1. **Import**: `use light_token::instruction::{TypeName};`
2. **Construct** struct literal with account and value fields
3. **Chain** (account creation CPIs only): `.idempotent()`, `.rent_free()`
4. **Invoke**: `.invoke()?` or `.invoke_signed(&[seeds])?` for PDA signers

## Operations reference

| Operation | Docs guide | GitHub example |
|-----------|-----------|----------------|
| `CreateAssociatedAccountCpi` | [create-ata](https://zkcompression.com/light-token/cookbook/create-ata) | [example](https://github.com/Lightprotocol/examples-light-token/tree/main/program-examples/anchor/basic-instructions/create-ata) |
| `CreateTokenAccountCpi` | [create-token-account](https://zkcompression.com/light-token/cookbook/create-token-account) | [example](https://github.com/Lightprotocol/examples-light-token/tree/main/program-examples/anchor/basic-instructions/create-token-account) |
| `CreateMintCpi` | [create-mint](https://zkcompression.com/light-token/cookbook/create-mint) | [example](https://github.com/Lightprotocol/examples-light-token/tree/main/program-examples/anchor/basic-instructions/create-mint) |
| `MintToCpi` | [mint-to](https://zkcompression.com/light-token/cookbook/mint-to) | [example](https://github.com/Lightprotocol/examples-light-token/tree/main/program-examples/anchor/basic-instructions/mint-to) |
| `MintToCheckedCpi` | [mint-to](https://zkcompression.com/light-token/cookbook/mint-to) | [example](https://github.com/Lightprotocol/examples-light-token/tree/main/program-examples/anchor/basic-instructions/mint-to-checked) |
| `BurnCpi` | [burn](https://zkcompression.com/light-token/cookbook/burn) | [example](https://github.com/Lightprotocol/examples-light-token/tree/main/program-examples/anchor/basic-instructions/burn) |
| `TransferCheckedCpi` | [transfer-checked](https://zkcompression.com/light-token/cookbook/transfer-checked) | [example](https://github.com/Lightprotocol/examples-light-token/tree/main/program-examples/anchor/basic-instructions/transfer-checked) |
| `TransferInterfaceCpi` | [transfer-interface](https://zkcompression.com/light-token/cookbook/transfer-interface) | [example](https://github.com/Lightprotocol/examples-light-token/tree/main/program-examples/anchor/basic-instructions/transfer-interface) |
| `ApproveCpi` | [approve-revoke](https://zkcompression.com/light-token/cookbook/approve-revoke) | [example](https://github.com/Lightprotocol/examples-light-token/tree/main/program-examples/anchor/basic-instructions/approve) |
| `RevokeCpi` | [approve-revoke](https://zkcompression.com/light-token/cookbook/approve-revoke) | [example](https://github.com/Lightprotocol/examples-light-token/tree/main/program-examples/anchor/basic-instructions/revoke) |
| `FreezeCpi` | [freeze-thaw](https://zkcompression.com/light-token/cookbook/freeze-thaw) | [example](https://github.com/Lightprotocol/examples-light-token/tree/main/program-examples/anchor/basic-instructions/freeze) |
| `ThawCpi` | [freeze-thaw](https://zkcompression.com/light-token/cookbook/freeze-thaw) | [example](https://github.com/Lightprotocol/examples-light-token/tree/main/program-examples/anchor/basic-instructions/thaw) |
| `CloseAccountCpi` | [close-token-account](https://zkcompression.com/light-token/cookbook/close-token-account) | [example](https://github.com/Lightprotocol/examples-light-token/tree/main/program-examples/anchor/basic-instructions/close-token-account) |

## E2E flow: create-mint → create-ata → mint-to → transfer

```rust
use light_token::instruction::{
    CreateMintCpi, CreateMintParams, SystemAccountInfos,
    CreateAssociatedAccountCpi, MintToCpi, TransferInterfaceCpi,
};
use light_token::{CompressedProof, ExtensionInstructionData, TokenMetadataInstructionData};

// 1. Create mint with metadata
pub fn create_mint(ctx: Context<CreateMintAccounts>, /* params omitted */) -> Result<()> {
    let mint = light_token::instruction::find_mint_address(ctx.accounts.mint_seed.key).0;

    let extensions = Some(vec![ExtensionInstructionData::TokenMetadata(
        TokenMetadataInstructionData {
            update_authority: Some(ctx.accounts.authority.key().to_bytes().into()),
            name: b"My Token".to_vec(),
            symbol: b"MTK".to_vec(),
            uri: b"https://example.com/metadata.json".to_vec(),
            additional_metadata: None,
        },
    )]);

    let params = CreateMintParams {
        decimals: 9,
        address_merkle_tree_root_index,
        mint_authority: *ctx.accounts.authority.key,
        proof,
        compression_address,
        mint,
        bump,
        freeze_authority: None,
        extensions,
        rent_payment: 16,     // ~24 hours
        write_top_up: 766,    // ~3 hours per write
    };

    let system_accounts = SystemAccountInfos {
        light_system_program: ctx.accounts.light_system_program.to_account_info(),
        cpi_authority_pda: ctx.accounts.cpi_authority_pda.to_account_info(),
        registered_program_pda: ctx.accounts.registered_program_pda.to_account_info(),
        account_compression_authority: ctx.accounts.account_compression_authority.to_account_info(),
        account_compression_program: ctx.accounts.account_compression_program.to_account_info(),
        system_program: ctx.accounts.system_program.to_account_info(),
    };

    CreateMintCpi {
        mint_seed: ctx.accounts.mint_seed.to_account_info(),
        authority: ctx.accounts.authority.to_account_info(),
        payer: ctx.accounts.payer.to_account_info(),
        address_tree: ctx.accounts.address_tree.to_account_info(),
        output_queue: ctx.accounts.output_queue.to_account_info(),
        compressible_config: ctx.accounts.compressible_config.to_account_info(),
        mint: ctx.accounts.mint.to_account_info(),
        rent_sponsor: ctx.accounts.rent_sponsor.to_account_info(),
        system_accounts,
        cpi_context: None,
        cpi_context_account: None,
        params,
    }
    .invoke()?;
    Ok(())
}

// 2. Create associated token account — .idempotent() skips if exists, .rent_free() sponsors rent
pub fn create_ata(ctx: Context<CreateAtaAccounts>, bump: u8) -> Result<()> {
    CreateAssociatedAccountCpi {
        payer: ctx.accounts.payer.to_account_info(),
        owner: ctx.accounts.owner.to_account_info(),
        mint: ctx.accounts.mint.to_account_info(),
        ata: ctx.accounts.associated_token_account.to_account_info(),
        bump,
    }
    .idempotent()
    .rent_free(
        ctx.accounts.compressible_config.to_account_info(),
        ctx.accounts.rent_sponsor.to_account_info(),
        ctx.accounts.system_program.to_account_info(),
    )
    .invoke()?;
    Ok(())
}

// 3. Mint to — struct literal pattern
pub fn mint_to(ctx: Context<MintToAccounts>, amount: u64) -> Result<()> {
    MintToCpi {
        mint: ctx.accounts.mint.to_account_info(),
        destination: ctx.accounts.destination.to_account_info(),
        amount,
        authority: ctx.accounts.authority.to_account_info(),
        system_program: ctx.accounts.system_program.to_account_info(),
        max_top_up: None,
        fee_payer: None,
    }
    .invoke()?;
    Ok(())
}

// 4. Transfer — ::new() constructor, resolves source/destination types
pub fn transfer(ctx: Context<TransferAccounts>, amount: u64, decimals: u8) -> Result<()> {
    TransferInterfaceCpi::new(
        amount,
        decimals,
        ctx.accounts.source.to_account_info(),
        ctx.accounts.destination.to_account_info(),
        ctx.accounts.authority.to_account_info(),
        ctx.accounts.payer.to_account_info(),
        ctx.accounts.cpi_authority.to_account_info(),
        ctx.accounts.system_program.to_account_info(),
    )
    .invoke()?;
    Ok(())
}
```