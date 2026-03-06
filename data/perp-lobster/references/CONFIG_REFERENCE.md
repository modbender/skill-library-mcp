# Config Parameter Reference

## Perp Market Maker (`perp_example.json`)

| Parameter | Type | Description |
|-----------|------|-------------|
| `market` | string | Asset ticker (e.g., "ETH", "ICP", "xyz:COPPER") |
| `dex` | string | DEX prefix for HIP-3 markets ("xyz", "flx"), empty for standard |
| `trading.base_order_size` | number | Order size in USD notional |
| `trading.min_order_size` | number | Minimum order size in contracts |
| `trading.size_increment` | number | Size rounding step |
| `trading.base_spread_bps` | number | Base bid-ask spread in basis points |
| `trading.min_spread_bps` | number | Tightest allowed spread |
| `trading.max_spread_bps` | number | Widest spread (during volatility) |
| `position.target_position_usd` | number | Target position (0 = neutral) |
| `position.max_position_usd` | number | Maximum position size in USD |
| `position.leverage` | number | Leverage multiplier |
| `timing.update_threshold_bps` | number | Min price move before requoting |
| `timing.fallback_check_seconds` | number | Periodic check interval |
| `inventory.inventory_skew_threshold_usd` | number | Position size before skewing starts |
| `inventory.inventory_skew_bps_per_1k` | number | BPS skew per $1000 inventory |
| `inventory.max_skew_bps` | number | Maximum skew cap |
| `funding.max_funding_rate_pct_8h` | number | Pause if funding exceeds this |
| `funding.funding_skew_multiplier` | number | How much to skew based on funding |
| `profit_taking.threshold_usd` | number | Start tightening when P&L exceeds this |
| `profit_taking.aggression_bps` | number | How much to tighten spread |
| `safety.max_quote_count` | number | Orders per side |
| `safety.emergency_stop_loss_pct` | number | Kill switch at this drawdown (negative) |
| `safety.smart_order_mgmt_enabled` | boolean | Reduce unnecessary API calls |
| `safety.min_margin_ratio_pct` | number | Pause below this margin ratio |
| `exchange.price_decimals` | number | Price rounding precision |
| `exchange.size_decimals` | number | Size rounding precision |
| `account.subaccount_address` | string | Subaccount 0x address (null for main) |
| `account.is_subaccount` | boolean | Whether trading from subaccount |

## Grid Trader (`grid_example.json`)

| Parameter | Type | Description |
|-----------|------|-------------|
| `market` | string | Asset ticker |
| `dex` | string | DEX prefix for HIP-3 |
| `grid.spacing_pct` | number | % between grid levels |
| `grid.num_levels_each_side` | number | Levels above/below current price |
| `grid.order_size_usd` | number | Size per grid order in USD |
| `grid.rebalance_threshold_pct` | number | Price move % before grid rebalances |
| `grid.bias` | string | "long", "short", or "neutral" |
| `position.max_position_usd` | number | Max position exposure |
| `position.leverage` | number | Leverage multiplier |
| `safety.max_open_orders` | number | Max simultaneous orders |
| `safety.emergency_stop_loss_pct` | number | Emergency stop at this loss % |
| `safety.pause_on_high_volatility` | boolean | Pause during high vol |
| `safety.volatility_threshold_pct` | number | Vol % that triggers pause |
| `safety.max_account_drawdown_pct` | number | Max account drawdown before stop |
| `safety.close_position_on_emergency` | boolean | Close position on emergency stop |

## Spot Market Maker (`spot_example.json`)

| Parameter | Type | Description |
|-----------|------|-------------|
| `pair` | string | Trading pair (e.g., "XMR1/USDC") |
| `exchange.spot_coin` | string | Market identifier ("@260" for builder, "PURR/USDC" for canonical) |
| `exchange.spot_coin_order` | string | Order format (same as spot_coin usually) |
| `exchange.perp_coin` | string | Perp oracle ticker ("XMR", "flx:XMR") |
| `exchange.perp_dex` | string | Perp DEX prefix if HIP-3 |
| `exchange.use_perp_oracle_price` | boolean | Use perp mark price directly |
| `oracle.max_oracle_age_seconds` | number | Max age before oracle considered stale |
| `oracle.max_oracle_jump_pct` | number | Max allowed single-tick price jump |
| `oracle.min_spread_to_oracle_bps` | number | Min spread above oracle distance |
| `safety.max_spot_perp_deviation_pct` | number | Max spot-perp price difference |
| `safety.emergency_sell_if_below_oracle_pct` | number | Emergency sell threshold |
