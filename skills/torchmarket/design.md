# Torch SDK — Design Document

> TypeScript SDK for the Torch Market protocol on Solana. Version 3.7.23.

## Overview

The Torch SDK is a stateless, RPC-first TypeScript library for interacting with the Torch Market protocol. It reads on-chain state directly from Solana, builds unsigned transactions locally, and returns them for the caller to sign and submit. There is no API server, no websocket dependency, and no custody of keys.

The SDK is designed for AI agent integration. The core safety primitive is the **Torch Vault** — a full-custody on-chain escrow that holds all SOL and tokens. The vault is integrated into all operations (buy, sell, star, borrow, repay, DEX swap) so that agents trade with vault funds and all value stays in the vault. The agent wallet is a disposable controller that holds nothing of value.

## Architecture

```
┌──────────────────────────────────────────────────────────┐
│                     CONSUMER (Agent / App)                │
│                                                          │
│  1. Call SDK function (e.g. buildBuyTransaction)         │
│  2. Receive unsigned Transaction                         │
│  3. Sign locally with wallet/keypair                     │
│  4. Submit to Solana RPC                                 │
└──────────────┬───────────────────────────┬───────────────┘
               │ read                      │ build
               ▼                           ▼
┌──────────────────────────┐  ┌────────────────────────────┐
│      Token Queries       │  │   Transaction Builders     │
│                          │  │                            │
│  getTokens()             │  │  buildBuyTransaction()     │
│  getToken()              │  │  buildSellTransaction()    │
│  getTokenMetadata()      │  │  buildVaultSwapTx()        │
│  getHolders()            │  │  buildCreateTokenTx()      │
│  getMessages()           │  │  buildStarTransaction()    │
│  getLendingInfo()        │  │  buildMigrateTransaction() │
│  getLoanPosition()       │  │  buildBorrowTransaction()  │
│  getAllLoanPositions()   │  │  buildRepayTransaction()   │
│  getVault()              │  │  buildLiquidateTransaction │
│  getVaultForWallet()     │  │  buildClaimProtocolRewardsTx│
│  getVaultWalletLink()    │  │  buildHarvestFeesTx()      │
│                          │  │  buildSwapFeesToSolTx()    │
│                          │  │  buildCreateVaultTx()      │
│                          │  │  buildDepositVaultTx()     │
│                          │  │  buildWithdrawVaultTx()    │
│                          │  │  buildWithdrawTokensTx()   │
│                          │  │  buildLinkWalletTx()       │
│                          │  │  buildUnlinkWalletTx()     │
│                          │  │  buildTransferAuthorityTx()│
└──────────┬───────────────┘  └──────────┬─────────────────┘
           │                             │
           ▼                             ▼
┌──────────────────────────────────────────────────────────┐
│                    Program Layer                          │
│                                                          │
│  PDA derivation    IDL decoding    Quote math            │
│  Account types     Anchor Program  Raydium PDAs          │
└──────────────────────────┬───────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────┐
│         Solana RPC (mainnet / devnet / validator)         │
│                                                          │
│  getProgramAccounts    getAccountInfo    sendTransaction  │
└──────────────────────────────────────────────────────────┘
```

## Module Structure

```
src/
├── index.ts            Public API — all exports
├── types.ts            TypeScript interfaces (params, results, types)
├── constants.ts        Program ID, PDA seeds, token constants, blacklist, dynamic network
├── program.ts          Anchor IDL, PDA derivation, on-chain types, math
├── tokens.ts           Read-only queries (tokens, metadata, holders, vault, lending, loan positions, pool price)
├── transactions.ts     Transaction builders (buy, sell, vault, lending, migrate, harvest, swap fees)
├── quotes.ts           Buy/sell quote calculations (no RPC write)
├── said.ts             SAID Protocol integration (verify, confirm)
├── gateway.ts          Irys metadata fetch with fallback
├── ephemeral.ts        Ephemeral agent (disposable wallet helper)
└── torch_market.json   Anchor IDL (v3.7.8, 27 instructions)
```

### Dependency Graph

