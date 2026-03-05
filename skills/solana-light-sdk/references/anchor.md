# Macro Pattern

Declarative macros for rent-free account creation. The SDK generates CPI and proof handling code at compile time.

## Dependencies

From workspace `Cargo.toml` — versions required for macro-based programs:

```toml
blake3 = { version = "=1.8.2", default-features = false }

anchor-lang = "0.31.1"

light-sdk = { version = "0.19.0", features = ["anchor", "idl-build", "v2", "anchor-discriminator", "cpi-context"] }
light-sdk-macros = "0.19.0"
light-sdk-types = { version = "0.19.0", features = ["v2", "cpi-context"] }
light-compressible = { version = "0.4.0", features = ["anchor"] }
light-token = { version = "0.4.0", features = ["anchor"] }
```

`blake3 = "=1.8.2"` is pinned at the workspace level to prevent edition2024 crate compilation errors.

## Program Setup

Every macro program requires three elements:

1. **`LIGHT_CPI_SIGNER` constant** — derived from the program ID at compile time.
2. **`#[light_program]` + `#[allow(deprecated)]` + `#[program]`** — stacked attributes on the module.
3. **Explicit lifetimes** — `Context<'_, '_, '_, 'info, T<'info>>` on every instruction handler.
4. **Single params struct** with `CreateAccountsProof` field — multi-arg functions are not supported.

```rust
pub const LIGHT_CPI_SIGNER: CpiSigner =
    derive_light_cpi_signer!("PDAm7XVHEkBvzBYDh8qF3z8NxnYQzPjGQJKcHVmMZpT");

#[light_program]
#[allow(deprecated)]
#[program]
pub mod counter {
    use super::*;

    pub fn create_counter<'info>(
        ctx: Context<'_, '_, '_, 'info, CreateCounter<'info>>,
        params: CreateCounterParams,
    ) -> Result<()> {
        ctx.accounts.counter.owner = ctx.accounts.owner.key();
        ctx.accounts.counter.count = params.count;
        Ok(())
    }
}
```

The params struct always contains `CreateAccountsProof`:

```rust
#[derive(AnchorSerialize, AnchorDeserialize, Clone)]
pub struct CreateCounterParams {
    // We must create a compressed address at creation to ensure the account does not exist yet.
    pub create_accounts_proof: CreateAccountsProof,
    pub count: u64,
}
```

The `#[instruction(params: ...)]` attribute on the accounts struct wires params into the macro expansion:

```rust
#[derive(Accounts, LightAccounts)]
#[instruction(params: CreateCounterParams)]
pub struct CreateCounter<'info> {
    // ...
}
```

## Import Paths

Two valid import styles exist across the examples:

**Style A — `light_token::anchor` re-exports** (counter, token-transfer examples):

```rust
use light_sdk::interface::CreateAccountsProof;
use light_token::anchor::{derive_light_cpi_signer, light_program, CompressionInfo, CpiSigner, LightAccount, LightAccounts};
```

**Style B — direct `light_sdk_macros` + `light_sdk_types`** (create-mint, create-ata, create-token-account examples):

```rust
use light_compressible::CreateAccountsProof;
use light_sdk::derive_light_cpi_signer;
use light_sdk_macros::{light_program, LightAccounts};
use light_sdk_types::CpiSigner;
```

Both styles compile to the same output. Style B requires `light-sdk-macros` and `light-sdk-types` as separate dependencies.

## State Structs

Custom state requires `LightAccount` derive and `CompressionInfo` field. Only the counter example defines custom state:

```rust
#[derive(Default, Debug, InitSpace, LightAccount)]
#[account]
pub struct Counter {
    pub compression_info: Option<CompressionInfo>,
    pub owner: Pubkey,
    pub count: u64,
}
```

**KEY RULE**: `Account<'info, T>` in the accounts struct only works if `T` derives `LightAccount`. Mint and token accounts do NOT derive `LightAccount`, so they use `UncheckedAccount<'info>` or `AccountInfo<'info>` instead.

## Account Patterns

### PDA init (counter)

Standard Anchor `#[account(init, ...)]` with `#[light_account(init)]`:

```rust
#[account(
    init,
    payer = fee_payer,
    space = 8 + Counter::INIT_SPACE,
    seeds = [COUNTER_SEED, owner.key().as_ref()],
    bump,
)]
#[light_account(init)]
pub counter: Account<'info, Counter>,
```

### Mint init (create-mint)

Uses `UncheckedAccount` with `#[light_account(init, mint::...)]`:

```rust
/// CHECK: Validated by light-token CPI
#[account(mut)]
#[light_account(init,
    mint::signer = mint_signer,
    mint::authority = fee_payer,
    mint::decimals = 9,
    mint::seeds = &[MINT_SIGNER_SEED, self.authority.to_account_info().key.as_ref()],
    mint::bump = params.mint_signer_bump
)]
pub mint: UncheckedAccount<'info>,
```

Requires a separate PDA signer account:

```rust
/// CHECK: Validated by light-token CPI
#[account(
    seeds = [MINT_SIGNER_SEED, authority.key().as_ref()],
    bump,
)]
pub mint_signer: UncheckedAccount<'info>,
```

### Mint with metadata (create-mint)

Extends mint init with metadata fields:

