# Moonwell

## Overview

Moonwell is a lending/borrowing protocol on Base. The Moonwell adapter provides market data reads and execution for lend/borrow/collateral operations.

- **Type**: `MOONWELL`
- **Module**: `wayfinder_paths.adapters.moonwell_adapter.adapter.MoonwellAdapter`
- **Capabilities**: `lending.lend`, `lending.unlend`, `lending.borrow`, `lending.repay`, `collateral.set`, `collateral.remove`, `rewards.claim`, `position.read`, `market.apy`, `market.collateral_factor`

## Market Data

```bash
# Describe the adapter (capabilities + market info)
poetry run wayfinder resource wayfinder://adapters/moonwell_adapter

# Check positions via wallet discovery
poetry run wayfinder wallets --action discover_portfolio --wallet_label main --protocols '["moonwell"]'
```

### Key Read Methods

| Method | Purpose | Wallet needed? |
|--------|---------|----------------|
| `get_apy(mtoken, apy_type, include_rewards)` | Supply/borrow APY | No |
| `get_collateral_factor(mtoken)` | Collateral factor (e.g. 0.88) | No |
| `get_pos(mtoken, account?, include_usd?)` | Single market position | Yes (or pass account) |
| `get_full_user_state(account?, include_rewards?, include_usd?, include_apy?)` | All positions + rewards | Yes (or pass account) |
| `is_market_entered(mtoken, account?)` | Check if collateral enabled | Yes (or pass account) |
| `get_borrowable_amount(account?)` | Account liquidity (USD) | Yes (or pass account) |
| `max_withdrawable_mtoken(mtoken, account?)` | Max withdraw without liquidation | Yes (or pass account) |

- **Comptroller**: `0xfbb21d0380bee3312b33c4353c8936a0f13ef26c` (Base)
- Only report values fetched from Moonwell contracts. Do not invent or estimate APYs.

## Execution

Moonwell operations are executed via one-off scripts under `.wayfinder_runs/`:

```bash
# Run a Moonwell script (dry run)
poetry run wayfinder run_script --script_path .wayfinder_runs/moonwell_lend.py --wallet_label main

# Run live
poetry run wayfinder run_script --script_path .wayfinder_runs/moonwell_lend.py --wallet_label main --force
```

### Script Example (supply USDC)

```python
from wayfinder_paths.mcp.scripting import get_adapter
from wayfinder_paths.adapters.moonwell_adapter import MoonwellAdapter

USDC_MTOKEN = "0xEdc817A28E8B93B03976FBd4a3dDBc9f7D176c22"
BASE_USDC = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"

adapter = get_adapter(MoonwellAdapter, "main")
ok, result = await adapter.lend(mtoken=USDC_MTOKEN, underlying_token=BASE_USDC, amount=10_000_000)  # 10 USDC
```

### Key Execution Methods

| Method | Purpose | Params |
|--------|---------|--------|
| `lend(mtoken, underlying_token, amount)` | Supply underlying | amount in raw units |
| `unlend(mtoken, amount)` | Withdraw (takes **mToken amount**, not underlying!) | amount in raw mToken units |
| `borrow(mtoken, amount)` | Borrow against collateral | amount in raw units |
| `repay(mtoken, underlying_token, amount, repay_full=False)` | Repay borrow | amount in raw units |
| `set_collateral(mtoken)` | Enable as collateral | — |
| `remove_collateral(mtoken)` | Disable collateral | — |
| `claim_rewards(min_rewards_usd?)` | Claim WELL rewards | returns dict of claimed rewards |
| `wrap_eth(amount)` | Wrap ETH to WETH | amount in raw units (wei) |

## Gotchas

- **mToken addresses, not underlying**: All adapter methods take **mToken addresses**, not underlying token addresses. `adapter.lend("0x833...", amount)` is wrong — use `adapter.lend("0xEdc...", amount)`.
- **Units are raw ints**: All `amount` parameters are **raw int units** (USDC: 6 decimals, so 10 USDC = `10_000_000`; WETH: 18 decimals; mTokens: 8 decimals).
- **unlend() takes mToken amount**: `unlend()` calls `redeem()` expecting **mToken amount**, not underlying. Use `max_withdrawable_mtoken()` first to get the correct value.
- **Exchange rate scaling**: When manually converting: `underlying = mTokenBalance * exchangeRate / 1e18`.
- **Collateral must be explicitly enabled**: Supplying tokens does NOT auto-enable them as collateral. Call `set_collateral()` separately.
- **Check before borrow**: Always call `get_borrowable_amount()` before borrowing — returns account liquidity in USD. Reverts are expensive.
- **Two USDC markets on Base**: Main: `0xEdc817A28E8B93B03976FBd4a3dDBc9f7D176c22` (use this). Secondary: `0x703843C3379b52F9FF486c9f5892218d2a065cC8`.
- **Transaction receipts**: A tx hash does **not** mean success. The SDK waits for receipt and raises `TransactionRevertedError` when `status=0`. If a step reverts, stop and fix before proceeding.
- **Health factor**: Monitor health factor before borrowing — liquidation risk increases with leverage.
- **APY composition**: Supply APY includes base rate + WELL token rewards. Both are shown in market data.
- **`get_borrowable_amount()` has no mtoken param**: Returns account-level liquidity in USD, not per-market.
- **Script execution**: Always run scripts via `run_script` with `--wallet_label` so the wallet profile tracks the Moonwell interaction for portfolio discovery.

## Moonwell wstETH Loop Strategy

For automated leveraged wstETH yield via Moonwell, use the dedicated strategy:

```bash
poetry run wayfinder run_strategy --strategy moonwell_wsteth_loop_strategy --action status
poetry run wayfinder run_strategy --strategy moonwell_wsteth_loop_strategy --action analyze --amount_usdc 500
```
