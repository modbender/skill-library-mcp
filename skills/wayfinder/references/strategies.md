# Strategies

## Strategy Interface

All strategies support these actions via `poetry run wayfinder run_strategy`:

### Read-Only Actions (no confirmation needed)

| Action | Description |
|--------|-------------|
| `status` | Current positions, balances, and state |
| `analyze` | Run strategy analysis with a given deposit amount |
| `snapshot` | Build batch snapshot for scoring |
| `policy` | Get strategy policies and constraints |
| `quote` | Get expected APY for a deposit amount |

### Fund-Moving Actions (require confirmation)

| Action | Description |
|--------|-------------|
| `deposit` | Add funds to the strategy (requires `--main_token_amount`) |
| `update` | Rebalance or execute the strategy logic |
| `withdraw` | **Liquidate**: Close all positions, convert to stablecoins (funds stay in strategy wallet) |
| `exit` | **Transfer**: Move funds from strategy wallet to main wallet (call after withdraw) |

## Available Strategies

### Basis Trading (`basis_trading_strategy`)

- **Status**: `stable`
- **Module**: `wayfinder_paths.strategies.basis_trading_strategy.strategy.BasisTradingStrategy`
- **Platform**: Hyperliquid
- **Token**: USDC
- **Risk**: Medium

Delta-neutral basis trading on Hyperliquid for funding rate capture. Opens matched positions:
- **Long Spot**: Buy the underlying asset (e.g., HYPE)
- **Short Perp**: Short the perpetual contract for the same asset

Price movements cancel out, and profit comes from collecting funding payments when longs pay shorts.

**Position Sizing** (given deposit `D` USDC and leverage `L`):
- Order Size: `D * (L / (L + 1))`
- Margin Reserved: `D / (L + 1)`

**Adapters Used**: BALANCE, LEDGER, TOKEN, HYPERLIQUID

```bash
poetry run wayfinder run_strategy --strategy basis_trading_strategy --action status
poetry run wayfinder run_strategy --strategy basis_trading_strategy --action analyze --amount_usdc 500
```

### Boros HYPE (`boros_hype_strategy`)

- **Status**: `stable`
- **Module**: `wayfinder_paths.strategies.boros_hype_strategy.strategy.BorosHypeStrategy`
- **Chains**: Arbitrum (42161), HyperEVM (999), Hyperliquid
- **Token**: HYPE/USDC
- **Risk**: Medium
- **Collateral Token (Arbitrum)**: LayerZero OFT HYPE at `0x007C26Ed5C33Fe6fEF62223d4c363A01F1b1dDc1`

Multi-leg HYPE yield strategy across Boros + HyperEVM + Hyperliquid. Holds spot HYPE, shorts perp on Hyperliquid, locks funding rate on Boros.

**Entry Flow**: Buys HYPE on Hyperliquid spot → withdraws to HyperEVM → bridges HyperEVM native HYPE → Arbitrum OFT HYPE for Boros collateral.

**Exit Gotchas**:
1. Boros withdraw delivers OFT HYPE on Arbitrum (no DEX liquidity)
2. Unwind path: Arbitrum OFT HYPE → (LayerZero) HyperEVM native HYPE → Hyperliquid spot → sell to USDC

**Adapters Used**: BALANCE, LEDGER, TOKEN, HYPERLIQUID, BOROS, BRAP

```bash
poetry run wayfinder run_strategy --strategy boros_hype_strategy --action status
poetry run wayfinder run_strategy --strategy boros_hype_strategy --action analyze --amount_usdc 1000
```

### HyperLend Stable Yield (`hyperlend_stable_yield_strategy`)

- **Status**: `stable`
- **Module**: `wayfinder_paths.strategies.hyperlend_stable_yield_strategy.strategy.HyperlendStableYieldStrategy`
- **Chain**: HyperEVM (999)
- **Token**: USDT0
- **Risk**: Low

Stablecoin yield optimization on HyperLend. Allocates USDT0 across HyperLend stablecoin markets by:
1. Transferring USDT0 (plus HYPE gas buffer) from main wallet to strategy wallet
2. Sampling HyperLend hourly rate history
3. Running bootstrap tournament analysis to identify best-performing stablecoin
4. Swapping and supplying to HyperLend
5. Enforcing hysteresis rotation policy to prevent excessive churn

**Key Parameters**:
| Parameter | Value | Description |
|-----------|-------|-------------|
| `MIN_USDT0_DEPOSIT_AMOUNT` | 1 | Minimum deposit |
| `GAS_MAXIMUM` | 0.1 HYPE | Max gas per deposit |
| `HYSTERESIS_DWELL_HOURS` | 168 | Rotation cooldown |
| `APY_REBALANCE_THRESHOLD` | 0.0035 | 35 bps edge required to rotate |

**Adapters Used**: BALANCE, LEDGER, TOKEN, HYPERLEND, BRAP

```bash
poetry run wayfinder run_strategy --strategy hyperlend_stable_yield_strategy --action status
```

### Moonwell wstETH Loop (`moonwell_wsteth_loop_strategy`)

- **Status**: `stable`
- **Module**: `wayfinder_paths.strategies.moonwell_wsteth_loop_strategy.strategy.MoonwellWstethLoopStrategy`
- **Chain**: Base (8453)
- **Tokens**: USDC, WETH, wstETH
- **Risk**: Medium-High

Leveraged wstETH carry trade on Base via Moonwell:
1. Deposits USDC as initial collateral on Moonwell
2. Borrows WETH against the USDC collateral
3. Swaps WETH to wstETH via Aerodrome/BRAP
4. Lends wstETH back to Moonwell as additional collateral
5. Repeats the loop until target leverage is reached

The position is **delta-neutral**: WETH debt offsets wstETH collateral, so PnL is driven by the spread between wstETH staking yield and WETH borrow cost.