```
index.ts ──→ tokens.ts ──→ program.ts ──→ constants.ts
         ──→ transactions.ts ──→ program.ts
                             ──→ tokens.ts (fetchTokenRaw)
         ──→ quotes.ts ──→ program.ts
                       ──→ tokens.ts (fetchTokenRaw)
         ──→ said.ts ──→ constants.ts
         ──→ types.ts (type-only)
```

No circular dependencies. `program.ts` is the foundation — it owns PDA derivation, Anchor types, and math. `tokens.ts` owns all read-only RPC queries. `transactions.ts` owns all write operations.

---

## Design Principles

### 1. Stateless

Every function takes a `Connection` as the first argument. No global state, no singletons, no connection pools. The caller owns the connection lifecycle.

### 2. Unsigned Transactions

All `build*Transaction` functions return `{ transaction: Transaction, message: string }`. The SDK never signs. The caller signs with their keypair and submits. This keeps key material out of the SDK entirely.

### 3. RPC-First

All data comes from Solana RPC. Token listings use `getProgramAccounts` with discriminator filters. Token details use `getAccountInfo`. No indexer, no API server, no database.

### 4. Vault-Aware

The buy transaction builder accepts an optional `vault` parameter. When provided, the transaction includes the TorchVault and VaultWalletLink accounts so the on-chain program debits the vault instead of the buyer's wallet. When omitted, the buy works exactly as before (backward compatible).

### 5. Agent-Safe by Default

The SDK is designed so that an agent wallet:
- Holds minimal SOL (~0.01) for transaction fees
- Spends from a vault with a finite balance (spending cap)
- Cannot withdraw from the vault (only the authority can)
- Cannot transfer vault SOL arbitrarily (vault SOL can only flow through `buy`)
- Receives tokens in its own wallet (can sell freely)

### 6. Reward Harvesting

Active agents earn protocol rewards. The protocol treasury accumulates 1% fees from all bonding curve buys across the platform. Each epoch (~weekly), the treasury distributes rewards proportionally to wallets that traded >= 2 SOL volume in the previous epoch. Agents call `buildClaimProtocolRewardsTransaction` to claim — rewards go directly to the vault. This creates a positive feedback loop: agents that trade actively earn back a share of platform fees, reducing their effective cost of operation.

---

## Torch Vault — Safety Model

The Torch Vault is the core safety primitive for AI agent interaction with the protocol. It solves the problem of giving an agent a wallet with SOL — without the vault, the agent could drain the wallet through any transaction, not just token buys.

### How It Works

```
┌─────────────────────────────────────────────────────┐
│                  VAULT LIFECYCLE                      │
│                                                      │
│  User (hardware wallet)                              │
│    │                                                 │
│    ├── createVault()     → TorchVault PDA created    │
│    ├── depositVault()    → SOL into vault escrow     │
│    ├── linkWallet(agent) → agent can use vault       │
│    │                                                 │
│  Agent (disposable controller, ~0.01 SOL for gas)    │
│    │                                                 │
│    ├── buy(vault=creator) → vault SOL pays, tokens   │
│    │                        to vault ATA              │
│    ├── sell(vault=creator)→ vault tokens sold, SOL    │
│    │                        returns to vault          │
│    ├── vaultSwap(buy)    → vault SOL → Raydium →     │
│    │                        tokens to vault ATA       │
│    ├── vaultSwap(sell)   → vault tokens → Raydium →  │
│    │                        SOL to vault              │
│    ├── borrow(vault)     → vault tokens locked, SOL  │
│    │                        to vault                  │
│    ├── repay(vault)      → vault SOL repays, tokens  │
│    │                        returned to vault         │
│    │                                                  │
│  User                                                │
│    ├── withdrawVault()   → pull SOL (authority only)  │
│    ├── withdrawTokens()  → pull tokens (auth only)    │
│    └── unlinkWallet()    → revoke agent access        │
└─────────────────────────────────────────────────────┘
```

### Multi-Wallet Identity

A single vault can be used by multiple wallets through VaultWalletLink PDAs:

