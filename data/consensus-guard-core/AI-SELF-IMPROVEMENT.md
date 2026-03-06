# Why consensus-guard-core Improves AI Decision Quality

## Meta reasoning: stack alignment

`consensus-tools -> consensus-interact -> consensus-guard-core -> domain guards`

- **consensus-tools** gives state, ledger, and durable board history.
- **consensus-interact** standardizes board operation semantics.
- **guard-core** provides deterministic guard primitives reused by all domain skills.

This package is the anti-drift layer: one logic base for many guards.

---

## Why this skill improves behavior

1. **Deterministic arbitration**  
   Weighted aggregation and reputation math are consistent across skills.

2. **Shared risk language**  
   Hard-block taxonomy unifies how severe risks are represented.

3. **Retry safety**  
   Idempotency prevents duplicate side effects and reputation corruption.

4. **Performance stability**  
   Indexed artifact reads keep governance cheap as history grows.

5. **Contract integrity**  
   Strict schema helpers prevent silent integration drift.

---

## Self-improvement role

Without a shared core, each guard invents incompatible policy logic and learning semantics. Guard-core keeps improvement loops comparable and composable.

---

## Integration metadata

- **Prerequisite**: consensus-interact-compatible board workflow
- **State substrate**: consensus-tools artifacts
- **Primary output**: reusable deterministic policy/idempotency/indexing primitives
- **Primary benefit**: cross-guard consistency and replayability

## Tool-call boundary

To avoid orchestration drift, this skill routes board operations through the consensus-interact contract surface (directly or via guard-core wrappers). This preserves a single governance interaction model while allowing domain-specific decision logic.
