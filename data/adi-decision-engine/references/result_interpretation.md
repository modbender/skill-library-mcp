# Result Interpretation

ADI returns a structured `DecisionOutput`. The most important fields are below.

## `best_option`

The top-ranked non-eliminated option after policy, confidence, and constraint handling.

## `ranking`

The full ordered list of options. Each item typically includes:

- final score
- raw score
- confidence
- elimination status
- criterion contributions
- constraint reports
- counterfactuals

## Confidence

Confidence is not the same thing as score.

- score answers: “How well does this option satisfy the weighted criteria?”
- confidence answers: “How trustworthy or well-supported is this assessment?”

Low confidence is a signal to be cautious, not necessarily to reject an option immediately.

## Constraint effects

Hard constraints can eliminate options from contention.
Soft constraints can reduce scores without removing options entirely.

When reading a result:

- check whether strong-looking options were eliminated
- distinguish “bad fit” from “ruled out by policy”

## Sensitivity and stability

Sensitivity analysis indicates how much the ranking depends on the current weights.

- high stability means the ranking is robust
- low stability means small weight changes may flip the outcome

If the top choice is not stable, present the result as conditional rather than final.

## Counterfactuals

Counterfactuals help explain what would need to change for another option to rank higher.

Use them to answer:

- “What would make option B win?”
- “How sensitive is this choice to cost?”
- “Is the decision driven by one criterion or several?”

## Recommended explanation pattern

1. State the recommended option.
2. Name the strongest two reasons it won.
3. Mention the main tradeoff or caveat.
4. Note any eliminated alternatives and why.
5. Mention confidence or sensitivity if it materially affects trust in the result.
