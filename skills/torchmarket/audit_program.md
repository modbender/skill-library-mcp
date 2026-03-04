# Torch Market Security Audit Summary

**Date:** February 27, 2026 | **Auditor:** Claude Opus 4.6 (Anthropic) | **Version:** V3.7.8 Production

---

## Scope

Four audits covering the full stack:

| Layer | Files | Lines | Report |
|-------|-------|-------|--------|
| On-chain program (V3.7.8) | 21 source files | ~6,800 | `audit.md` |
| Frontend & API | 37 files (17 API routes, 12 libs, 8 components) | -- | `SECURITY_AUDIT_FE_V2.4.1_PROD.md` |
| Agent Kit plugin (V4.0) | 4 files | ~1,900 | `SECURITY_AUDIT_AGENTKIT_V4.0.md` |
| Torch SDK (V2.0) | 9 files | ~2,800 | Included in Agent Kit V4.0 audit |

Program ID: `8hbUkonssSEEtkqzwM7ZcZrD9evacM92TcWSooVF4BeT`

---

## Findings Summary

### On-Chain Program (V3.7.8)

| Severity | Count | Details |
|----------|-------|---------|
| Critical | 0 | -- |
| High | 0 | -- |
| Medium | 3 | Lending enabled by default (accepted); Token-2022 transfer fee on collateral (inherent, 0.04% new / 0.03% legacy); Epoch rewards race condition (accepted) |
| Low | 7 | fund_vault_wsol decoupled accounting; Stranded WSOL lamports; Vault sol_balance drift; Sell no position check; Slot-based interest; Revival no virtual reserve update; Treasury lock ATA not Anchor-constrained (CPI validated, see V31 notes) |
| Informational | 24 | Various carried findings + 3 new V3.7.1 + 2 new V3.7.2 + 2 new V3.7.3 + 2 new V3.7.5 (I-20: zero-burn migration design; I-21: AccountInfo stack pressure mitigation) + 1 new V3.7.6 (I-22: reserve floor zeroed, fee split rebalanced) + 1 new V3.7.7 (I-23: buyback removed, lending cap increased) + 1 new V3.7.8 (I-24: creator revenue streams, transfer fee bump) |

**Rating: EXCELLENT -- Ready for Mainnet**

Key strengths:
- 27 instructions, 12 account types, 43 Kani formal verification proofs passed
- **V34 creator revenue**: Three new income streams for creators — bonding SOL share (0.2%→1% carved from treasury rate, linear growth), 15% of post-migration `swap_fees_to_sol` proceeds, and star payout (cost reduced 0.05→0.02 SOL). `creator` account added to `Buy` and `SwapFeesToSol` contexts, validated against `bonding_curve.creator`. Transfer fee bumped from 3 to 4 bps (new tokens only — old tokens immutable). 4 new Kani proofs verify creator rate bounds, monotonicity, subtraction safety, and fee share conservation
- **V33 buyback removal**: `execute_auto_buyback` instruction removed (~330 lines of handler + context). Eliminates a complex Raydium CPI instruction that spent treasury SOL providing exit liquidity during dumps, had a fee-inflation bug in vault balance reads, and competed with lending for treasury SOL. One fewer attack surface. Binary size reduced ~6% (850 KB → 804 KB). Treasury simplified to: fee harvest → sell high → SOL → lending yield + epoch rewards
- **V33 lending cap increase**: Utilization cap raised from 50% to 70%. More SOL available for community lending while maintaining 30% visible reserve. Conservative LTV/liquidation thresholds unchanged
- **V32 protocol treasury rebalance**: Reserve floor removed (1,500 SOL → 0) -- all fees distributed each epoch. Volume eligibility lowered (10 SOL → 2 SOL). New MIN_CLAIM_AMOUNT (0.1 SOL) prevents dust claims. Protocol fee split rebalanced from 75/25 to 90% treasury / 10% dev wallet. New `verify_min_claim_enforcement` Kani proof
- **V31 zero-burn migration**: Curve supply reduced from 750M to 700M. At graduation, `vault_remaining == tokens_for_pool` exactly -- zero excess tokens to burn. Cleaner migration with no deflationary side effect
- **V31 vote return → treasury lock**: Vote-return tokens now transfer to TreasuryLock PDA instead of Raydium LP injection. Preserves tokens for future governance release instead of diluting the pool
- **V31 supply split**: 700M curve (70%) + 300M locked (30%) = 1B total. Treasury lock increased from 250M to 300M for stronger community reserve
- **V31 transfer fee**: Reduced from 10 bps (0.1%) to 3 bps (0.03%). Round-trip cost ~0.006% instead of ~0.2%
- **V29 on-chain metadata**: Token-2022 MetadataPointer + TokenMetadata extensions replace Metaplex dependency. Metadata immutably stored on the mint itself. Pointer authority is `None` (permanently immutable). SDK tests verify name/symbol/uri round-trip via `getTokenMetadata()`
- **V29 Metaplex removal**: `add_metadata` (Metaplex backfill for legacy tokens) was temporary -- 13/24 succeeded, remaining 11 have old account layouts. All Metaplex code removed: `METAPLEX_PROGRAM_ID` constant, `build_create_metaplex_metadata_instruction`, `AddMetadata` context, `add_metadata` handler, `InvalidMetadataAccount` error. L-9 (untyped mint AccountInfo) is now moot
- **V20 swap_fees_to_sol**: Closed economic loop verified -- treasury tokens sold on Raydium, WSOL unwrapped, SOL credited back to same treasury. No external routing possible
- **V20 vault ordering fix**: `order_mints()` now correctly orders pool vaults by mint pubkey for `validate_pool_accounts` in `swap_fees_to_sol`
- **V27 PDA-based pool validation** eliminates oracle spoofing at the Anchor constraint level (cryptographically unforgeable)
- **V27 treasury lock**: 300M tokens (30%) permanently locked in TreasuryLock PDA. No withdrawal instruction exists
- **V27 supply conservation**: 700M curve + 300M locked = 1B total, verified via two separate `mint_to` CPIs
- **V26 permissionless migration**: SOL custody preserved via `bc_wsol` intermediary. CPI isolation via `fund_migration_wsol`
- **V28 zero-cost migration**: Payer fronts ~1 SOL for Raydium costs, treasury reimburses exact amount via lamport snapshot (pre/post CPI). Net cost to payer: 0 SOL. `MIN_MIGRATION_SOL` (1.5 SOL) safety floor replaces fixed `RAYDIUM_POOL_CREATION_FEE`
- **V3.7.1 MigrateToDex amm_config constrained**: Address constraint added to prevent pool creation with wrong Raydium fee tier (defense-in-depth, matches existing constraint on VaultSwap and SwapFeesToSol)
- **V26/V29 authority revocation**: Mint, freeze, and transfer fee config authorities all revoked to `None` at migration (permanent, irreversible). Supply capped, trading unrestricted, fee rate locked forever
- **V28 minimal admin surface**: Only `initialize` and `update_dev_wallet` require authority. `update_authority` removed
- Checked arithmetic everywhere with u128 intermediaries for overflow-prone multiplication
- All 15 PDA types use unique seeds with stored bumps
- Vault full custody verified: closed economic loop across buy, sell, star, borrow, repay, DEX swap, and fee swap
- CPI ordering rule enforced: token CPIs before lamport manipulation in all vault paths
- Authority separation: creator (immutable seed) vs authority (transferable) vs controller (disposable signer)

