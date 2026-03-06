# Decision Policy (Valiron Route -> Payment Action)

## Baseline mapping

- `prod`
  - authorization: allow
  - rail: production
  - limits: standard

- `prod_throttled`
  - authorization: allow_with_limits
  - rail: production
  - limits: strict caps + reduced burst

- `sandbox`
  - authorization: restricted
  - rail: sandbox/test only
  - limits: minimal

- `sandbox_only`
  - authorization: deny
  - rail: none
  - limits: zero

## Required policy fields

- `route`
- `authorization`
- `allowedRails`
- `maxAmountPerPayment`
- `maxAmountPerHour`
- `maxAmountPerDay`
- `requireHumanApprovalOver`
- `fallbackMode`

## Guardrails

- Never allow `sandbox_only` on production rail.
- Use exact rails allowlist; avoid wildcard rules.
- Keep policy versioned and reviewable.
