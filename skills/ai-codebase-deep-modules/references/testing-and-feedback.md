# Testing and feedback loops for greybox modules

A deep module becomes a **greybox** when you can trust its behaviour without reading its internals.

That trust comes from:
- a fast feedback loop (run locally + in CI)
- contract tests at the boundary

## The “fast loop” checklist

Aim for a default `verify` command that:
- runs in minutes (ideally < 2–5 for unit-level signal)
- fails loudly with actionable messages
- is deterministic

If your repo has multiple packages/services:
- add `verify:fast` (unit + typecheck) and `verify:full` (integration/e2e)
- make the agent run `verify:fast` frequently while refactoring

## Contract tests (module boundary tests)

Contract tests focus on **what the module promises**, not how it does it.

For each exported function/type:
- 1–3 happy path tests
- at least 1 meaningful error/edge case
- side effects verified via fakes/spies

Examples of boundary contract assertions:
- return value shape is stable
- errors are typed/structured and documented
- database writes happen exactly once
- events are emitted with the expected payload

## A practical sequence for risky refactors

1. **Freeze the surface**
   - Write down the public API you want.
   - Add a thin wrapper over existing code to match that API.
2. **Add contract tests**
   - If there are no tests, start with “golden master” tests:
     - given input X, output matches snapshot Y
     - useful for stabilising behaviour before improving it
3. **Refactor internals**
   - move helpers into `internal/`
   - replace implementations gradually
4. **Tighten tests over time**
   - replace snapshots with explicit assertions
   - add internal tests only where justified

## What to test where

- **Boundary / contract tests** (high value)
  - live next to the module
  - protect consumers
  - enable internal rewrites

- **Internal unit tests** (selective)
  - for complex algorithms
  - for performance-sensitive code

- **Integration tests** (targeted)
  - verify real DB/API wiring
  - keep small; they’re slower and flakier

## Making tests AI-friendly

Tests should:
- be runnable with one command
- use clear naming (“should return invalid-credentials when …”)
- include minimal fixture complexity
- avoid non-determinism (time, random, network)

When failures happen, error output should tell the agent:
- what broke
- where to look
- what invariant was violated