---

## V20: `swap_fees_to_sol` -- Deep Audit

### Overview

New instruction that sells harvested Token-2022 transfer fee tokens back to SOL via Raydium CPMM. Permissionless -- anyone can call post-migration. Completes the fee lifecycle: transfer fees (0.03%) accumulate as tokens, `harvest_fees` collects them, `swap_fees_to_sol` converts to SOL for lending yield and epoch rewards.

**Files audited:**
- `handlers/treasury.rs` (lines 82-207) -- handler logic
- `contexts.rs` (lines 443-540) -- `SwapFeesToSol` account context
- `pool_validation.rs` -- `order_mints`, `validate_pool_accounts`, `read_token_account_balance`
- `state.rs` -- Treasury struct, `harvested_fees` field
- `constants.rs` -- seeds, program IDs
- `lib.rs` -- instruction entry point

### Account Context Verification

All 16 accounts in `SwapFeesToSol` verified:

| Account | Constraint | Verdict |
|---------|-----------|---------|
| `payer` | `Signer`, mutable | SAFE -- permissionless, pays gas only |
| `mint` | `InterfaceAccount<MintInterface>`, mutable | SAFE -- typed, Token-2022 validated via bonding_curve |
| `bonding_curve` | PDA `[BONDING_CURVE_SEED, mint]`, `migrated` + `is_token_2022` | SAFE -- prevents pre-migration and non-Token-2022 calls |
| `treasury` | PDA `[TREASURY_SEED, mint]`, mutable | SAFE -- receives SOL, same treasury that owns the tokens |
| `treasury_token_account` | `associated_token::mint/authority/token_program` | SAFE -- can only be treasury's Token-2022 ATA |
| `treasury_wsol` | Address = `get_associated_token_address(&treasury, &WSOL_MINT)` | SAFE -- can only be treasury's WSOL ATA |
| `raydium_program` | Address = `RAYDIUM_CPMM_PROGRAM_ID` | SAFE -- hardcoded |
| `raydium_authority` | Unconstrained | LOW -- Raydium validates internally (see L-8) |
| `amm_config` | Address = `RAYDIUM_AMM_CONFIG` | SAFE -- hardcoded, prevents fee tier substitution |
| `pool_state` | Address = `derive_pool_state(&mint)` | SAFE -- PDA-derived, unforgeable |
| `token_vault` | Address = `derive_pool_vault(&pool_state, &mint)` | SAFE -- PDA-derived, unforgeable |
| `wsol_vault` | Address = `derive_pool_vault(&pool_state, &WSOL_MINT)` | SAFE -- PDA-derived, unforgeable |
| `wsol_mint` | Address = `WSOL_MINT` | SAFE -- hardcoded |
| `observation_state` | Address = `derive_observation_state(&pool_state)` | SAFE -- PDA-derived |
| `token_program` | `Interface<TokenInterface>` | SAFE -- Anchor validates |
| `token_2022_program` | Address = `TOKEN_2022_PROGRAM_ID` | SAFE -- hardcoded |

### Handler Logic Verification

**Step-by-step trace through `swap_fees_to_sol` (treasury.rs:96-207):**

| Step | Code | Finding |
|------|------|---------|
| 1. Pool validation | `order_mints` + `validate_pool_accounts` with correctly ordered vaults | SAFE -- defense-in-depth, vaults passed in pool order (vault_0/vault_1 by mint pubkey), not swap direction |
| 2. Token balance check | `token_amount > 0`, `minimum_amount_out > 0` | SAFE -- prevents empty swaps and 0-value slippage |
| 3. WSOL balance before | `read_token_account_balance(&treasury_wsol)` | SAFE -- handles pre-existing WSOL via before/after diff |
| 4. Treasury signer | `[TREASURY_SEED, mint, bump]` | SAFE -- standard PDA signer |
| 5. Raydium swap CPI | `swap_base_input(token_amount, minimum_amount_out)` | SAFE -- see CPI analysis below |
| 6. WSOL balance after | `wsol_balance_after.checked_sub(wsol_balance_before)` | SAFE -- checked arithmetic, only counts swap proceeds |
| 7. Slippage check | `sol_received >= minimum_amount_out` | SAFE -- belt-and-suspenders (Raydium also enforces) |
| 8. Close WSOL ATA | `close_account(treasury_wsol → treasury)` | SAFE -- SOL returns to treasury PDA |
| 9. State update | `sol_balance += sol_received`, `harvested_fees += sol_received` | SAFE -- checked arithmetic, credits same treasury |

### Raydium CPI Analysis

The swap CPI correctly maps accounts for the **sell direction** (Token-2022 → WSOL):

| CPI Field | Account | Token Standard | Direction |
|-----------|---------|---------------|-----------|
| `input_token_account` | `treasury_token_account` | Token-2022 | Tokens being sold |
| `output_token_account` | `treasury_wsol` | SPL Token | WSOL being received |
| `input_vault` | `token_vault` | -- | Pool receives tokens |
| `output_vault` | `wsol_vault` | -- | Pool sends WSOL |
| `input_token_program` | `token_2022_program` | Token-2022 | For input token |
| `output_token_program` | `token_program` | SPL Token | For WSOL output |
| `payer` (signer) | `treasury` PDA | -- | Treasury signs swap |

Verified against `vault_swap` sell path (swap.rs:183-250) -- same Raydium CPI pattern with correctly mapped token programs for the sell direction.

### Fund Flow Analysis -- Can Funds Be Drained?

**Critical question: Is there any path where SOL or tokens leave the treasury's control?**

```
Treasury Token ATA (Token-2022 tokens)
    │ swap_base_input CPI
    ▼
Raydium Pool (token_vault receives tokens, wsol_vault sends WSOL)
    │
    ▼
Treasury WSOL ATA (receives WSOL)
    │ close_account CPI
    ▼
Treasury PDA (receives SOL = WSOL lamports)
    │ state update
    ▼
treasury.sol_balance += sol_received
```

