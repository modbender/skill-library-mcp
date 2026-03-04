---
name: valiron-payment-interceptor
description: Intercept and authorize outgoing machine-to-machine payments (x402 or similar) using @valiron/sdk trust decisions on the counterparty agent before payment execution. Use when implementing payment middleware, wallet spend guards, policy engines, trust-based allow/deny/throttle decisions, fail-open/fail-closed behavior, and auditable transaction risk controls.
metadata: {"openclaw":{"skillKey":"valiron-payment-interceptor","primaryEnv":"VALIRON_API_KEY"}}
---

# Valiron Payment Interceptor

Add a trust gate in front of outgoing agent payments.

## Runtime requirements

Declare and validate runtime prerequisites before enabling the interceptor:

- Node.js runtime compatible with your app and `@valiron/sdk`.
- Installed dependencies:
  - `@valiron/sdk`
  - Your payment rail package(s) (x402 or equivalent) used by the host app.
- Configuration/credentials (via secret manager or env vars):
  - `VALIRON_API_KEY` (optional today; reserved for authenticated deployments)
  - `VALIRON_BASE_URL` (if using non-default endpoint)
  - `VALIRON_TIMEOUT_MS` (optional, with safe default)
- Policy/config inputs:
  - Decision policy JSON (route-to-action matrix)
  - Spend limit defaults and per-route overrides

Fail startup (or fail closed for payment endpoints) when required policy/config inputs are missing. If your deployment enforces SDK auth, treat `VALIRON_API_KEY` as required.

## Workflow

1. Extract counterparty identity from the payment request.
   - Prefer `counterpartyAgentId`.
   - Support wallet fallback with `getWalletProfile(wallet)`.
2. Evaluate trust with Valiron.
   - Fast path: `checkAgent(agentId)`.
   - Full path: `getAgentProfile(agentId)` when you need reasons/signals, pricing, or audit details.
3. Apply deterministic decision policy from `references/decision-policy.md`.
4. Enforce spend controls from `references/spend-controls.md`.
5. If allowed, continue to payment initiation (x402 challenge creation or equivalent flow).
6. If blocked/restricted, return explicit denial/degrade reason.
7. Log outcome using `references/audit-events.md`.

## Decision model

Map route decisions to payment actions:

- `prod`: allow payment under normal limits.
- `prod_throttled`: allow with reduced caps/rate limits.
- `sandbox`: allow only test/sandbox payment rail (or deny prod transfer).
- `sandbox_only`: deny outgoing payment.

Never authorize payment using free-form model output alone.

## x402-specific sequencing

For x402-protected purchases or settlement-like flows:

1. Trust-check counterparty identity.
2. Evaluate route + spend policy.
3. If denied, abort before creating payment commitment.
4. If allowed, generate/send x402 payment payload.
5. Record authorization decision + amount + result.

## Outage and fallback

Use endpoint-class fallback from `references/fallback-modes.md`:

- High-risk payment actions: `fail-closed`.
- Low-risk/test actions: optional `fail-open-guarded` with strict caps.

Keep fallback mode explicit and versioned.

## Use bundled resources

- Runtime + credential checklist: `references/runtime-requirements.md`
- Decision matrix: `references/decision-policy.md`
- Spend/risk controls: `references/spend-controls.md`
- Fallback guidance: `references/fallback-modes.md`
- Audit schema: `references/audit-events.md`
- Error handling: `references/error-handling.md`
- Interceptor template: `assets/payment-interceptor.ts`
- Policy validator: `scripts/validate-payment-policy.mjs`
