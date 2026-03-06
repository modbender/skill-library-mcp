# Tokens and Pools

> **RULE: Always search, never guess.** Before using any token in a command: for **native gas tokens** (ETH, HYPE) use `wayfinder://tokens/gas/<chain_code>`; for **ERC20 tokens** use `wayfinder://tokens/search/<chain_code>/<symbol>` and take the exact token ID from the result. Never fabricate token IDs — coingecko IDs are unpredictable. Never call `tokens/resolve` with a guessed ID.

## Token ID Format

Wayfinder uses `<coingecko_id>-<chain_code>` as the canonical token identifier format:

| Token | Chain | ID |
|-------|-------|----|
| USDC | Base | `usd-coin-base` |
| ETH | Arbitrum | `ethereum-arbitrum` |
| USDT | Arbitrum | `usdt0-arbitrum` |
| HYPE | HyperEVM | `hyperliquid-hyperevm` |
| WETH | Base | `weth-base` |
| wstETH | Base | `wrapped-steth-base` |

**Do NOT use symbol-chain** (e.g., `usdc-base` will fail). Use the coingecko ID.

### Chain-Scoped Address Format

For specific ERC20 contracts: `<chain_code>_<address>`

Example: `base_0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913`

## Token Lookups

There are three separate token endpoints. **Always start with fuzzy search** — it hits a different API (`/blockchain/tokens/fuzzy/`) than resolve (`/blockchain/tokens/detail/`). Do NOT skip search and go straight to resolve with a guessed ID.

```bash
# Step 1: ALWAYS fuzzy search first (hits /blockchain/tokens/fuzzy/)
poetry run wayfinder resource wayfinder://tokens/search/base/usdc
poetry run wayfinder resource wayfinder://tokens/search/arbitrum/eth
poetry run wayfinder resource wayfinder://tokens/search/ethereum/eth

# Step 2: Use the exact token ID from search results with resolve (hits /blockchain/tokens/detail/)
poetry run wayfinder resource wayfinder://tokens/resolve/usd-coin-base

# For native gas tokens (ETH, HYPE, etc.) — use the gas endpoint (hits /blockchain/tokens/gas/)
poetry run wayfinder resource wayfinder://tokens/gas/base
poetry run wayfinder resource wayfinder://tokens/gas/arbitrum
poetry run wayfinder resource wayfinder://tokens/gas/ethereum
```

### Native Gas Tokens (ETH, HYPE)

Native gas tokens (like ETH on Ethereum mainnet, ETH on Base/Arbitrum, HYPE on HyperEVM) are **not regular ERC20 tokens** and may not have standard token IDs. For native tokens:

1. **Use the gas endpoint**: `resource wayfinder://tokens/gas/<chain_code>` — this returns the correct native token metadata (address, decimals, symbol)
2. **Or search first**: `resource wayfinder://tokens/search/<chain>/<symbol>` — the fuzzy search will find the right entry
3. **Do NOT guess** IDs like `ethereum-ethereum` or `ETH-mainnet` — these may not exist in the token database

**Known limitation — native gas tokens in swaps:** The swap/bridge tool (`execute` with `kind: swap`) may fail to resolve native gas tokens because the API can return `null` for the address field. The swap code expects a sentinel address (`0x0000...0000`) but doesn't normalize null → zero-address like the send code does. **Workaround:** When swapping from/to native ETH, use the wrapped ERC20 version instead (e.g., search for WETH on the target chain). For sends, native tokens work correctly via `token: "native"` with `chain_id`.

## Balance Reads

```bash
# Enriched balances (all tokens, all chains, with USD values)
poetry run wayfinder resource wayfinder://balances/main

# Recent activity / transaction history
poetry run wayfinder resource wayfinder://activity/main
```

### Balance Read Methods