**Every hop in this chain is constrained to treasury-owned accounts:**

1. **Source**: `treasury_token_account` -- constrained as treasury's Token-2022 ATA via `associated_token` Anchor macro. Cannot be substituted.
2. **Intermediate**: `treasury_wsol` -- constrained as `get_associated_token_address(&treasury, &WSOL_MINT)`. Cannot be substituted.
3. **Destination**: `treasury.key()` in both `close_account` args (destination AND authority). SOL returns to treasury PDA.
4. **State**: `treasury.sol_balance` credits the same treasury account.

**Verdict: NO DRAIN POSSIBLE. The instruction is a closed economic loop within the treasury.**

### Attack Vector Analysis

| # | Vector | Mitigation | Verdict |
|---|--------|-----------|---------|
| 1 | **Pool substitution** -- pass fake Raydium pool | `pool_state` = `derive_pool_state(&mint)` (PDA, unforgeable). `token_vault`/`wsol_vault` = PDA-derived from pool_state. `amm_config` = hardcoded address. Runtime `validate_pool_accounts()` double-checks. | NOT POSSIBLE |
| 2 | **Sandwich attack** -- front-run/back-run to extract MEV | `minimum_amount_out` slippage protection. Caller sets via SDK based on current price. Tx reverts if output below threshold. | MITIGATED |
| 3 | **Repeated calls** -- drain via multiple invocations | First call swaps all tokens (full balance). Second call hits `require!(token_amount > 0)` and reverts. SOL always returns to same treasury. | NOT POSSIBLE |
| 4 | **Fund routing** -- redirect output to attacker wallet | WSOL destination = treasury's ATA (address-constrained). Close destination = treasury PDA (hardcoded in CPI args). No external wallet referenced. | NOT POSSIBLE |
| 5 | **Pre-migration exploit** -- call before pool exists | `bonding_curve.migrated` constraint. No pool = no swap. | NOT POSSIBLE |
| 6 | **Non-Token-2022 token** -- call on legacy token | `bonding_curve.is_token_2022` constraint. Legacy tokens have no transfer fees. | NOT POSSIBLE |
| 7 | **Vote vault theft** -- steal pre-vote tokens | Only callable post-migration. Vote vault resolved before migration completes (burned or returned). Treasury token ATA only contains harvested fee tokens post-migration. | NOT POSSIBLE |
| 8 | **WSOL account injection** -- fake WSOL ATA | `treasury_wsol` address-constrained to ATA derivation. Deterministic, unforgeable. | NOT POSSIBLE |
| 9 | **Reentrancy** -- re-enter during CPI | Solana runtime prevents reentrancy within same transaction. | NOT POSSIBLE |
| 10 | **Stale WSOL balance** -- count pre-existing WSOL as proceeds | Before/after diff pattern: `sol_received = wsol_after - wsol_before`. Only counts swap delta. | MITIGATED |
| 11 | **Treasury state desync** -- accounting mismatch | `sol_balance += sol_received` uses checked arithmetic. SOL physically arrives at treasury PDA via WSOL close. Accounting matches reality. | MITIGATED |

### V20 New Findings

**~~L-8 (Low): `raydium_authority` has no explicit address constraint~~ -- RESOLVED (V33)**

The `raydium_authority` account in `SwapFeesToSol` context had no `address = ...` constraint. Raydium validates its own authority PDA internally. `TreasuryBuybackDex` (which also had this pattern) was removed in V33. Only `SwapFeesToSol` and `VaultSwap` remain -- both rely on Raydium's internal validation. Not exploitable.

**I-16 (Informational): `harvested_fees` field semantic change**

The `Treasury.harvested_fees` field (declared in V3, never previously written to) is now repurposed to track cumulative SOL earned from fee swaps. The field name suggests "harvested token fees" but now stores SOL amounts. No layout change, no migration needed. Cosmetic only -- no security impact.

**I-17 (Informational): WSOL ATA rent not tracked in `sol_balance`**

When `treasury_wsol` is closed, the treasury PDA receives both swap proceeds (token balance) and rent-exempt lamports. Only the token balance (via before/after diff) is added to `treasury.sol_balance`. The rent lamports become untracked SOL in the treasury PDA. This is consistent with `vault_swap` (the only other WSOL-closing path since `execute_auto_buyback` was removed in V33). Dust-level amounts, not exploitable.

### V20 Vault Ordering Fix Verification

The `order_mints()` fix in `swap_fees_to_sol` was verified:

```rust
// swap_fees_to_sol (treasury.rs:104-111)
let (mint_0, _) = order_mints(&mint_key);
let (vault_0, vault_1) = if mint_0 == mint_key {
    (&ctx.accounts.token_vault, &ctx.accounts.wsol_vault)
} else {
    (&ctx.accounts.wsol_vault, &ctx.accounts.token_vault)
};
```

Correctly passes vaults in **pool order** (vault_0/vault_1 by mint pubkey comparison) to `validate_pool_accounts`, while the Raydium CPI receives vaults in **swap direction** order (input/output). These are independent concerns and both are handled correctly. (Note: `execute_auto_buyback` which had the same pattern was removed in V33.)

---

## V29: Token Metadata + Transfer Fee Changes -- Deep Audit

### Overview

V29 makes two changes: (1) new tokens store metadata on-chain via Token-2022 MetadataPointer + TokenMetadata extensions, replacing the Metaplex dependency; (2) transfer fee reduced from 1% (100 bps) to 0.03% (3 bps) with fee config authority revoked at migration. The `add_metadata` instruction (Metaplex backfill for legacy tokens) was temporary and has been removed -- all Metaplex code is deleted.

**Files audited:**
- `handlers/token.rs` -- create_token with Token-2022 metadata extensions
- `token_2022_utils.rs` -- metadata pointer and token metadata instruction builders
- `constants.rs` -- metadata extension sizes
- `migration.rs` (lines 377-389) -- transfer fee config authority revocation

### `create_token` Metadata Extension Verification

**Extension initialization order (critical -- Token-2022 requires specific ordering):**

| Step | Extension | When | Verified |
|------|-----------|------|----------|
| 1 | `create_account` | Before all inits | SAFE -- space = TransferFeeConfig + MetadataPointer only (346 bytes) |
| 2 | `InitializeTransferFeeConfig` | Before InitializeMint2 | SAFE -- fee config authority = bonding curve PDA, withdraw authority = treasury PDA |
| 3 | `InitializeMetadataPointer` | Before InitializeMint2 | SAFE -- authority = None (immutable), metadata address = mint itself |
| 4 | `InitializeMint2` | After all extension inits | SAFE -- mint/freeze authority = bonding curve PDA |
| 5 | `system_program::transfer` | After InitializeMint2 | SAFE -- funds mint account for TokenMetadata realloc rent |
| 6 | `InitializeTokenMetadata` | After InitializeMint2 | SAFE -- Token-2022 reallocs internally. Bonding curve PDA signs as mint authority |

