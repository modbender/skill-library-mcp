# Spend Controls

Apply deterministic spend constraints before initiating payment.

## Control layers

1. Per-payment cap (`maxAmountPerPayment`)
2. Sliding-window cap (`maxAmountPerHour`)
3. Daily cap (`maxAmountPerDay`)
4. Counterparty concentration limit (max % of daily spend to one agent)
5. Optional human approval threshold (`requireHumanApprovalOver`)

## Recommended defaults

- `prod`: normal caps
- `prod_throttled`: 20-50% of prod caps
- `sandbox`: tiny limits and test rail only
- `sandbox_only`: zero

## Additional controls

- Currency allowlist
- Merchant/category allowlist (if available)
- Idempotency key required
- Replay window checks
