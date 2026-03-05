# Why consensus-support-reply-guard Improves AI Decision Quality

## Meta reasoning: stack alignment

`consensus-tools -> consensus-interact -> persona-generator -> support-reply-guard`

The same consensus substrate is applied to customer support, where language mistakes create trust and liability damage.

---

## Why this skill improves behavior

1. **Customer-facing safety control**  
   Catches legal/sensitive/confidentiality failures before send.

2. **Escalation-aware arbitration**  
   Multi-persona review reduces single-tone overconfidence.

3. **Operational consistency**  
   Similar support risks are judged with similar policy logic.

4. **Adaptive oversight**  
   Persona reputations evolve with decision alignment.

5. **Audit and coaching value**  
   Board artifacts expose recurring support failure patterns.

---

## Self-improvement role

Support quality becomes a governed loop: detect risk, rewrite safely, learn from outcomes.

---

## Integration metadata

- **Prerequisite**: consensus-interact conventions + persona_set
- **State substrate**: consensus-tools artifacts
- **Primary output**: support decision + updated persona set
- **Primary benefit**: reduced customer-facing risk and improved consistency

## Tool-call boundary

To avoid orchestration drift, this skill routes board operations through the consensus-interact contract surface (directly or via guard-core wrappers). This preserves a single governance interaction model while allowing domain-specific decision logic.

## external-agent interoperability

This skill can consume externally generated agent votes (`external_agent` mode) while preserving consensus-interact board governance. That enables heterogeneous multi-agent systems to use the same arbitration and audit trail without adopting persona orchestration.