**Two-phase allocation pattern (I-19):**
The mint is created with space for TransferFeeConfig + MetadataPointer only (346 bytes). Before TokenMetadata init, additional rent lamports are transferred to the mint via `system_program::transfer`. Token-2022 then reallocs the account internally when processing `InitializeTokenMetadata`. This avoids Token-2022's `InvalidAccountData` error when uninitialized TLV entries exist at `InitializeMint2` time.

**Metadata pointer authority = None (I-18):**
The metadata pointer is initialized with `authority = None`, meaning the pointer target (mint itself) can never be changed. This is the correct choice -- the metadata lives on the mint and should never point elsewhere.

### Transfer Fee Config Authority Revocation Verification

```rust
// migration.rs:377-389
set_authority(
    CpiContext::new_with_signer(
        ctx.accounts.token_2022_program.to_account_info(),
        SetAuthority {
            current_authority: ctx.accounts.bonding_curve.to_account_info(),
            account_or_mint: ctx.accounts.mint.to_account_info(),
        },
        bc_signer,
    ),
    AuthorityType::TransferFeeConfig,
    None,  // revoked permanently
)?;
```

**Verified:** This follows the same pattern as the existing mint authority and freeze authority revocations (lines 354-375). `AuthorityType::TransferFeeConfig` with `new_authority = None` is irreversible -- Token-2022 rejects `SetAuthority` when the current authority is `None`. The 0.03% fee rate is locked forever post-migration.

**Three authorities now revoked at migration:**
1. Mint authority → `None` (supply capped)
2. Freeze authority → `None` (free trading guaranteed)
3. Transfer fee config authority → `None` (0.03% fee rate locked)

### V29 New Findings

**~~L-9 (Low): `add_metadata` mint is untyped `AccountInfo`~~ -- REMOVED**

The `add_metadata` instruction and `AddMetadata` context have been deleted. This finding is no longer applicable.

**I-18 (Informational): Metadata pointer authority permanently `None`**

The MetadataPointer extension is initialized with `authority = None`, making the pointer permanently immutable. The pointer target is the mint itself. This is the correct configuration -- there is no reason to ever change where metadata is stored.

**I-19 (Informational): Two-phase mint allocation pattern**

The mint account is created with 346 bytes (TransferFeeConfig + MetadataPointer), then Token-2022 reallocs internally during `InitializeTokenMetadata`. The creator pays additional rent via `system_program::transfer` before the metadata init. This is a standard Token-2022 pattern -- pre-allocating the full space causes `InitializeMint2` to fail due to uninitialized TLV entries in the trailing bytes.

---

## V31: Zero-Burn Migration + Treasury Lock Vote Return -- Deep Audit

### Overview

V31 makes three changes: (1) curve supply reduced from 750M to 700M, treasury lock increased from 250M to 300M -- at graduation, `vault_remaining == tokens_for_pool` exactly, eliminating the ~50M excess token burn; (2) vote-return tokens now transfer to TreasuryLock PDA instead of Raydium LP injection; (3) transfer fee reduced from 10 bps to 3 bps (0.03%).

**Files audited:**
- `contexts.rs` -- `MigrateToDex` account context (treasury_lock_token_account downgraded to AccountInfo)
- `migration.rs` -- vote return transfer to treasury lock, manual ATA validation
- `constants.rs` -- CURVE_SUPPLY, TREASURY_LOCK_TOKENS, TRANSFER_FEE_BPS
- `handlers/token.rs` -- updated mint_to amounts (700M/300M)
- `errors.rs` -- `InvalidTokenAccount` error variant

### Zero-Burn Migration Verification

**Before V31:** `CURVE_SUPPLY = 750M`, `TREASURY_LOCK = 250M`. At graduation with 200 SOL target, `tokens_for_pool ≈ 700M` (computed from price matching), leaving ~50M excess tokens burned.

**After V31:** `CURVE_SUPPLY = 700M`, `TREASURY_LOCK = 300M`. At graduation, `tokens_for_pool == vault_remaining` exactly. The `excess_tokens` burn path (migration.rs:208-225) still exists as a safety net but fires with `excess_tokens = 0` for V31 tokens.

**Supply conservation:** `700M + 300M = 1B` total supply. Verified via two separate `mint_to` CPIs in `create_token`. The 39 Kani formal verification proofs include `verify_price_matched_pool_flame` which validates the zero-excess property.

### Vote Return → Treasury Lock Verification

**Previous behavior (V27):** Vote-return tokens were added to Raydium LP, diluting the pool at migration.

**V31 behavior:** Vote-return tokens transfer to `treasury_lock_token_account` via `transfer_checked` CPI with treasury as signer.

```rust
// migration.rs (V31 vote return path)
if bonding_curve.vote_result_return {
    let expected_lock_ata = get_associated_token_address_2022(
        &ctx.accounts.treasury_lock.key(),
        &mint_key,
    );
    require!(
        ctx.accounts.treasury_lock_token_account.key() == expected_lock_ata,
        TorchMarketError::InvalidTokenAccount
    );
    transfer_checked(/* treasury → treasury_lock_token_account */);
}
```

**Validation chain:**
1. `treasury_lock` is `Box<Account<'info, TreasuryLock>>` -- Anchor validates discriminator and PDA
2. `treasury_lock_token_account` is `AccountInfo` with manual ATA address validation
3. `get_associated_token_address_2022` derives the expected ATA deterministically
4. `require!` rejects mismatched addresses with `InvalidTokenAccount`
5. `transfer_checked` CPI validates the account is a valid Token-2022 token account

### AccountInfo Stack Pressure Mitigation (I-21)

The `treasury_lock_token_account` was downgraded from `Box<InterfaceAccount<TokenAccount>>` with `associated_token::` constraints to plain `AccountInfo` with `#[account(mut)]`. This was necessary because the Anchor-generated `try_accounts` validation code for `MigrateToDex` (which has ~25 accounts) exceeded the Solana BPF 4KB stack frame limit.

**Security impact:** None. The manual ATA validation in the handler provides equivalent security:
- ATA addresses are deterministic (derived from owner + mint + Token-2022 program)
- An attacker cannot forge an ATA address -- it's a PDA with fixed seeds
- `transfer_checked` CPI validates the destination is a valid token account
- The `treasury_lock` account itself is still fully typed and PDA-validated by Anchor

