# Modes

## 1) Project Mode

### greenfield
Use for new systems from scratch.

Expected pre-architecture outputs:
- requirements baseline
- architecture baseline
- ADR-0001
- initial CI/test strategy

### brownfield
Use for onboarding and evolving existing systems.

Expected pre-architecture outputs:
- as-is architecture
- system inventory
- dependency map
- legacy risk register
- characterization test baseline
- migration strategy with rollback points
- compatibility matrix

## 2) Execution Mode

### autonomous
- proceed automatically when gate checks pass
- auto-repair up to configured retries (default 2)
- pause only on persistent failures/blockers

### gated
- pause at every gate
- present pass/fail evidence
- require explicit user go-ahead to proceed

## Recommended Defaults

- Unknown/new domain → `gated`
- High-risk brownfield migration → `gated`
- Well-understood internal greenfield project → `autonomous`
