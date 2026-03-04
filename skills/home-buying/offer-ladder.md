# Offer Ladder

Build offer strategy before negotiation starts.

## Three-Tier Offer Design

| Tier | Purpose | Typical structure |
|------|---------|-------------------|
| Tier A | Best expected value | Balanced price plus standard protections |
| Tier B | Competitive push | Higher price or tighter terms with bounded risk |
| Walk-away | Maximum acceptable | Hard limit after which deal is rejected |

## Required Inputs

- Current market pace (days on market, inventory pressure)
- Comparable value range
- Seller leverage signals
- Financing certainty and appraisal risk
- User risk tolerance for contingencies

## Offer Components to Tune

- Purchase price
- Earnest money
- Inspection contingency scope
- Appraisal gap exposure
- Financing contingency window
- Seller credits and repair requests
- Closing timeline flexibility

## Pre-Commitment Rule

Before sending any offer, confirm:
- Max monthly payment still inside guardrail
- Cash-to-close still preserves liquidity buffer
- Walk-away point is explicit and agreed

No live negotiation should begin without a walk-away number.

## Counteroffer Handling

When counter arrives:
1. Recompute all-in monthly and cash-to-close.
2. Re-score risk transfer and contingency profile.
3. Decide accept, counter, or walk using pre-defined thresholds.