This pattern is analogous to how `raydium_authority` is left unconstrained (L-8) -- the CPI target validates internally.

### Backward Compatibility

Tokens created on v3.7.4 (750M curve / 250M lock) will use the new V31 migration handler when they graduate. They get the new vote-return → treasury lock path, but their creation-time economics are preserved:
- Supply split remains 750M/250M (stored on-chain at creation)
- Transfer fee rate remains whatever was set at mint creation (immutable)
- The ~50M excess burn still occurs (vault_remaining > tokens_for_pool for old supply split)

### V31 New Findings

**I-20 (Informational): Zero-burn migration design**

The V31 supply split (700M/300M) is calibrated so that `vault_remaining == tokens_for_pool` at the 200 SOL bonding target. This eliminates the ~50M deflationary burn at migration, making the supply more predictable. The excess burn code path is retained as a safety net. This property is verified by the `verify_price_matched_pool_flame` Kani proof.

**I-21 (Informational): AccountInfo stack pressure mitigation**

The `treasury_lock_token_account` in `MigrateToDex` uses `AccountInfo` instead of a typed Anchor account to reduce stack frame size. The `associated_token::` macro generates heavy validation code in `try_accounts` that, combined with ~25 other accounts in the context, exceeded the 4KB BPF stack limit. Manual ATA validation in the handler provides equivalent security guarantees. This is a standard Solana optimization pattern for large account contexts.

---

## V32: Protocol Treasury Rebalance -- Deep Audit

### Overview

V32 changes four protocol constants and adds a min claim guard. No new instructions, no new accounts, no state struct changes. Pure economics rebalance: more fees to traders, lower entry barrier, dust claim protection.

**Files audited:**
- `constants.rs` -- PROTOCOL_TREASURY_RESERVE_FLOOR (→0), MIN_EPOCH_VOLUME_ELIGIBILITY (→2 SOL), DEV_WALLET_SHARE_BPS (→1000), new MIN_CLAIM_AMOUNT
- `handlers/protocol_treasury.rs` -- min claim check in `claim_protocol_rewards`
- `errors.rs` -- `ClaimBelowMinimum` error variant

### Constant Changes Verification

| Constant | Before | After | Security Impact |
|----------|--------|-------|-----------------|
| `PROTOCOL_TREASURY_RESERVE_FLOOR` | 1,500 SOL | 0 SOL | Rent-exempt minimum still subtracted (line 61). Account stays alive. No drain risk. |
| `MIN_EPOCH_VOLUME_ELIGIBILITY` | 10 SOL | 2 SOL | More claimants, smaller individual shares. Intentional -- broader distribution. |
| `DEV_WALLET_SHARE_BPS` | 2500 (25%) | 1000 (10%) | Same arithmetic path in buy handler. `dev_share = total * 1000 / 10000`. No overflow risk. |
| `MIN_CLAIM_AMOUNT` | (new) | 0.1 SOL | New `require!` guard. Prevents dust drain via many micro-claims. |

### Min Claim Guard Verification

```rust
// handlers/protocol_treasury.rs (V32)
let claim_amount = user_share.min(ctx.accounts.protocol_treasury.distributable_amount);

// [V32] Reject dust claims below minimum
require!(
    claim_amount >= MIN_CLAIM_AMOUNT,
    TorchMarketError::ClaimBelowMinimum
);
```

**Analysis:**
- Guard placed after share calculation, before SOL transfer -- correct position
- Uses `>=` (not `>`) -- 0.1 SOL exactly is accepted
- `MIN_CLAIM_AMOUNT = 100_000_000` lamports (0.1 SOL) -- verified matches constant
- New `ClaimBelowMinimum` error variant added to `TorchMarketError` enum
- Error message string updated: "need >= 2 SOL/epoch" (was 10 SOL)

### Attack Vector Analysis

| # | Vector | Mitigation | Verdict |
|---|--------|-----------|---------|
| 1 | **Dust drain** -- many accounts claim tiny amounts | MIN_CLAIM_AMOUNT (0.1 SOL) floor. Claims below threshold revert. | MITIGATED |
| 2 | **Reserve floor = 0 drain** -- treasury emptied each epoch | Distributable = available - rent_exempt. Account survives. Each claim decrements distributable_amount. | SAFE |
| 3 | **Volume manipulation** -- fake 2 SOL volume to claim | Volume tracked via buy/sell handlers with real SOL flow. Cannot inflate without actual trades. | NOT POSSIBLE |
| 4 | **Fee split arbitrage** -- exploit 90/10 change | Constant-only change. Same `checked_mul/checked_div` path. No timing exploit. | NOT POSSIBLE |

### V32 New Findings

**I-22 (Informational): Reserve floor zeroed with min claim protection**

The reserve floor removal (1,500 SOL → 0) means all accumulated fees are distributed each epoch. The new MIN_CLAIM_AMOUNT (0.1 SOL) prevents the theoretical dust drain vector where many low-volume accounts could claim tiny amounts. The combination is sound -- broader access with a sensible floor on individual claims. The `verify_min_claim_enforcement` Kani proof formally verifies that claims passing the check are genuinely >= 0.1 SOL.

---

## V33: Buyback Removal + Lending Cap Increase -- Deep Audit

### Overview

V33 removes the `execute_auto_buyback` instruction entirely (~330 lines of handler + context) and increases the lending utilization cap from 50% to 70%. No new instructions, no state struct layout changes. Pure simplification: fewer code paths, smaller binary, reduced attack surface.

**Rationale for removal:**
1. **Fee-inflation bug** -- buyback read Raydium vault balances including unclaimed protocol/fund fees, inflating apparent price ratio. V32 patched the read but added complexity.
2. **Exit liquidity subsidy** -- spent treasury SOL buying during dumps, effectively subsidizing sellers when treasury should conserve.
3. **SOL competition** -- buyback, lending, and epoch rewards all competed for the same treasury SOL.
4. **Never triggered in testing** -- sell cycle (`swap_fees_to_sol`) always ran first due to higher threshold sensitivity.

**Files audited:**
- `lib.rs` -- instruction entry point removed
- `handlers/migration.rs` -- handler delegation removed
- `migration.rs` -- `execute_auto_buyback_handler` (230 lines) removed, migration init simplified
- `contexts.rs` -- `TreasuryBuybackDex` struct (100 lines) removed
- `constants.rs` -- 4 buyback constants removed, lending cap updated
- `handlers/token.rs` -- buyback config fields zeroed instead of initialized
- `kani_proofs.rs` -- proof #18 comment updated

### Removed Code Verification

