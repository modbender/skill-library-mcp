# Pinocchio Pattern

Rent-free DeFi accounts using Pinocchio. The Light-SDK sponsors rent-exemption for your PDAs, token accounts, and mints.

## Dependencies

```toml
[dependencies]
light-account-pinocchio = { version = "0.20", features = ["token", "std"] }
light-token-pinocchio = "0.20"

pinocchio = "0.9"
pinocchio-pubkey = { version = "0.3", features = ["const"] }
pinocchio-system = "0.3"
borsh = { version = "0.10.4", default-features = false }
bytemuck = { version = "1.21", features = ["derive"] }
```

## State Struct

```rust
use borsh::{BorshDeserialize, BorshSerialize};
use light_account_pinocchio::{CompressionInfo, LightPinocchioAccount};

#[derive(
    Default, Debug, Copy, Clone, PartialEq,
    BorshSerialize, BorshDeserialize,
    LightPinocchioAccount,
    bytemuck::Pod, bytemuck::Zeroable,
)]
#[repr(C)]
pub struct PoolState {
    pub compression_info: CompressionInfo,

    // Your regular state...
    pub fee_bps: u16,
}
```

NOTE: `CompressionInfo` is NOT `Option<CompressionInfo>`. Uses `#[repr(C)]`, `bytemuck::Pod + Zeroable`.

## Program Enum

```rust
use light_account_pinocchio::{
    derive_light_cpi_signer, pubkey_array, CpiSigner, LightProgramPinocchio,
};
use pinocchio::pubkey::Pubkey;

pub const ID: Pubkey = pubkey_array!("YourProgram11111111111111111111111111111111");
pub const LIGHT_CPI_SIGNER: CpiSigner =
    derive_light_cpi_signer!("YourProgram11111111111111111111111111111111");

#[derive(LightProgramPinocchio)]
pub enum ProgramAccounts {
    #[light_account(pda::seeds = [POOL_SEED, ctx.mint_a, ctx.mint_b], pda::zero_copy)]
    PoolState(PoolState),

    #[light_account(token::seeds = [POOL_VAULT_SEED, ctx.pool, ctx.mint], token::owner_seeds = [POOL_AUTHORITY_SEED])]
    Vault,

    #[light_account(associated_token)]
    UserToken,
}
```

This auto-generates 4 instructions, discriminators, and the `LightAccountVariant` enum used by the client SDK.

## Entrypoint

```rust
pinocchio::entrypoint!(process_instruction);

pub fn process_instruction(
    _program_id: &Pubkey,
    accounts: &[AccountInfo],
    instruction_data: &[u8],
) -> Result<(), ProgramError> {
    if instruction_data.len() < 8 {
        return Err(ProgramError::InvalidInstructionData);
    }

    let (disc, data) = instruction_data.split_at(8);
    let disc: [u8; 8] = disc.try_into().unwrap();

    match disc {
        // your custom program logic...
        discriminators::INITIALIZE => process_initialize(accounts, data),
        discriminators::SWAP => process_swap(accounts, data),

        // add this:
        ProgramAccounts::INITIALIZE_COMPRESSION_CONFIG => {
            ProgramAccounts::process_initialize_config(accounts, data) // generated
        }
        ProgramAccounts::UPDATE_COMPRESSION_CONFIG => {
            ProgramAccounts::process_update_config(accounts, data)
        }
        ProgramAccounts::COMPRESS_ACCOUNTS_IDEMPOTENT => {
            ProgramAccounts::process_compress(accounts, data)
        }
        ProgramAccounts::DECOMPRESS_ACCOUNTS_IDEMPOTENT => {
            ProgramAccounts::process_decompress(accounts, data)
        }
        _ => Err(ProgramError::InvalidInstructionData),
    }
}
```

## Init Handler

### Create Token Account

```rust
use light_account_pinocchio::CreateTokenAccountCpi;

CreateTokenAccountCpi {
    payer: ctx.payer,
    account: vault,
    mint,
    owner: *pool_authority.key(),
}
.rent_free(
    ctx.light_token_config,
    ctx.light_token_rent_sponsor,
    ctx.system_program,
    &crate::ID,
)
.invoke_signed(&[
    POOL_VAULT_SEED,
    pool_key.as_ref(),
    mint_key.as_ref(),
    &[bump],
])?;
```

### Create Mints (Batch)

```rust
use light_account_pinocchio::{CreateMints, CreateMintsStaticAccounts, SingleMintParams};

let sdk_mints: [SingleMintParams<'_>; 2] = [
    SingleMintParams {
        decimals: 9,
        mint_authority: authority_key,
        mint_bump: None,
        freeze_authority: None,
        mint_seed_pubkey: mint_signer_a_key,
        authority_seeds: None,
        mint_signer_seeds: Some(mint_signer_a_seeds),
        token_metadata: None,
    },
    // ...
];

CreateMints {
    mints: &sdk_mints,
    proof_data: &params.create_accounts_proof,
    mint_seed_accounts: ctx.mint_signers,
    mint_accounts: ctx.mints,
    static_accounts: CreateMintsStaticAccounts {
        fee_payer: ctx.payer,
        compressible_config: ctx.light_token_config,
        rent_sponsor: ctx.light_token_rent_sponsor,
        cpi_authority: ctx.cpi_authority,
    },
    cpi_context_offset: 1,
}
.invoke(&cpi_accounts)?;
```