```
Hardware Wallet ──┐
                  │
Hot Wallet ───────┼──→ VaultWalletLink ──→ TorchVault (shared SOL pool)
                  │
Agent Wallet ─────┘
```

Each wallet has a reverse-pointer PDA: `["vault_wallet", wallet.key()]`. Given any wallet, derive its link PDA to find which vault it belongs to. No enumeration needed.

### Permission Model

| Action | Who | Enforced By |
|--------|-----|-------------|
| Create vault | Anyone | PDA uniqueness (one per creator) |
| Deposit SOL | Anyone | No auth check (permissionless) |
| Withdraw SOL | Authority only | `has_one = authority` |
| Link wallet | Authority only | `has_one = authority` |
| Unlink wallet | Authority only | `has_one = authority` |
| Transfer authority | Authority only | `has_one = authority` |
| Buy with vault | Any linked wallet | `vault_wallet_link.vault == torch_vault.key()` |
| Sell with vault | Any linked wallet | `vault_wallet_link.vault == torch_vault.key()` |
| Vault swap (DEX) | Any linked wallet | `vault_wallet_link.vault == torch_vault.key()` |
| Borrow with vault | Any linked wallet | `vault_wallet_link.vault == torch_vault.key()` |
| Repay with vault | Any linked wallet | `vault_wallet_link.vault == torch_vault.key()` |
| Star with vault | Any linked wallet | `vault_wallet_link.vault == torch_vault.key()` |
| Buy without vault | Anyone | Unchanged (direct buy) |

### What the Vault Controls

- **Buy**: vault SOL pays, tokens to vault ATA
- **Sell**: vault tokens sold, SOL returns to vault
- **DEX Swap**: vault SOL/tokens swap on Raydium, all value stays in vault
- **Borrow**: vault tokens locked as collateral, SOL to vault
- **Repay**: vault SOL repays, collateral returned to vault ATA
- **Star**: vault SOL pays 0.02 SOL fee

The vault is a **full-custody escrow**. All SOL and tokens stay in the vault. The controller wallet holds nothing of value.

---

## Token Lifecycle

The SDK covers the full token lifecycle on the Torch Market protocol:

```
CREATE → BONDING → COMPLETE → MIGRATE → DEX TRADING
   │         │                    │           │
   │    buy/sell on curve    vote finalizes   borrow/repay
   │    (vault-funded buys)                  (treasury lending)
   │
   └── star token (appreciation signal, 0.02 SOL)
```

### Bonding Phase (0–target SOL, per tier: 50/100/200)

- `buildBuyTransaction` — buy tokens on the bonding curve
- `buildSellTransaction` — sell tokens back to the curve
- `getBuyQuote` / `getSellQuote` — simulate trades
- Fee split: 1% protocol fee (90% treasury / 10% dev), remainder to curve+treasury (20%→5% flat dynamic rate). Creator receives 0.2%→1% carved from treasury rate.

### Migration (V26 — Permissionless)

- `buildMigrateTransaction` — two-step: fund WSOL from treasury + create Raydium CPMM pool. Anyone can trigger for bonding-complete tokens. Payer fronts ~1 SOL for Raydium costs (pool creation fee + account rent), treasury reimburses the exact amount in the same transaction. Net cost to payer: 0 SOL.

### Post-Migration

- `buildVaultSwapTransaction` — buy/sell migrated tokens on Raydium DEX via vault (full custody)
- `buildBorrowTransaction` — lock tokens as collateral, borrow SOL from treasury
- `buildRepayTransaction` — repay SOL debt, recover collateral
- `buildLiquidateTransaction` — liquidate underwater positions (permissionless)

### Treasury Cranks (Permissionless)

- `buildHarvestFeesTransaction` — harvest accumulated Token-2022 transfer fees from token accounts into the treasury. Auto-discovers source accounts with withheld fees via `getTokenLargestAccounts` + `unpackAccount` + `getTransferFeeAmount`. Falls back gracefully if RPC doesn't support discovery. Optional `sources` param for explicit accounts.
- `buildSwapFeesToSolTransaction` — swap harvested transfer fee tokens to SOL via Raydium CPMM. Bundles `create_idempotent(treasury_wsol)` + `harvest_fees` + `swap_fees_to_sol` in one atomic transaction. SOL proceeds split 85% treasury / 15% creator. Set `harvest=false` to skip harvest if already done separately.