**Instruction removed from `lib.rs`:**
```rust
// REMOVED (V33)
pub fn execute_auto_buyback(ctx: Context<TreasuryBuybackDex>) -> Result<()> {
    handlers::migration::execute_auto_buyback(ctx)
}
```

Instruction count: 28 → 27. One fewer entry point in the dispatch table.

**Handler removed from `migration.rs` (~230 lines):**
The handler performed: cooldown check → Raydium vault balance read → ratio calculation → treasury SOL allocation → Raydium swap CPI → state update. All of this logic is now dead code -- the instruction that called it no longer exists.

**Context removed from `contexts.rs` (~100 lines):**
`TreasuryBuybackDex` had 16 accounts with PDA constraints for Raydium CPMM interaction. Removing this struct eliminates one entire CPI surface with Raydium.

**Constants removed from `constants.rs`:**

| Constant | Value | Was Used By |
|----------|-------|-------------|
| `DEFAULT_RATIO_THRESHOLD_BPS` | 8000 (80%) | Buyback trigger only |
| `DEFAULT_RESERVE_RATIO_BPS` | 3000 (30%) | Buyback amount calc only |
| `DEFAULT_BUYBACK_PERCENT_BPS` | 1500 (15%) | Buyback amount calc only |
| `MIN_BUYBACK_AMOUNT` | 0.01 SOL | Buyback minimum check only |

**Shared infrastructure kept** (used by sell cycle):
- `RATIO_PRECISION` (1e9) -- ratio math in `swap_fees_to_sol`
- `DEFAULT_MIN_BUYBACK_INTERVAL_SLOTS` (2700) -- sell cycle cooldown
- `DEFAULT_SELL_THRESHOLD_BPS` (12000) -- sell cycle trigger
- Baseline fields (`baseline_sol_reserves`, `baseline_token_reserves`, `baseline_initialized`)
- `read_pool_accumulated_fees` -- sell cycle fee correction

### Treasury Struct Layout Verification

On-chain accounts cannot have fields removed without migration. Deprecated buyback fields remain in the `Treasury` struct as dead weight:

| Field | Status | New Token Value |
|-------|--------|-----------------|
| `ratio_threshold_bps` | Deprecated (V33) | 0 |
| `reserve_ratio_bps` | Deprecated (V33) | 0 |
| `buyback_percent_bps` | Deprecated (V33) | 0 |
| `total_bought_back` | Deprecated (V33) | 0 |
| `total_burned_from_buyback` | Deprecated (V33) | 0 |
| `buyback_count` | Deprecated (V33) | 0 |

**Verified:** `handlers/token.rs` now explicitly zeros these fields at token creation. Existing migrated tokens retain their historical values but the instruction to act on them no longer exists. No deserialization issues -- layout is identical.

### Lending Utilization Cap Increase

`DEFAULT_LENDING_UTILIZATION_CAP_BPS`: 5000 (50%) → 7000 (70%)

**Impact analysis:**
- 30% visible reserve remains in per-token treasury -- sufficient for confidence
- More SOL available for community lending → borrowers buy tokens → more volume → more fees
- Conservative LTV (50%) and liquidation threshold (65%) unchanged
- Worst case: 70% lent, all borrowers default, 50% of collateral value recovered via liquidation. Treasury retains 30% reserve + liquidation proceeds (~35% of lent amount). Net loss bounded at ~22.5% of total treasury SOL in catastrophic scenario.

**Code change:** Single constant update. The utilization check in `borrow` handler (`treasury.total_lent + amount <= cap * treasury.sol_balance / 10000`) uses the same checked arithmetic path.

### Attack Vector Analysis

| # | Vector | Mitigation | Verdict |
|---|--------|-----------|---------|
| 1 | **Stale buyback instruction call** -- client sends old buyback tx | Instruction removed from program dispatch. Anchor returns `InvalidInstructionData` or `InstructionFallbackNotFound`. | NOT POSSIBLE |
| 2 | **Layout mismatch** -- zeroed fields cause deserialization error | Layout unchanged. Zero is a valid `u64` value. Anchor deserializes normally. | NOT POSSIBLE |
| 3 | **Sell cycle broken** -- removal affects shared code | Sell cycle (`swap_fees_to_sol`) uses its own handler, context, and shared constants. No code paths shared with removed buyback handler. Verified: `cargo build` succeeds, sell cycle handler unchanged. | NOT POSSIBLE |
| 4 | **Lending over-extension** -- 70% cap too aggressive | 50% max LTV + 65% liquidation threshold unchanged. Liquidation keepers incentivized with 10% bonus. 30% reserve always available for withdrawals. | ACCEPTABLE |
| 5 | **Historical data corruption** -- existing tokens with buyback history | Read-only. Fields retain historical values. No instruction exists to modify them. | NOT POSSIBLE |

### Binary Size Reduction

~850 KB → ~804 KB (~6% reduction). Removing the `TreasuryBuybackDex` context (100 lines of Anchor-generated validation code) and the handler (230 lines with Raydium CPI) accounts for the reduction.

### V33 New Findings

**I-23 (Informational): Buyback removed, lending cap increased**

The `execute_auto_buyback` instruction was removed in its entirety -- handler, context, and 4 dedicated constants. Treasury SOL is no longer spent on market buys during price dips. The lending utilization cap was increased from 50% to 70%, making more SOL available for community lending. Both changes are pure simplification with no new attack surface. The 6 deprecated Treasury fields remain in the struct at zero values for layout compatibility. The sell cycle (`swap_fees_to_sol`) continues to operate with its own ratio gating, baseline tracking, and cooldown logic -- fully independent of the removed buyback.

### V34 New Findings (V3.7.8)

**I-24 (Informational): Creator revenue streams, transfer fee bump**

V34 introduces three creator income streams: (1) a 0.2%→1% SOL share during bonding carved from the existing 20%→5% treasury rate (linear growth formula: `creator = 0.2% + 0.8% × reserves/target`), (2) 15% of post-migration `swap_fees_to_sol` proceeds (85% to treasury, 15% to creator via direct lamport transfer), and (3) star payout at 2000 stars (cost reduced from 0.05 to 0.02 SOL, so ~40 SOL payout instead of ~100 SOL).

**Security analysis:**
- Creator account validated against `bonding_curve.creator` in both `Buy` and `SwapFeesToSol` contexts via Anchor `constraint` — no account substitution possible
- Creator SOL share is carved FROM the existing treasury split, not added — total extraction from buyer unchanged. Kani proof `verify_creator_rate_less_than_treasury_rate` proves subtraction safety at all points
- Direct lamport transfer to creator in `swap_fees_to_sol` follows the same treasury-owned PDA pattern as existing lamport manipulations. Works even if creator wallet is garbage-collected (Solana runtime adds lamports to any address)
- Transfer fee bumped from 3→4 bps for new tokens. Old tokens retain 3 bps (immutable — fee config authority was revoked to `None` at migration)
- Self-buy discount for creators during bonding (0.2%→1% of their own buy) is negligible and incentive-aligned
- 4 new Kani proofs: `verify_creator_rate_bounds`, `verify_creator_rate_monotonic`, `verify_creator_rate_less_than_treasury_rate`, `verify_creator_fee_share_bounded`. All passing. Conservation property updated in `verify_sol_distribution_conservation` (now 5-way sum)

