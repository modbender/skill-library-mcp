# Economic Validation

Economic validation is mandatory for market-dependent attacks.

## Required Inputs

- chain and block context
- liquidity depth for impacted pools/markets
- price sources and oracle update cadence
- slippage and fee model
- attacker capital assumptions (own + flash loan)
- unwind path for profit realization

## Evaluation Steps

1. Quantify required capital.
2. Quantify expected slippage and execution costs.
3. Quantify extractable value or protocol loss.
4. Confirm execution sequence can settle profitably.
5. Compare gross gain vs gas/fees/borrow costs.

## Reject Conditions

Reject or downgrade if:
- required liquidity is unrealistic
- execution requires impossible ordering guarantees
- expected profit is below costs
- exploit assumes infinite flash liquidity without route support
- impact only exists under extreme, rare market conditions

## Output Block

Include:
- `capital_required`
- `liquidity_constraints`
- `execution_cost_estimate`
- `profit_or_loss_estimate`
- `economic_confidence` (high/medium/low)

If low confidence and no hard evidence, keep finding as `Theoretical`.
