# Why consensus-agent-action-guard Improves AI Decision Quality

## Meta reasoning: stack alignment

`consensus-tools -> consensus-interact -> persona-generator -> agent-action-guard`

This skill governs the final mile: high-risk agent actions before execution.

---

## Why this skill improves behavior

1. **Pre-execution governance**  
   Risky actions are evaluated before irreversible effects occur.

2. **Action-class policy mapping**  
   Weighted consensus maps to ALLOW/BLOCK/REQUIRE_REWRITE.

3. **Irreversibility control**  
   High-risk destructive actions can be blocked or require human confirmation.

4. **Consistency across automation**  
   Different agents/actions share one governance standard.

5. **Accountability receipts**  
   Decision artifacts record rationale for every gated action.

---

## Self-improvement role

Autonomous systems improve when action quality is constrained by explicit policy and feedback, not post-hoc regret.

---

## Integration metadata

- **Prerequisite**: consensus-interact board workflow + persona_set
- **State substrate**: consensus-tools decision/persona artifacts
- **Primary output**: action decision artifact + updated persona set
- **Primary benefit**: safer autonomous execution under clear governance

## Tool-call boundary

To avoid orchestration drift, this skill routes board operations through the consensus-interact contract surface (directly or via guard-core wrappers). This preserves a single governance interaction model while allowing domain-specific decision logic.

## external-agent interoperability

This skill can consume externally generated agent votes (`external_agent` mode) while preserving consensus-interact board governance. That enables heterogeneous multi-agent systems to use the same arbitration and audit trail without adopting persona orchestration.