No new accounts, no new instructions, no state struct changes. `creator` account added to two existing contexts.

---

### Frontend & API Routes

| Severity | Count | Details |
|----------|-------|---------|
| Critical | 0 | **Fixed:** RPC proxy method allowlist (read-only only) |
| High | 0 | **Fixed:** Amount bounds validation on buy/sell routes; CSP updated for Jupiter API |
| Medium | 5 | SSRF via metadata URI fetch; Vanity grinding DoS; No rate limiting; Slippage unbounded (**Fixed**); SAID confirm feedback spoofing |
| Low | 5 | skipPreflight on all txs; BigInt conversion throws; Unoptimized images; SAID proxy passthrough; API sell route account layout |
| Informational | 5 | Good security headers; No dangerouslySetInnerHTML; Env vars properly segregated; Wallet adapter correct; Transaction preview shown |

**Rating: GOOD with targeted improvements needed**

Post-audit fixes applied:
- **C-1 Fixed:** RPC proxy now allowlists 37 read-only methods, blocks `sendTransaction` and all write methods
- **H-1 Fixed:** Buy route validates 0.001-500 SOL bounds; Sell route validates 1-1B token bounds; Slippage clamped 0.1%-10%
- **H-2 Fixed:** CSP `connect-src` updated with `https://api.jup.ag`

### Agent Kit Plugin (V4.0 -- Vault-Only)

| Severity | Count | Details |
|----------|-------|---------|
| Critical | 0 | **Resolved from V1.6:** Blind signing eliminated -- transactions are now built locally via Anchor IDL |
| High | 0 | **Resolved from V1.6:** No API dependency -- no TLS pinning needed, no server trust required |
| Medium | 1 | SAID feedback endpoint is unauthenticated (best-effort, non-critical) |
| Low | 3 | Memo not sanitized for control characters (max 500 chars); signOrSendTX delegates signing to agent kit (correct but opaque); Spot price oracle for lending collateral (inherits on-chain limitation) |
| Informational | 5 | All state reads via RPC (no caching, fresh every call); Slippage default 100bps (1%) hardcoded per-tool; Action handlers catch all errors (no uncaught throws); E2E test suite covers 21 tests; `buildDirectBuyTransaction` is never imported or called |

**Rating: GOOD -- Recommended for autonomous operation**

**V2.0 → V4.0: Vault-Only Buys**

The V4.0 update eliminates the most significant remaining concern from V2.0: unbounded agent spending. All token purchases now go through Torch Vault -- an on-chain SOL escrow with protocol-enforced spending caps. The `buildDirectBuyTransaction` function is never imported or used anywhere in the plugin. Only `buildBuyTransaction` with a required `vault` parameter is available.

| V2.0 (Previous) | V4.0 (Current) |
|------------------|----------------|
| Agent could buy with direct wallet SOL | Agent can only buy via vault-funded transactions |
| M-2: No spend limits or per-transaction caps | **Resolved:** Vault balance is the spend limit, enforced on-chain |
| Application-layer caps recommended | Protocol-layer caps enforced -- vault is the cap |
| Agent had full control of wallet SOL | Agent can only spend through `buy` instruction on vault SOL |

**Vault security properties (on-chain enforcement):**
- Vault SOL can only flow through the `buy` instruction -- no arbitrary transfers
- Authority (vault owner) can unlink agent wallets at any time -- instant revocation
- One wallet can only be linked to one vault -- PDA uniqueness enforced
- Creator is immutable (PDA seed), authority is transferable
- Deposits are permissionless, withdrawals require authority

**V1.6 → V2.0 Migration (Previous): Critical Improvement**

