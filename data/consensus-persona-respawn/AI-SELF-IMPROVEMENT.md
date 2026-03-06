# Why consensus-persona-respawn Improves AI Decision Quality

## Meta reasoning: stack alignment

`consensus-tools -> consensus-interact -> persona-generator -> persona-respawn`

This skill closes the lifecycle gap: when personas degrade, governance should adapt rather than stagnate.

---

## Why this skill improves behavior

1. **Failure-informed replacement**  
   New personas are seeded from ledger mistake patterns, not random refresh.

2. **Controlled evolution**  
   Persona mutation is explicit, versioned, and auditable.

3. **Anti-stagnation mechanism**  
   Dead/low-reputation personas are replaced before they degrade decision quality.

4. **Continuity with adaptation**  
   Role slot persists while behavior profile is improved.

5. **Replayable learning narrative**  
   Respawn artifacts capture why and how changes were made.

---

## Self-improvement role

This is the governance equivalent of model maintenance: evaluator quality is monitored and refreshed from observed error modes.

---

## Integration metadata

- **Prerequisite**: persona_set artifact history via consensus-interact flows
- **State substrate**: consensus-tools decisions + persona artifacts
- **Primary output**: `persona_respawn` + updated `persona_set`
- **Primary benefit**: adaptive evaluator evolution with auditability

## Tool-call boundary

To avoid orchestration drift, this skill routes board operations through the consensus-interact contract surface (directly or via guard-core wrappers). This preserves a single governance interaction model while allowing domain-specific decision logic.
