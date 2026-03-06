# Strategy Reference

## Quick Reference

| # | Strategy | Key Signal | Default Hold | Best Market |
|---|----------|-----------|--------------|-------------|
| 1 | Order Book Imbalance | volume_imbalance > 0.3 | Until reversal | Trending |
| 2 | Breakout | Price > lookback high + 0.1% | 50 snapshots | Volatile |
| 3 | False Breakout | Breakout reversal + absorption | 30 snapshots | Range-bound |
| 4 | Scalping | Microprice divergence | TP/SL (2/3 bps) | Tight spread |
| 5 | Momentum | Sustained price + imbalance | 80 snapshots | Strong trend |
| 6 | Reversal | Overextension + contrary imbalance | 60 snapshots | Mean-reverting |
| 7 | Spoofing Detection | Volume spike then vanish | 40 snapshots | Manipulated |
| 8 | Optimal Execution | Favorable imbalance windows | TWAP slices | Any |
| 9 | Market Making | Spread capture + inventory | TP/SL (1/5 bps) | Low vol |
| 10 | Latency Arbitrage | Microprice ≠ mid (>1.5 bps) | 10 snapshots | Fast-moving |

## Tunable Parameters

### 1. Order Book Imbalance
- `imbalance_threshold` (0.3): Min absolute imbalance to trigger entry. Range: 0.1–0.6.
- `exit_imbalance` (0.0): Close when imbalance crosses this toward zero.
- `lookback` (20): Warmup period.
- `cooldown` (10): Min snapshots between trades.

### 2. Breakout
- `lookback` (100): Window for high/low calculation.
- `breakout_pct` (0.001): Price move beyond high/low as fraction. 0.001 = 0.1%.
- `hold_periods` (50): Fixed holding period in snapshots.
- `volume_confirm_ratio` (1.5): Bid volume must exceed this × average to confirm.

### 3. False Breakout
- `lookback` (100): Window for support/resistance.
- `breakout_pct` (0.0008): Threshold to detect initial breakout.
- `reversal_pct` (0.0003): Not used directly; reversal detected when price returns inside range.
- `absorption_ratio` (2.0): Opposing volume must be this × supporting volume.
- `hold_periods` (30): Fixed holding period.

### 4. Scalping
- `microprice_threshold` (0.0002): Min microprice-to-mid divergence as fraction.
- `take_profit_bps` (2.0): Exit on this many bps profit.
- `stop_loss_bps` (3.0): Exit on this many bps loss.
- `min_spread_bps` (0.5): Only trade when spread < 5× this value.
- `cooldown` (5): Min snapshots between trades.

### 5. Momentum Trading
- `lookback` (50): Window for momentum calculation.
- `momentum_threshold` (0.0005): Min price change over lookback.
- `exit_reversal_pct` (0.3): Close if recent imbalance reverses beyond this.
- `hold_periods` (80): Max holding period.

### 6. Reversal Trading
- `lookback` (100): Window for mean calculation.
- `overextension_pct` (0.002): Price deviation from mean to trigger.
- `imbalance_extreme` (0.5): Min contrary imbalance to confirm reversal.
- `hold_periods` (60): Max holding period.
- `stop_loss_pct` (0.003): Hard stop loss as fraction.

### 7. Spoofing Detection
- `volume_spike_ratio` (3.0): Volume must exceed this × average to flag as potential spoof.
- `disappearance_ratio` (0.3): Volume must drop to this × previous to confirm spoof removal.
- `lookback` (20): Window for average volume.
- `hold_periods` (40): Fixed holding period.
- `cooldown` (15): Min snapshots between trades.

### 8. Optimal Execution
- `total_slices` (10): Number of execution slices.
- `slice_interval` (50): Target snapshots between slices (TWAP baseline).
- `favorable_imbalance` (0.1): Execute early when imbalance favors direction.
- `direction` ("buy"): "buy" or "sell".

### 9. Market Making
- `quote_offset_bps` (1.5): Distance from mid to post quotes.
- `take_profit_bps` (1.0): Exit on profit.
- `stop_loss_bps` (5.0): Exit on loss.
- `max_inventory` (3): Max directional exposure.
- `rebalance_threshold` (2): Inventory level triggering skew.
- `cooldown` (3): Min snapshots between trades.

### 10. Latency Arbitrage
- `divergence_bps` (1.5): Min microprice-to-mid divergence in bps.
- `hold_periods` (10): Very short hold — exploit stale quote.
- `cooldown` (8): Min snapshots between trades.
- `min_volume_ratio` (1.2): Not currently enforced; for future volume confirmation.

## Extending Strategies

To add a new strategy:
1. Subclass `Strategy` in `backtest.py`
2. Implement `on_snapshot(self, row, idx, df)`
3. Use `self.open_long()`, `self.open_short()`, `self.close_position()`
4. Register in `STRATEGY_MAP` dict
