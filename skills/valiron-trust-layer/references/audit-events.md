# Audit Event Schema

Log one event per authorization attempt.

## Required fields

- `timestamp`
- `requestId`
- `paymentId`
- `counterparty.agentId` or wallet source
- `amount` + `currency`
- `rail`
- `valiron.route`
- `valiron.reasons[]` (sanitized)
- `policyVersion`
- `authorization.outcome` (`allow` | `allow_with_limits` | `restricted` | `deny`)
- `fallback.used`
- `fallback.mode`
- `error.code` (if any)

## Redaction

- Never log secrets/private keys/tokens.
- Hash sensitive IDs when feasible.
- Cap free-form fields.