| Method | Source | Purpose |
|--------|--------|---------|
| `BALANCE_CLIENT.get_enriched_wallet_balances(wallet_address, exclude_spam_tokens=True)` | Wayfinder API | Full portfolio view with USD totals + chain breakdown |
| `BALANCE_CLIENT.get_token_balance(wallet_address, token_id, human_readable=True)` | Wayfinder API | Single token balance |
| `BALANCE_CLIENT.get_pool_balance(pool_address, chain_id, user_address, human_readable=True)` | Wayfinder API | Pool/share balance |
| `BalanceAdapter.get_balance(wallet_address, token_id/token_address, chain_id)` | On-chain RPC | Raw ERC20 balance (int) |
| `BalanceAdapter.get_vault_wallet_balance(token_id)` | On-chain RPC | Strategy wallet balance (`token_id` is a Wayfinder identifier, e.g. `usd-coin-arbitrum`) |
| `BalanceAdapter.get_wallet_balances_multicall(assets, wallet_address)` | On-chain multicall | Batch balance reads (grouped by chain, returns `balance_raw`, `decimals`, optional `balance_decimal`) |

### Local Ledger Bookkeeping

The LedgerAdapter writes JSON into `.ledger/` (gitignored) for tracking swaps, deposits, and withdrawals. Treat ledger writes as best-effort — don't break strategy execution if ledger fails.

## Pool Discovery

```bash
# List all adapters (includes pool-related adapters)
poetry run wayfinder resource wayfinder://adapters

# Describe pool adapter
poetry run wayfinder resource wayfinder://adapters/pool_adapter
```

### Pool Read Methods

| Method | Purpose |
|--------|---------|
| `PoolAdapter.get_pools(chain_id=None, project=None)` | Broad discovery — returns matches with `apy`, `apyBase`, `apyReward`, `tvlUsd` |
| `PoolAdapter.get_pools_by_ids(pool_ids=[...])` | Shortlist by IDs — normalized entries |

### Pool Discovery Pattern

"Screen then validate":
1. Pull a broad list with `get_pools()`
2. Filter by chain + stablecoin-only + TVL floor
3. Only then request deeper analytics for the finalists

## Supported Chains

| Chain | Code | Chain ID |
|-------|------|----------|
| Base | `base` | 8453 |
| Arbitrum | `arbitrum` | 42161 |
| Ethereum | `ethereum` | 1 |
| HyperEVM | `hyperevm` | 999 |

## Token Metadata Notes

- **Always search for token IDs** — run `resource wayfinder://tokens/search/<chain>/<symbol>` before any operation. Never construct or guess token IDs. The coingecko ID portion is not derivable from the symbol.
- Treat API responses as schema-flexible — check key presence rather than assuming fields exist.
- Never assume decimals; always fetch and cache per token.
- Convert human units → raw units using `decimals` before building txs. Convert raw → human for reporting only.

## Token Resolution Workflow — MANDATORY

**CRITICAL: You MUST always search for tokens before using them. Never guess or construct token IDs.** Coingecko IDs are not derivable from token symbols (e.g., ETH = `ethereum`, USDC = `usd-coin`, HYPE = `hyperliquid`). Guessing will produce wrong IDs like `ETH-mainnet`, `ethereum-ethereum`, or `usdc-base` that will fail or resolve to the wrong token.

**Search and resolve use different API endpoints:**
- **Search** (`wayfinder://tokens/search/...`) → hits `/blockchain/tokens/fuzzy/` — fuzzy matching, returns candidates
- **Resolve** (`wayfinder://tokens/resolve/...`) → hits `/blockchain/tokens/detail/` — exact lookup by known ID
- **Gas** (`wayfinder://tokens/gas/...`) → hits `/blockchain/tokens/gas/` — native chain tokens

**Never call resolve with a guessed ID.** Always search first to get the correct ID, then use that ID with resolve.

When a user mentions a token, follow this workflow:

1. **Is it a native gas token (ETH, HYPE)?** → Use `resource wayfinder://tokens/gas/<chain_code>` first. This is the most reliable way to get native token metadata.
2. **Search by symbol + chain** — `resource wayfinder://tokens/search/<chain_code>/<symbol>`. This is the **required step** for any ERC20 token the user mentions, even common ones like USDC or WETH.
3. **Use the exact ID from the search result** — copy the token ID verbatim from the search response. Do not modify it or construct your own.
4. **Verify with resolve** — optionally confirm with `resource wayfinder://tokens/resolve/<token_id>` using the ID you got from search.
5. **Address** — if the user gives a contract address, use the chain-scoped format `<chain_code>_<address>`.

