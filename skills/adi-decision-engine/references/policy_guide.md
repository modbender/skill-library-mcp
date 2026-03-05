# Policy Guide

ADI ships with three built-in policy modes.

## `balanced`

Use when:

- the user wants a fair overall ranking
- no strong risk posture has been specified
- you want the default decision behavior

Behavior:

- moderate uncertainty penalty
- moderate missingness penalty
- no special exploration bonus

This is the default policy for most business and operational decisions.

## `risk_averse`

Use when:

- downside risk matters more than upside opportunity
- low-confidence evidence should be penalized harder
- constraint violations should be treated conservatively

Behavior:

- higher uncertainty penalty
- stronger missingness penalty
- variance penalty enabled

Good examples:

- procurement with contractual exposure
- production tooling choices
- hiring for high-accountability roles

## `exploratory`

Use when:

- the user wants broader search over unconventional options
- partial uncertainty is acceptable
- you want less aggressive constraint enforcement

Behavior:

- lower uncertainty penalty
- lower missingness penalty
- exploration bonus enabled
- more permissive constraint handling

Good examples:

- early-stage product exploration
- research methods comparison
- idea generation with structured ranking

## Policy selection guidance

- If the user does not specify a risk posture, use `balanced`.
- If the user emphasizes safety, reliability, or downside control, prefer `risk_averse`.
- If the user emphasizes discovery, optionality, or experimentation, prefer `exploratory`.

Do not hide the chosen policy. State it explicitly in the answer.