### Community Features

- `buildStarTransaction` — star a token (0.02 SOL, sybil-resistant)
- `getMessages` — read trade-bundled memos (SPL Memo program)
- Vote on first buy (`vote` param in `buildBuyTransaction`)

---

## Quote Engine

The SDK includes a local quote engine that mirrors the on-chain math exactly:

### Buy Quote

```
1. Protocol fee: 1% of input SOL (90% treasury / 10% dev wallet)
2. Dynamic treasury split: 20%→5% flat across all tiers (decays as bonding progresses)
3. Creator share: 0.2%→1% carved from treasury split (grows linearly with reserves)
4. Remaining SOL → constant product formula → tokens out
5. Token split: 90% to buyer, 10% to community treasury
```

### Sell Quote

```
1. Constant product formula → SOL out
2. No sell fee (0%)
3. Full SOL amount to seller
```

### Constant Product Formula

```
tokens_out = (virtual_token_reserves × sol_in) / (virtual_sol_reserves + sol_in)
sol_out    = (virtual_sol_reserves × token_in) / (virtual_token_reserves + token_in)
price      = virtual_sol_reserves / virtual_token_reserves
```

---

## SAID Protocol Integration

The SDK integrates with the SAID (Solana Agent Identity) Protocol for wallet reputation:

- `verifySaid(wallet)` — check verification status and trust tier
- `confirmTransaction(connection, signature, wallet)` — confirm a transaction on-chain and determine its event type for reputation tracking

Event types: `token_launch`, `trade_complete`, `governance_vote`, `unknown`

SAID verification data enriches token detail responses (`creator_verified`, `creator_trust_tier`, `creator_said_name`, `creator_badge_url`) and message responses (`sender_verified`, `sender_trust_tier`).

---

## On-Chain Data Access

### Account Discovery

Tokens are discovered via `getProgramAccounts` with a BondingCurve discriminator filter (`4y6pru6YvC7` base58). This returns all bonding curve accounts. The SDK decodes them with Anchor's BorshCoder, filters out blacklisted/reclaimed tokens, and applies sorting/pagination locally.

### PDA Derivation

All PDAs are deterministic. The SDK derives them locally without RPC calls:

| Account | Seeds |
|---------|-------|
| GlobalConfig | `["global_config"]` |
| BondingCurve | `["bonding_curve", mint]` |
| Treasury | `["treasury", mint]` |
| UserPosition | `["user_position", bonding_curve, user]` |
| UserStats | `["user_stats", user]` |
| ProtocolTreasury | `["protocol_treasury_v11"]` |
| StarRecord | `["star_record", user, mint]` |
| LoanPosition | `["loan", mint, user]` |
| CollateralVault | `["collateral_vault", mint]` |
| TorchVault | `["torch_vault", creator]` |
| VaultWalletLink | `["vault_wallet", wallet]` |

### Raydium CPMM PDAs

For post-migration operations (borrow, liquidate), the SDK derives Raydium pool accounts:

| Account | Seeds (under Raydium CPMM program) |
|---------|-------------------------------------|
| Authority | `["vault_and_lp_mint_auth_seed"]` |
| PoolState | `["pool", amm_config, token0, token1]` |
| LP Mint | `["pool_lp_mint", pool_state]` |
| Vault | `["pool_vault", pool_state, token_mint]` |
| Observation | `["observation", pool_state]` |

Token ordering follows Raydium convention: `token0 < token1` by pubkey bytes.

---

## Token Metadata

Token metadata (name, symbol, URI) is stored on-chain in the BondingCurve account as fixed-size byte arrays. The SDK decodes these with `Buffer.from(bytes).toString('utf8').replace(/\0/g, '')`.

For detailed token views (`getToken`), the SDK fetches the metadata URI to get description, image, and social links. The Irys gateway URL is automatically converted to the uploader URL as a fallback for SSL issues.