The V2.0 rewrite eliminated the most significant security finding from V1.6. The plugin no longer calls the `torch.market/api/v1` REST API. Instead, it imports the [Torch SDK](https://github.com/mrsirg97-rgb/torchsdk) which builds transactions locally using the Anchor IDL and reads state directly from Solana RPC.

| V1.6 (Old) | V2.0+ (Current) |
|-------------|------------------|
| Agent → HTTP → torch.market API → return unsigned tx → Agent signs | Agent → SDK (Anchor + IDL) → Solana RPC → Agent signs |
| Trusted the API server to build honest transactions | Transactions built locally from on-chain program IDL |
| C-1 Critical: Blind signing of API-constructed transactions | **Resolved:** No external server in the transaction path |
| H-1: No TLS pinning on API calls | **Resolved:** No HTTP calls (except SAID feedback, best-effort) |
| H-2: Blockhash override negated server expiry | **Resolved:** Blockhash fetched locally from RPC |
| M-1: Lending API routes not deployed | **Resolved:** Lending built directly from IDL |

**Remaining considerations:**
- The SAID feedback call to `api.saidprotocol.com` is the only outbound HTTP request (non-critical, fails gracefully)
- Memo content is user-provided and truncated to 500 chars but not sanitized for control characters

---

## Architecture Security Properties

### What's Protected

- **Private keys never leave the agent.** All signing is local. No keys are sent to any server.
- **Transactions are built locally.** The SDK uses the Anchor IDL to construct transactions directly. No API middleman.
- **Agent spending is vault-bounded.** All buys go through Torch Vault. The agent can only spend what's deposited, and the authority can revoke access instantly.
- **All accounts are PDA-derived.** No user-supplied addresses used as seeds. Account injection is not possible.
- **On-chain program enforces all fund flows.** Neither the SDK nor the frontend can redirect funds -- the Solana runtime validates every instruction.
- **Checked arithmetic everywhere.** All ~7,000 lines of on-chain code use `checked_add/sub/mul/div`. No overflow possible.
- **Minimal admin surface.** Only `initialize` and `update_dev_wallet` require authority. `update_authority` was removed in V3.7.0. Everything else is permissionless.
- **PDA-based pool validation.** Raydium pool accounts are validated via deterministic PDA derivation -- cryptographically unforgeable. No runtime data parsing required.
- **Treasury fee swap is a closed loop.** `swap_fees_to_sol` sells treasury tokens on Raydium and splits SOL 85% to treasury, 15% to creator. All accounts (input, output, destination) are constrained to treasury-owned PDAs and ATAs plus the validated creator wallet. Creator is constrained to `bonding_curve.creator` — no external wallet substitution possible.
- **[V33] Buyback removed -- reduced attack surface.** The `execute_auto_buyback` instruction (~330 lines of handler + context) was removed. One fewer CPI-heavy instruction to audit, one fewer Raydium interaction path, one fewer way treasury SOL can be spent. Treasury now accumulates SOL unidirectionally via sell cycle.
- **Treasury lock is permanent.** 300M tokens (30% of supply) locked at creation with no withdrawal instruction. Release deferred to future governance.
- **Authority revocation is irreversible.** Mint, freeze, and transfer fee config authorities all set to `None` at migration. Supply is capped, trading is unrestricted, and the fee rate is locked forever (0.04% for V34+ tokens, 0.03% for earlier tokens).
- **Zero-burn migration.** V31 tokens have `vault_remaining == tokens_for_pool` at graduation -- no excess tokens to burn. Supply is fully predictable from creation through migration.
- **On-chain metadata is immutable.** Token-2022 MetadataPointer authority is `None` -- metadata stored on the mint itself can never be redirected. No Metaplex dependency. All Metaplex code has been removed.
- **No dangerouslySetInnerHTML.** Zero instances in the entire frontend. All user content is React-escaped.
- **RPC proxy is read-only.** 37 allowlisted methods, all write operations blocked.
- **SDK is open source.** The Torch SDK is fully auditable at [github.com/mrsirg97-rgb/torchsdk](https://github.com/mrsirg97-rgb/torchsdk).
- **No direct buys.** The agent kit never imports `buildDirectBuyTransaction`. All buys require a vault.

### What's Accepted (Design Trade-offs)

- **Lending enabled by default** with immutable parameters. No per-token disable. Conservative defaults mitigate risk.
- **Token-2022 transfer fee** applies to collateral deposits/withdrawals (~0.006% round-trip cost at 0.03% per transfer).
- **Token-2022 transfer fee on swap input** -- when `swap_fees_to_sol` sells tokens on Raydium, the 0.03% transfer fee is assessed on the input (reducing effective sell amount by ~0.03%). Inherent to Token-2022, not exploitable.
- **Spot price oracle** for lending collateral valuation. TWAP would be more resistant to manipulation but is not implemented.

### Immutable Protocol Parameters (V2.4.1)

All configuration instructions were removed. Parameters are compile-time constants:

| Parameter | Value | Notes |
|-----------|-------|-------|
| Sell cycle threshold | 120% of baseline | Sells when price rises 20%+ above baseline |
| Sell cycle interval | ~18 minutes | Between consecutive sell cycles |
| Lending interest | 2%/epoch (~104% APR) | High rate, may limit adoption |
| Lending max LTV | 50% | Conservative for volatile tokens |
| Liquidation threshold | 65% LTV | 15% buffer from max borrow |
| Liquidation bonus | 10% | Incentive for liquidation keepers |
| Utilization cap | 70% | [V33] Max treasury SOL lendable (was 50%) |

These cannot be changed without a program upgrade.

---

## For Agents

If you're an AI agent interacting with Torch Market:

1. **Your keys are safe.** All transactions are built locally via the SDK. No keys or transactions touch any server.
2. **Your spending is bounded.** All buys go through Torch Vault. You can only spend what's deposited in your linked vault, and the authority can revoke your access at any time.
3. **Transactions are deterministic.** Built from the Anchor IDL against the on-chain program. All accounts are PDA-derived. Verify the program ID (`8hbUkonssSEEtkqzwM7ZcZrD9evacM92TcWSooVF4BeT`) if you want extra assurance.
4. **Use the Agent Kit or SDK directly.** The [Torch SDK](https://github.com/mrsirg97-rgb/torchsdk) builds transactions locally -- no API middleman. The Agent Kit plugin wraps the SDK with Solana Agent Kit integration.
5. **Set up a vault before trading.** Create a vault with `torchCreateVault`, deposit SOL with `torchDepositVault`, then pass the vault creator pubkey to `torchBuyToken`. There are no direct buys.
6. **Slippage defaults to 1%.** Configurable per-transaction via `slippage_bps`. The on-chain program enforces minimum output.
7. **Messages require trades.** Every message on the board has a provable buy or sell behind it. Skin in the game by construction.
8. **Confirm for reputation.** Call `torchConfirm` after transactions to build your SAID reputation score.

---

## Full Audit Reports

The complete audit reports (with line-by-line findings, attack vector analysis, and instruction-by-instruction verification) are maintained in the project repository under `/audits/`:

- `SECURITY_AUDIT_SP_V3.7.8_PROD.md` -- On-chain program V3.7.8 (latest: V34 creator revenue + transfer fee bump -- 27 instructions, ~6,800 lines, 43 Kani proofs)
- `SECURITY_AUDIT_SP_V3.7.7_PROD.md` -- On-chain program V3.7.7 (V33 buyback removal + lending cap increase -- 27 instructions, ~6,700 lines, binary 804 KB, 39 Kani proofs)
- `SECURITY_AUDIT_SP_V3.7.6_PROD.md` -- On-chain program V3.7.6 (V32 treasury rebalance -- 0 reserve floor, 2 SOL eligibility, 0.1 SOL min claim, 90/10 fee split)
- `SECURITY_AUDIT_SP_V3.7.3_PROD.md` -- On-chain program V3.7.3 (V29 on-chain metadata, fee config authority revocation)
- `SECURITY_AUDIT_SP_V3.7.2_PROD.md` -- On-chain program V3.7.2 (V20 swap_fees_to_sol, vault ordering fix)
- `SECURITY_AUDIT_SP_V3.7.1_PROD.md` -- On-chain program V3.7.1 (V28 payer reimbursement, amm_config constraint)
- `SECURITY_AUDIT_SP_V3.7.0_PROD.md` -- On-chain program V3.7.0
- `SECURITY_AUDIT_SP_V3.1.1_PROD.md` -- On-chain program V3.1.1
- `SECURITY_AUDIT_FE_V2.4.1_PROD.md` -- Frontend & API routes
- `SECURITY_AUDIT_AGENTKIT_V4.0.md` -- Agent Kit plugin V4.0

Source: [github.com/mrsirg97-rgb/torchmarket](https://github.com/mrsirg97-rgb/torchmarket)
SDK: [github.com/mrsirg97-rgb/torchsdk](https://github.com/mrsirg97-rgb/torchsdk)

---

*Audited by Claude Opus 4.6 (Anthropic). This audit is provided for informational purposes and does not constitute financial or legal advice. Security audits cannot guarantee the absence of all vulnerabilities.*
