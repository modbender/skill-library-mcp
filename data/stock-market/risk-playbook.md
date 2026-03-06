# Risk Playbook — Stock Market

Apply this before validating any trade candidate.

## Position Risk Formula

Use:

`position_size = max_risk_amount / (entry_price - invalidation_price)`

Where:
- `max_risk_amount` is the pre-defined loss limit for one idea
- `entry_price - invalidation_price` is the per-share risk

If the size is too large for liquidity, reduce size or skip.

## Baseline Limits

| Control | Suggested Limit |
|---------|-----------------|
| Max risk per trade | 0.25% to 1.00% of account |
| Max daily loss | 1.0% to 2.0% of account |
| Max concurrent correlated positions | 2 to 3 |
| Max total open risk | 2.0% to 3.0% of account |

User-approved limits always override defaults.

## Volatility Adjustment

During high-volatility sessions:
- Cut normal size by 30-50%
- Widen invalidation only if thesis still holds
- Avoid adding to losers

During low-volatility sessions:
- Keep realistic target assumptions
- Avoid oversizing due to tighter stops

## No-Trade Conditions

Mark no-trade when any condition is true:
- No invalidation level can be defined
- Catalyst window is unclear
- Bid/ask spread or liquidity makes exits unreliable
- Emotional state overrides process
- Daily loss cap is already hit

## Post-Trade Risk Review

After close, log:
- Planned risk vs realized loss/gain
- Whether rules were followed
- Which limit prevented larger damage, if any

The objective is stable process quality, not short-term win rate.
