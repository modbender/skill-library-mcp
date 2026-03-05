# tradebot-tuning

## Purpose
Increase tradability **safely** by adjusting parameters one step at a time based on regime and diagnostics.

## Use when
- No trades for long periods
- Diagnostics show gates failing (trend_ok/breakout_ok always 0)

## Safety rails
- Keep risk controls enabled (daily loss cap, max trades).
- One change per cycle; log before/after.

## Tuning ladder (preferred order)
1) Switch strategy based on regime:
   - RANGE → reversion
   - TREND → breakout
2) vol_surge → 1.0
3) adx_period → 0
4) cooldown_m ↓ (min 1)
5) lookback ↓ (min 6)
6) max_hold_m ↑ (max 30)

## Verification
- After each change: confirm signals updating and `signal` sometimes flips.
- If losses exceed limits: tighten / halt.