```rust
/// CHECK: Validated by light-token CPI
#[account(mut)]
#[light_account(init,
    mint::signer = mint_signer,
    mint::authority = fee_payer,
    mint::decimals = 9,
    mint::seeds = &[MINT_SIGNER_SEED, self.authority.to_account_info().key.as_ref()],
    mint::bump = params.mint_signer_bump,
    mint::name = params.name.clone(),
    mint::symbol = params.symbol.clone(),
    mint::uri = params.uri.clone(),
    mint::update_authority = authority,
    mint::additional_metadata = params.additional_metadata.clone()
)]
pub mint: UncheckedAccount<'info>,
```

Params struct includes metadata fields and `AdditionalMetadata`:

```rust
use light_token::AdditionalMetadata;

#[derive(AnchorSerialize, AnchorDeserialize, Clone)]
pub struct CreateMintWithMetadataParams {
    pub create_accounts_proof: CreateAccountsProof,
    pub mint_signer_bump: u8,
    pub name: Vec<u8>,
    pub symbol: Vec<u8>,
    pub uri: Vec<u8>,
    pub additional_metadata: Option<Vec<AdditionalMetadata>>,
}
```

### Associated token account init (create-ata)

```rust
/// CHECK: Validated by light-token CPI
#[account(mut)]
#[light_account(init, associated_token::authority = ata_owner, associated_token::mint = ata_mint, associated_token::bump = params.ata_bump)]
pub ata: UncheckedAccount<'info>,
```

### Token account init (create-token-account)

```rust
/// CHECK: Validated by light-token CPI
#[account(
    mut,
    seeds = [VAULT_SEED, mint.key().as_ref()],
    bump,
)]
#[light_account(
    init,
    token::authority = [VAULT_SEED, self.mint.key()],
    token::mint = mint,
    token::owner = vault_authority,
    token::bump = params.vault_bump
)]
pub vault: UncheckedAccount<'info>,
```

### Transfer with destination associated token account init (token-transfer)

Macro init for the destination combined with `TransferInterfaceCpi` in the handler body:

```rust
/// CHECK: Validated by light-token CPI
#[account(mut)]
#[light_account(init,
    associated_token::authority = recipient,
    associated_token::mint = mint,
    associated_token::bump = params.dest_ata_bump
)]
pub destination: UncheckedAccount<'info>,
```

## Infrastructure Accounts

Different account types require different infrastructure accounts:

**PDA (counter):**
- `compression_config: AccountInfo<'info>` — validated by Light System CPI

**Token accounts (mint, associated token account, token account):**
- `light_token_compressible_config: AccountInfo<'info>`
- `rent_sponsor: AccountInfo<'info>` (mut)
- `light_token_program: AccountInfo<'info>`
- `light_token_cpi_authority: AccountInfo<'info>` (for mint and token account; not needed for associated token account)

The create-ata and create-token-account examples show explicit address constraints using known constants:

```rust
use light_token::instruction::{COMPRESSIBLE_CONFIG_V1, RENT_SPONSOR as LIGHT_TOKEN_RENT_SPONSOR};
use light_sdk_types::LIGHT_TOKEN_PROGRAM_ID;

#[account(address = COMPRESSIBLE_CONFIG_V1)]
pub light_token_compressible_config: AccountInfo<'info>,

#[account(mut, address = LIGHT_TOKEN_RENT_SPONSOR)]
pub light_token_rent_sponsor: AccountInfo<'info>,

#[account(address = LIGHT_TOKEN_PROGRAM_ID.into())]
pub light_token_program: AccountInfo<'info>,
```

## Hybrid Pattern

The token-transfer example combines macro account init with explicit CPI in the handler body. The macro creates the destination associated token account, while `TransferInterfaceCpi` executes the transfer:

```rust
use light_token::instruction::TransferInterfaceCpi;

#[light_program]
#[allow(deprecated)]
#[program]
pub mod token_transfer {
    use super::*;

    pub fn transfer<'info>(
        ctx: Context<'_, '_, '_, 'info, Transfer<'info>>,
        params: TransferParams,
    ) -> Result<()> {
        TransferInterfaceCpi::new(
            params.amount,
            params.decimals,
            ctx.accounts.source.to_account_info(),
            ctx.accounts.destination.to_account_info(),
            ctx.accounts.authority.to_account_info(),
            ctx.accounts.payer.to_account_info(),
            ctx.accounts.light_token_cpi_authority.to_account_info(),
            ctx.accounts.system_program.to_account_info(),
        )
        .invoke()
        .map_err(|e| anchor_lang::prelude::ProgramError::from(e))?;
        Ok(())
    }
}
```

Note the `.map_err(|e| anchor_lang::prelude::ProgramError::from(e))` — required because `TransferInterfaceCpi::invoke()` returns a different error type than Anchor's `Result<()>`.

## Common Errors

- **edition2024 crate errors** — pin `blake3 = "=1.8.2"` in workspace `[workspace.dependencies]`.
- **`Account<'info, Mint>` with `LightAccounts`** — use `UncheckedAccount<'info>` or `AccountInfo<'info>` instead. `Mint` does not derive `LightAccount`, so `Account<'info, Mint>` will fail.
- **Wrong field names** — use `compression_config` (not `light_interface_config`), `light_token_compressible_config` (not `light_token_interface_config`).
- **Missing `#[allow(deprecated)]`** — required between `#[light_program]` and `#[program]`. Some examples use file-level `#![allow(unexpected_cfgs, deprecated)]` instead.
- **Missing `LIGHT_CPI_SIGNER` constant** — every macro program must define this with `derive_light_cpi_signer!` using the program's ID string.
- **Multi-arg functions** — must use a single params struct containing `CreateAccountsProof`. The macro expansion expects exactly one params argument after `ctx`.