---

## Error Handling

The SDK throws standard JavaScript errors with descriptive messages:

- `Token not found: {mint}` — no bonding curve account for this mint
- `Bonding curve complete, trade on DEX` — buy/sell after migration
- `Cannot star your own token` — self-star prevention
- `Already starred this token` — duplicate star prevention
- `Token not yet migrated, lending not available` — borrow before migration

Transaction builders validate inputs locally before constructing the transaction. On-chain errors are returned by the RPC on submission and are not caught by the SDK.

---

## Constants

| Constant | Value | Description |
|----------|-------|-------------|
| `PROGRAM_ID` | `8hbUkonssSEEtkqzwM7ZcZrD9evacM92TcWSooVF4BeT` | Torch Market program |
| `TOTAL_SUPPLY` | 1,000,000,000 (1B × 10^6) | Token supply with 6 decimals |
| `TOKEN_DECIMALS` | 6 | SPL token decimals |
| `getRaydiumCpmmProgram()` | Mainnet: `CPMMoo8L3F4...` / Devnet: `CPMDWBwJ...` | Raydium CPMM (dynamic) |
| `getRaydiumAmmConfig()` | Mainnet: `D4FPEru...` / Devnet: `9zSzfk...` | Fee tier (dynamic) |
| `TOKEN_2022_PROGRAM_ID` | `TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb` | Token Extensions |
| `MEMO_PROGRAM_ID` | `MemoSq4gqABAXKb96qnH8TysNcWxMyWCqXgDLGmfcHr` | SPL Memo |

---

## E2E Test Coverage

The SDK includes a comprehensive end-to-end test that runs against a Surfpool mainnet fork:

| Test | What It Validates |
|------|-------------------|
| Create Token | Token-2022 mint + bonding curve + treasury initialized |
| Create Vault | TorchVault PDA + auto-linked creator wallet |
| Deposit Vault | SOL transferred into vault escrow |
| Query Vault | `getVault`, `getVaultForWallet`, `getVaultWalletLink` |
| Get Token | On-chain metadata decoding, status, progress |
| List Tokens | Discriminator filtering, sort, pagination |
| Buy (direct) | Standard buy without vault (backward compat) |
| Buy (via vault) | Vault-funded buy, vault balance decreases |
| Link + Vault Buy | Agent wallet linked, buys via vault, then unlinked |
| Withdraw Vault | Authority withdraws remaining SOL |
| Sell | Sell tokens back to curve |
| Star | Sybil-resistant appreciation signal |
| Messages | Trade-bundled SPL Memo retrieval |
| Confirm | SAID Protocol transaction confirmation |
| Full Lifecycle | Bond to graduation (50/100/200 SOL tier) → migrate to Raydium → borrow → repay |
| Vault Swap Buy | Vault-routed Raydium buy (SOL → tokens via DEX) |
| Vault Swap Sell | Vault-routed Raydium sell (tokens → SOL via DEX) |
| Withdraw Tokens | Authority withdraws tokens from vault ATA |
| Harvest Fees | Auto-discovery of token accounts with withheld fees, treasury balance increase |
| Protocol Rewards | Vault-routed epoch reward claim (fee-funded, 2 SOL min volume) |

Expected result: **29 passed, 0 failed** (mainnet fork). Tiers test covers harvest + lending across Spark/Flame/Torch.

---

## Version History

