# Client SDK

Implement `LightProgramInterface` in your program's SDK crate so routers/aggregators can integrate.

## LightProgramInterface Trait

```rust
pub trait LightProgramInterface {
    type Variant: Pack<AccountMeta> + Clone + Debug;
    type Instruction;

    fn program_id() -> Pubkey;
    fn instruction_accounts(&self, ix: &Self::Instruction) -> Vec<Pubkey>;
    fn load_specs(
        &self,
        cold_accounts: &[AccountInterface],
    ) -> Result<Vec<AccountSpec<Self::Variant>>, Box<dyn Error>>;
}
```

- `instruction_accounts` -- returns the pubkeys the instruction reads/writes.
- `load_specs` -- given cold `AccountInterface`s (with `ColdContext`), returns the `AccountSpec`s that `create_load_instructions` needs to bring them back on-chain.

## Anchor Example

```rust
pub struct AmmSdk {
    pub pool_state_pubkey: Pubkey,
    pub observation_key: Pubkey,
    pub token_0_vault: Pubkey,
    pub token_1_vault: Pubkey,
    pub token_0_mint: Pubkey,
    pub token_1_mint: Pubkey,
    pub lp_mint: Pubkey,
    pub amm_config: Pubkey,
}

pub enum AmmInstruction {
    Swap,
    Deposit,
    Withdraw,
}

impl LightProgramInterface for AmmSdk {
    type Variant = LightAccountVariant;
    type Instruction = AmmInstruction;

    fn program_id() -> Pubkey {
        PROGRAM_ID
    }

    fn instruction_accounts(&self, ix: &Self::Instruction) -> Vec<Pubkey> {
        match ix {
            AmmInstruction::Swap => vec![
                self.pool_state_pubkey,
                self.observation_key,
                self.token_0_vault,
                self.token_1_vault,
                self.token_0_mint,
                self.token_1_mint,
            ],
            AmmInstruction::Deposit | AmmInstruction::Withdraw => vec![
                self.pool_state_pubkey,
                self.observation_key,
                self.token_0_vault,
                self.token_1_vault,
                self.token_0_mint,
                self.token_1_mint,
                self.lp_mint,
            ],
        }
    }

    fn load_specs(
        &self,
        cold_accounts: &[AccountInterface],
    ) -> Result<Vec<AccountSpec<Self::Variant>>, Box<dyn Error>> {
        // Build AccountSpec for each cold account by matching pubkey
        // and deserializing its data into the macro-generated variant.
        let mut specs = Vec::new();
        for account in cold_accounts {
            let pubkey = account.key();
            if pubkey == self.pool_state_pubkey || pubkey == self.observation_key {
                let parsed: PoolState = AnchorDeserialize::deserialize(&mut &account.data()[8..])?;
                specs.push(AccountSpec::Pda(PdaSpec { interface: account.clone(), variant: parsed.into() }));
            } else if pubkey == self.token_0_vault || pubkey == self.token_1_vault {
                specs.push(AccountSpec::Token(account.clone()));
            }
            // ...
        }
        Ok(specs)
    }
}
```

| Resource | Link |
|----------|------|
| Trait Implementation Example | [CpSwapSdk](https://github.com/Lightprotocol/cp-swap-reference/blob/main/programs/cp-swap/tests/program.rs#L409) |

## Pinocchio Example

```rust
use light_client::interface::{
    AccountInterface, AccountSpec, ColdContext, LightProgramInterface, PdaSpec,
};
use light_account::token::Token;
use pinocchio_swap::{LightAccountVariant, PoolState, PoolStateSeeds, VaultSeeds};

/// Flat SDK struct. All fields populated at construction from pool state data.
pub struct SwapSdk {
    pub pool_state_pubkey: Pubkey,
    pub token_a_mint: Pubkey,
    pub token_b_mint: Pubkey,
    pub token_a_vault: Pubkey,
    pub token_b_vault: Pubkey,
    pub pool_authority: Pubkey,
}

impl SwapSdk {
    pub fn new(pool_state_pubkey: Pubkey, pool_data: &[u8]) -> Result<Self, SwapSdkError> {
        let pool = PoolState::deserialize(&mut &pool_data[8..])?;
        // ... derive addresses from pool state
        Ok(Self { pool_state_pubkey, /* ... */ })
    }
}

impl LightProgramInterface for SwapSdk {
    type Variant = LightAccountVariant;
    type Instruction = SwapInstruction;

    fn program_id() -> Pubkey { PROGRAM_ID }

    fn instruction_accounts(&self, ix: &Self::Instruction) -> Vec<Pubkey> {
        match ix {
            SwapInstruction::Swap => vec![
                self.pool_state_pubkey,
                self.token_a_vault,
                self.token_b_vault,
                self.token_a_mint,
                self.token_b_mint,
            ],
            // ...
        }
    }

    fn load_specs(
        &self,
        cold_accounts: &[AccountInterface],
    ) -> Result<Vec<AccountSpec<Self::Variant>>, Box<dyn std::error::Error>> {
        let mut specs = Vec::new();
        for account in cold_accounts {
            if account.key == self.pool_state_pubkey {
                let pool = PoolState::deserialize(&mut &account.data()[8..])?;
                let variant = LightAccountVariant::PoolState {
                    seeds: PoolStateSeeds { /* ... */ },
                    data: pool,
                };
                specs.push(AccountSpec::Pda(PdaSpec::new(account.clone(), variant, PROGRAM_ID)));
            } else if account.key == self.token_a_vault {
                let token: Token = Token::deserialize(&mut &account.data()[..])?;
                let variant = LightAccountVariant::Vault(TokenDataWithSeeds {
                    seeds: VaultSeeds { pool: /* ... */, mint: /* ... */ },
                    token_data: token,
                });
                specs.push(AccountSpec::Pda(PdaSpec::new(account.clone(), variant, PROGRAM_ID)));
            }
            // ... token_b_vault, mints
        }
        Ok(specs)
    }
}
```

| Resource | Link |
|----------|------|
| Full SDK implementation | [sdk.rs](https://github.com/Lightprotocol/examples-light-token/blob/main/pinocchio/swap/tests/sdk.rs) |

## Dependencies

```toml
[dependencies]
light-client = { version = "0.19.0", features = ["v2"] }
```