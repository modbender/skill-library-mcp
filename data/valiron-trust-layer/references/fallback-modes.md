# Fallback Modes

Define fallback behavior for Valiron lookup failures.

## Modes

- `fail-closed`
  - deny payment when trust decision is unavailable
  - use for high-value or irreversible transfers

- `fail-open-guarded`
  - allow only under emergency low limits + restricted rails
  - use only for low-risk/test scenarios

## Operational requirements

- Set mode per endpoint/payment class.
- Emit alert on fallback usage spikes.
- Re-check trust as soon as service recovers.
- Keep fallback decisions auditable.
