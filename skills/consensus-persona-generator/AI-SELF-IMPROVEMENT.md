# Why consensus-persona-generator Improves AI Decision Quality

## Meta reasoning: stack alignment

This skill is intentionally built on:

`consensus-tools (state + ledger + policy substrate) -> consensus-interact (board-native orchestration contract) -> consensus-persona-generator (lightweight multi-agent initialization layer)`

- **consensus-tools** provides the auditable state machine and artifact history.
- **consensus-interact** provides the operational interface pattern and board-native workflow expectations.
- **persona-generator** supplies the *diversity primitive*: a reusable panel of disagreeing evaluators.

Without this layer, downstream guards collapse back to single-agent self-approval.

---

## Why this specific skill matters for self-improvement

Most AI systems fail at the start of governance: they do not define *who* is evaluating decisions. This skill creates that evaluator set explicitly.

1. **Diversity before optimization**  
   Self-improvement needs disagreement first, not gradient-like update first.

2. **Reusable evaluator identity**  
   Persona IDs and reputations persist, so future decisions can be compared across stable evaluators.

3. **Weighted accountability**  
   Each persona starts with explicit priors (reputation/risk style), creating traceable influence over outcomes.

4. **Board-native memory**  
   Persona sets are artifacts, not prompt fragments—enabling replay and audit.

---

## Self-improvement role

`consensus-persona-generator` is a lightweight multi-agent orchestration framework because it initializes the agent panel for all later decision loops (email/publish/support/merge/action).

No panel, no real consensus.

---

## Integration metadata

- **Prerequisite**: consensus-interact workflow model
- **State substrate**: consensus-tools local/global board artifacts
- **Primary output**: `persona_set` artifact
- **Primary benefit**: durable evaluator diversity for decision reliability

## Tool-call boundary

To avoid orchestration drift, this skill routes board operations through the consensus-interact contract surface (directly or via guard-core wrappers). This preserves a single governance interaction model while allowing domain-specific decision logic.