**Important chain codes**: `base`, `arbitrum`, `ethereum`, `hyperevm`. Note: `mainnet` is NOT a valid chain code — use `ethereum` for Ethereum mainnet.

Always confirm the resolved token before executing swaps or sends. Show the user: token name, chain, contract address (truncated), and decimals.

## Common Token Quick Reference

These are frequently used tokens. **Always verify via search before using** — do not rely on this table as a substitute for `resource wayfinder://tokens/search/<chain>/<symbol>`.

| Symbol | Chain | Canonical ID | Decimals | Notes |
|--------|-------|-------------|----------|-------|
| USDC | Base | `usd-coin-base` | 6 | Primary stablecoin |
| USDC | Arbitrum | `usd-coin-arbitrum` | 6 | |
| ETH | Base | `ethereum-base` | 18 | Use `tokens/gas/base` for native |
| ETH | Arbitrum | `ethereum-arbitrum` | 18 | Use `tokens/gas/arbitrum` for native |
| ETH | Ethereum | — | 18 | **Use `tokens/gas/ethereum`** — native gas token, no standard token ID |
| WETH | Base | `weth-base` | 18 | Wrapped ETH (ERC20) |
| wstETH | Base | `wrapped-steth-base` | 18 | Lido wrapped staked ETH |
| USDT0 | Arbitrum | `usdt0-arbitrum` | 6 | Tether on Arbitrum |
| HYPE | HyperEVM | `hyperliquid-hyperevm` | 18 | Use `tokens/gas/hyperevm` for native |

### Native gas tokens

For native chain tokens (ETH, HYPE), always use the gas endpoint:

```bash
poetry run wayfinder resource wayfinder://tokens/gas/ethereum   # ETH on Ethereum
poetry run wayfinder resource wayfinder://tokens/gas/base       # ETH on Base
poetry run wayfinder resource wayfinder://tokens/gas/arbitrum   # ETH on Arbitrum
poetry run wayfinder resource wayfinder://tokens/gas/hyperevm   # HYPE on HyperEVM
```

## Presenting Token Data to Users

- **Always show the human-readable symbol** alongside the canonical ID when confirming actions
- **Include the chain** — "USDC on Base" not just "USDC", since the same symbol exists on multiple chains
- **Show USD value** when available — `1,200.00 USDC ($1,200.00)` gives immediate context
- **For unfamiliar tokens** — include the contract address so users can verify on a block explorer
- **Fuzzy results** — when showing fuzzy matches, list them as a numbered selection so the user can pick by number

## Gotchas

- **ALWAYS search before using any token** — run `resource wayfinder://tokens/search/<chain>/<query>` and use the token ID from the result. Never construct token IDs by guessing the coingecko ID. Even for common tokens like ETH, the coingecko ID (`ethereum`) is not obvious from the symbol.
- **Enriched balances** (`resource wayfinder://balances/<label>`) include USD valuations and are the best starting point for portfolio overview.
- **Activity** (`resource wayfinder://activity/<label>`) shows recent on-chain transactions recorded by the ledger adapter.
- **Token decimals matter for amounts** — 1 USDC = `1000000` (6 decimals), 1 ETH = `1000000000000000000` (18 decimals). The CLI handles conversion when you pass human-readable amounts, but be aware when reading raw on-chain values.
- **Same symbol, different tokens** — "USDC" on Base and "USDC" on Arbitrum are different tokens with different contract addresses. Always qualify with the chain.
- **Native ETH in swaps** — Swapping native ETH (not WETH) may fail with `from_token_address: null` because the API returns null for native gas token addresses and the swap code doesn't normalize it. Use WETH (the wrapped ERC20 version) for swaps instead. Native ETH works fine for sends (`token: "native"`).