### Full Initialize Processor

```rust
use light_account_pinocchio::{
    prepare_compressed_account_on_init, CompressedCpiContext, CpiAccounts, CpiAccountsConfig,
    CpiContextWriteAccounts, CreateMints, CreateMintsStaticAccounts, CreateTokenAccountCpi,
    InstructionDataInvokeCpiWithAccountInfo, InvokeLightSystemProgram, LightAccount, LightConfig,
    SingleMintParams,
};
use pinocchio::sysvars::{clock::Clock, Sysvar};

pub fn process(
    ctx: &InitializeAccounts<'_>,
    params: &InitializeParams,
    remaining_accounts: &[AccountInfo],
) -> Result<(), LightSdkTypesError> {
    // 1. Build CPI accounts
    let config = CpiAccountsConfig::new_with_cpi_context(crate::LIGHT_CPI_SIGNER);
    let cpi_accounts = CpiAccounts::new_with_config(
        ctx.payer,
        &remaining_accounts[params.create_accounts_proof.system_accounts_offset as usize..],
        config,
    );

    // 2. Get address tree info + config
    let address_tree_info = &params.create_accounts_proof.address_tree_info;
    let address_tree_pubkey = address_tree_info.get_tree_pubkey(&cpi_accounts)?;
    let light_config = LightConfig::load_checked(ctx.compressible_config, &crate::ID)?;
    let current_slot = Clock::get()?.slot;

    // 3. Create pool PDA (write to CPI context)
    {
        let cpi_context = CompressedCpiContext::first();
        let mut new_address_params = Vec::with_capacity(1);
        let mut account_infos = Vec::with_capacity(1);
        let pool_key = *ctx.pool.key();

        prepare_compressed_account_on_init(
            &pool_key, &address_tree_pubkey, address_tree_info,
            params.create_accounts_proof.output_state_tree_index,
            0, &crate::ID,
            &mut new_address_params, &mut account_infos,
        )?;

        // Initialize pool state (zero-copy)
        {
            let mut data = ctx.pool.try_borrow_mut_data()?;
            let pool_state: &mut PoolState = bytemuck::from_bytes_mut(
                &mut data[8..8 + core::mem::size_of::<PoolState>()]
            );
            pool_state.set_decompressed(&light_config, current_slot);
            pool_state.token_a_mint = *ctx.mint_a().key();
            pool_state.token_b_mint = *ctx.mint_b().key();
            // ... remaining fields
        }

        // Write to CPI context
        let instruction_data = InstructionDataInvokeCpiWithAccountInfo {
            mode: 1,
            bump: crate::LIGHT_CPI_SIGNER.bump,
            invoking_program_id: crate::LIGHT_CPI_SIGNER.program_id.into(),
            proof: params.create_accounts_proof.proof.0,
            new_address_params,
            account_infos,
            // ...
        };
        instruction_data.invoke_write_to_cpi_context_first(
            CpiContextWriteAccounts {
                fee_payer: cpi_accounts.fee_payer(),
                authority: cpi_accounts.authority()?,
                cpi_context: cpi_accounts.cpi_context()?,
                cpi_signer: crate::LIGHT_CPI_SIGNER,
            }
        )?;
    }

    // 4. Create mints
    CreateMints { /* ... */ }.invoke(&cpi_accounts)?;

    // 5. Create vaults (rent-free)
    CreateTokenAccountCpi { /* ... */ }.rent_free(/* ... */).invoke_signed(/* ... */)?;

    Ok(())
}
```

## Client SDK

Implement `LightProgramInterface` so routers can detect and load cold accounts. See the full Pinocchio implementation in [client-sdk.md](./client-sdk.md#pinocchio-example).

## Testing

For the full Pinocchio test lifecycle (init with proof, swap, compress, load + swap), see [testing.md](./testing.md#pinocchio-test).

## How it works

The SDK sponsors rent-exemption for all accounts. After extended inactivity, Forester nodes compress accounts to cold state — your program code does not change. See [hot/cold model](../SKILL.md#hot-vs-cold-model) for overhead numbers. For client-side cold-account loading details, see [router.md](./router.md).

## FAQ

See [faq.md](./faq.md) for common questions (re-init attacks, compression triggers, rent sponsoring, CU overhead, Pinocchio handler generation).

## Reference

| Resource | Link |
|----------|------|
| Pinocchio swap reference | [pinocchio-swap](https://github.com/Lightprotocol/examples-light-token/tree/main/pinocchio/swap) |
| Full SDK implementation | [sdk.rs](https://github.com/Lightprotocol/examples-light-token/blob/main/pinocchio/swap/tests/sdk.rs) |
| Full test | [test_lifecycle.rs](https://github.com/Lightprotocol/examples-light-token/blob/main/pinocchio/swap/tests/test_lifecycle.rs) |