| Version | Changes |
|---------|---------|
| 1.0.0 | Initial SDK: tokens, quotes, buy/sell/create/star, SAID, messages |
| 1.0.1–1.0.5 | Bug fixes, lending support, discriminator filtering |
| 2.0.0 | **Torch Vault integration.** 6 new vault builders, 3 vault queries, vault-funded buy. IDL updated to v3.0.0. Breaking change: BuyParams accepts optional `vault` field. |
| 2.1.0 | **Full custody + DEX trading.** All operations vault-routed (sell, star, borrow, repay). New `buildVaultSwapTransaction` for Raydium DEX trading via vault. New `buildWithdrawTokensTransaction`. IDL updated to v3.1.1 (28 instructions). 25 tests. |
| 3.2.0 | **Platform treasury merge.** Removed `buildClaimEpochRewardsTransaction` (platform treasury eliminated). Protocol treasury is now the single reward system — funded by trading fees and reclaims. New `buildClaimProtocolRewardsTransaction` for vault-routed epoch reward claims. IDL updated to v3.2.0 (25 instructions). Reclaim SOL now routes to protocol treasury. Buy/Sell no longer accept platform_treasury account. 32 tests. |
| 3.2.3 | **Documentation only.** Updated whitepaper, SKILL.md (ClawHub spec compliance), audit.md, design.md, readme. No code changes. |
| 3.2.4 | **Audit remediation.** Metadata fetch timeout (10s AbortController in `fetchWithFallback`). Explicit slippage validation (throws on out-of-range instead of silent clamping). IDL-derived LoanPosition discriminator (replaces hardcoded bytes). All 3 low-severity audit findings resolved. |
| 3.3.0 | **Tiered Bonding Curves (V23).** New optional `sol_target` parameter on `buildCreateTokenTransaction`: Spark (50 SOL, ~7x), Flame (100 SOL, ~19x), Torch (200 SOL, ~59x, default). Same formula, different graduation points. On-chain: `harvest_fees` hardened (V3.2.1 security fix — constrained treasury ATA destination). Raydium pool validation confirmed by independent auditor. Kani proofs updated for all tiers (20/20 passing). IDL updated to v3.3.0. |
| 3.4.0 | **Tiered Fee Structure (V24).** Dynamic treasury SOL rate is now per-tier: Spark 5%→1%, Flame 10%→2%, Torch 20%→5% (unchanged). Fee bounds derived from `bonding_target` at runtime — zero new on-chain state. `calculateTokensOut` accepts optional `bondingTarget` parameter. Callers (`getBuyQuote`, `buildBuyTransaction`) pass `bonding_target` from on-chain state. Legacy tokens (bonding_target=0) get Torch rates. IDL updated to v3.4.0. |
| 3.5.1 | **V25 Pump-Style Token Distribution.** New virtual reserve model: IVS = bonding_target/8 (6.25-25 SOL), IVT = 900M tokens, ~81x multiplier across all tiers. Reverted V24 per-tier treasury fees to flat 20%→5% for all tiers. 35 Kani proof harnesses (up from 26), including 7 new V25 supply conservation and excess burn proofs. IDL updated to v3.5.1. |
| 3.6.8 | **V26-V28 + Dynamic Network.** Permissionless DEX migration (`buildMigrateTransaction`) — two-step fund WSOL + migrate in one tx. Pool account validation hardened (V27 — AMM config constrained, pool ownership verified). `update_authority` admin instruction (V28). Critical lending `sol_balance` accounting fix. Lending utilization cap properly applied (50% - total_sol_lent). Live Raydium pool price for migrated tokens. Dynamic network detection (`globalThis.__TORCH_NETWORK__` / `process.env.TORCH_NETWORK`). Pre-migration buyback removed. IDL updated to v3.6.0. |
| 3.7.0 | **V28 update_authority Removed + V27 Treasury Lock.** Removed `update_authority` instruction — authority transfer now done at deployment via multisig tooling. 27 instructions total (down from 28). Minimal admin surface: only `initialize` and `update_dev_wallet` require authority. V27 Treasury Lock: 250M tokens (25%) locked in TreasuryLock PDA at creation; 750M (75%) for bonding curve. IVS = 3BT/8, IVT = 756.25M tokens — 13.44x multiplier. PDA-based Raydium pool validation replaces runtime validation. Pre-migration buyback handler removed. 36 Kani proof harnesses. IDL updated to v3.7.0. |
| 3.7.1 | **Treasury Cranks.** New `buildAutoBuybackTransaction` (removed in V33) — permissionless treasury buyback on Raydium. New `buildHarvestFeesTransaction` — permissionless Token-2022 transfer fee harvesting into treasury. New types: `HarvestFeesParams`. |
| 3.7.2 | **Buyback Pre-Checks + Harvest Auto-Discovery.** Buyback pre-checks (removed in V33). `buildHarvestFeesTransaction` auto-discovers source accounts with withheld fees via `getTokenLargestAccounts` + `unpackAccount` + `getTransferFeeAmount`. New optional `sources` field for explicit accounts. Dynamic compute budget (200k + 20k per source). Graceful RPC fallback when `getTokenLargestAccounts` is unsupported (e.g. Surfpool). E2E tests for harvest across all three test suites. |
| 3.7.3 | **`fetchWithFallback` resilience.** Improved metadata fetch with gateway URL fallback. |
| 3.7.6 | **V28 Migration Payer Reimbursement.** `buildBuyTransactionInternal` auto-migrate path collapsed into a single `buildMigrateTransaction()` call — program now handles treasury reimbursement internally (payer fronts ~1 SOL, treasury reimburses exact cost, net 0). Removed ~50 lines of inline migration builder. IDL updated to v3.7.1 (program v3.7.1: `MIN_MIGRATION_SOL` replaces `RAYDIUM_POOL_CREATION_FEE`, payer lamport snapshot + reimbursement in migration handler). 36 Kani proofs all passing on v3.7.1. |
| 3.7.10 | **V20 Swap Fees to SOL.** New `buildSwapFeesToSolTransaction` — bundles `create_idempotent(treasury_wsol)` + `harvest_fees` + `swap_fees_to_sol` in one atomic tx. Sells harvested Token-2022 transfer fee tokens back to SOL via Raydium CPMM. Treasury PDA signs the swap, WSOL unwrapped to SOL, proceeds added to `treasury.sol_balance` and tracked in `treasury.harvested_fees`. New type: `SwapFeesToSolParams`. Fixed `validate_pool_accounts` vault ordering bug in `swap_fees_to_sol` — vaults now passed in pool order (by mint pubkey) instead of swap direction. IDL updated to v3.7.10. |
| 3.7.17 | **V29 On-Chain Metadata + Loan Position Scanner.** Metaplex `buildAddMetadataTransaction` removed (temporary backfill complete — all active tokens now use Token-2022 metadata extensions). New `getTokenMetadata(connection, mint)` read-only function returns `{ name, symbol, uri, mint }` from on-chain Token-2022 metadata. Transfer fee updated from 1% to 0.1% on-chain (`TRANSFER_FEE_BPS` 100→10). New `getAllLoanPositions(connection, mint)` scans all `LoanPosition` accounts for a token via `getProgramAccounts` with discriminator + mint memcmp filters, computes health status (healthy/at_risk/liquidatable) using Raydium pool price, returns sorted by liquidation risk. New types: `TokenMetadataResult`, `LoanPositionWithKey`, `AllLoanPositionsResult`. IDL updated to v3.7.17. |
| 3.7.22 | **V33 Buyback Removed, Lending Extended.** Removed `buildAutoBuybackTransaction` and `AutoBuybackParams`. `execute_auto_buyback` instruction removed from on-chain program (27 instructions). Lending utilization cap 50%→70%. Treasury simplified to: fee harvest → sell → SOL → lending yield + epoch rewards. IDL updated to v3.7.7. |
| 3.7.23 | **V34 Creator Revenue.** Three creator income streams: (1) bonding SOL share 0.2%→1% carved from treasury rate, growing linearly with reserves; (2) post-migration fee split 85% treasury / 15% creator on `swap_fees_to_sol`; (3) star payout ~40 SOL at 2,000 stars. `creator` account added to `buy` and `swap_fees_to_sol` instructions, validated against `bonding_curve.creator`. `calculateTokensOut` returns `solToCreator` and `creatorRateBps`. Star cost 0.05→0.02 SOL. Transfer fee 3→4 bps (0.04%). Protocol fee split 75/25→90/10 (treasury/dev). Volume eligibility 10→2 SOL. 43 Kani proofs (4 new: creator share bounds, conservation, fee split). IDL updated to v3.7.8. |
| 3.7.25 | **V34 Optional Account on Sell.** no functional changes |