**Key Parameters**:
| Parameter | Value | Description |
|-----------|-------|-------------|
| `MIN_GAS` | 0.002 ETH | Minimum gas buffer |
| `MIN_USDC_DEPOSIT` | 20 USDC | Minimum initial collateral |
| `MAX_DEPEG` | 0.01 (1%) | Max stETH/ETH depeg threshold |
| `MIN_HEALTH_FACTOR` | 1.2 | Triggers deleveraging if below |
| `MAX_HEALTH_FACTOR` | 1.5 | Triggers leverage loop if above |
| `leverage_limit` | 10 | Maximum leverage multiplier |

**Adapters Used**: BALANCE, LEDGER, TOKEN, MOONWELL, BRAP

```bash
poetry run wayfinder run_strategy --strategy moonwell_wsteth_loop_strategy --action status
```

### Stablecoin Yield (`stablecoin_yield_strategy`)

- **Status**: `wip` (work in progress)
- **Module**: `wayfinder_paths.strategies.stablecoin_yield_strategy.strategy.StablecoinYieldStrategy`
- **Chain**: Base (8453)
- **Token**: USDC
- **Risk**: Low

Automated USDC yield optimization on Base chain:
1. Transfers USDC (plus ETH gas buffer) from main wallet to strategy wallet
2. Searches Base-native pools for the best USD-denominated APY
3. Monitors DeFi Llama feeds and Wayfinder pool analytics
4. Rebalances to higher-yield pools when APY improvements exceed thresholds
5. Respects rotation cooldowns to avoid excessive churn

**Key Parameters**:
| Parameter | Value | Description |
|-----------|-------|-------------|
| `MIN_AMOUNT_USDC` | 2 | Minimum deposit |
| `MIN_TVL` | 1,000,000 | Minimum pool TVL |
| `ROTATION_MIN_INTERVAL` | 14 days | Cooldown between rotations |
| `DUST_APY` | 0.01 (1%) | APY threshold below which pools are ignored |
| `MIN_GAS` | 0.001 ETH | Minimum gas buffer |

**Adapters Used**: BALANCE, LEDGER, TOKEN, POOL, BRAP

```bash
poetry run wayfinder run_strategy --strategy stablecoin_yield_strategy --action status
poetry run wayfinder run_strategy --strategy stablecoin_yield_strategy --action deposit --main_token_amount 100 --gas_token_amount 0.01
poetry run wayfinder run_strategy --strategy stablecoin_yield_strategy --action update
```

### ProjectX THBILL/USDC (`projectx_thbill_usdc_strategy`)

- **Status**: `wip` (work in progress)
- **Module**: `wayfinder_paths.strategies.projectx_thbill_usdc_strategy.strategy.ProjectXThbillUsdcStrategy`
- **Chain**: HyperEVM (999)
- **Tokens**: THBILL, USDC
- **Risk**: Medium

Concentrated-liquidity market making on ProjectX (HyperEVM) for the THBILL/USDC stable pair. Pulls USDC from `main` wallet, swaps to an optimal split, mints/adds liquidity around the current tick, and periodically collects/compounds fees and recenters when out of range.

**Adapters Used**: BALANCE, LEDGER, TOKEN, PROJECTX

```bash
poetry run wayfinder run_strategy --strategy projectx_thbill_usdc_strategy --action status
poetry run wayfinder run_strategy --strategy projectx_thbill_usdc_strategy --action analyze --amount_usdc 1000
```

## Withdraw vs Exit

These are separate steps:

1. **`withdraw`** — Liquidates all positions and converts to stablecoins. Funds remain in the strategy wallet.
2. **`exit`** — Transfers funds from the strategy wallet back to the main wallet.

**Full exit flow:**
```bash
poetry run wayfinder run_strategy --strategy stablecoin_yield_strategy --action withdraw
poetry run wayfinder run_strategy --strategy stablecoin_yield_strategy --action exit
```

## Strategy Development

### Data Sources Golden Rule

Strategies call **adapters** for domain actions. Clients are low-level wrappers:
`Strategy → Adapter → Client(s) → Network/API`

Never invent or "ballpark" rates/APYs/funding. Prefer a concrete adapter/client/tool call. If you can't fetch, say "unavailable" and show the exact call needed.

### Manifests

Each strategy directory has a `manifest.yaml` (source of truth) with `entrypoint`, `name`, `permissions.policy`, `adapters`. Validate with `just validate-manifests`.

### Testing Contract

- Maintain `examples.json` per strategy — load test inputs from it (never hardcode).
- Provide smoke coverage for lifecycle: `deposit → update → status → withdraw`.
- Optional methods: `quote()`, `analyze()`, `build_batch_snapshot()` for APY queries and batch scoring.

### Safety Patterns

- Wallets in `config.json` are matched by label (label == strategy directory name).
- Never commit private keys or live credentials.
- EVM execution goes through `send_transaction` (waits for receipts) and `ensure_allowance` (ERC20 approvals).
- Prefer MCP tools for side effects: `execute()`, `hyperliquid_execute()`, `run_script()`.

### Explore-First Approach

When exploring an unfamiliar strategy:
1. Start from its `manifest.yaml` (capabilities, entrypoint, dependencies)
2. Read its `examples.json` (expected inputs and runtime assumptions)
3. Prefer read-only calls first; only move to execution after validating inputs/units

## Discovering Strategies

Always discover before guessing strategy names:

```bash
# List all available strategies
poetry run wayfinder resource wayfinder://strategies

# Get detailed description for a specific strategy
poetry run wayfinder resource wayfinder://strategies/stablecoin_yield_strategy
```

Strategy names use `snake_case` (e.g., `boros_hype_strategy`, not `hype_boros_strategy`).
