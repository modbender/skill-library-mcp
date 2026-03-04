# Request Schema

The skill uses the upstream ADI `DecisionRequest` schema as its canonical execution contract.

## Minimum runnable request

A runnable request needs:

- `options`
- `criteria`

Each option must have:

- `name`
- `values`

Each criterion should have:

- `name`
- `weight`
- `direction`

## Core fields

### `options`

List of candidate choices to rank.

Each option contains:

- `name`: human-readable identifier
- `values`: criterion measurements for that option
- optional `metadata`

### `criteria`

List of evaluation criteria.

Each criterion contains:

- `name`
- `weight`
- `direction`: `benefit` or `cost`
- optional `description`
- optional fuzzy settings in advanced use cases

### `constraints`

Optional hard or soft rules, such as:

- must exclude an option
- minimum acceptable value
- maximum allowed value

### `policy_name`

Optional policy selector:

- `balanced`
- `risk_averse`
- `exploratory`

### `preferences`

Optional weight overrides or saved profile input.

### `context`

Optional human-readable context for logging and explanation. It does not replace structured decision inputs.

## Common mistakes

- Missing numeric values for option/criterion pairs
- Mixing subjective prose into numeric value fields
- Omitting criterion direction
- Using overlapping criteria like `cost`, `price`, and `budget impact` without clear separation
- Treating `context` as if it replaces the request schema

## Good criterion examples

- `cost`
- `implementation_time`
- `reliability`
- `quality_score`
- `walking_minutes`
- `transfer_count`
- `interpretability`

## Weak criterion examples

- `best overall`
- `goodness`
- `vibes`
- `seems fine`

These are too ambiguous to score consistently.

## Guidance

- Prefer 3 to 5 criteria for most decisions.
- Use explicit units where possible.
- Make every criterion direction obvious.
- Use weights that reflect real tradeoff importance rather than equal defaults unless equality is intentional.

## Recommended authoring pattern

For polished decision requests:

1. Name options in business language, not internal shorthand.
2. Use criteria that can be measured or at least scored consistently.
3. Add `description` to each criterion when the metric is domain-specific.
4. Attach `confidence` or `evidence` when the quality of information is uneven across options.
5. Use `context` to explain the decision frame, not to hide missing structure.

## Strong request checklist

- At least 2 options are present.
- Every option has values for every important criterion.
- Every criterion has both a weight and a direction.
- Constraints reflect real policy limits rather than preferences already captured in weights.
- The chosen policy matches the actual decision posture.
