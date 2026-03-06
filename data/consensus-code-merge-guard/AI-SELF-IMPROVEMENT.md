# Why consensus-code-merge-guard Improves AI Decision Quality

## Meta reasoning: stack alignment

`consensus-tools -> consensus-interact -> persona-generator -> code-merge-guard`

This skill translates consensus governance into engineering release decisions.

---

## Why this skill improves behavior

1. **Merge-time arbitration**  
   Security/reliability/performance concerns are weighted before merge.

2. **Hard fail conditions**  
   Test/security constraints become explicit block criteria.

3. **Reduced release variance**  
   Similar PR risk patterns get consistent treatment.

4. **Reputation-calibrated reviewers**  
   Personas that align with robust outcomes gain influence.

5. **Replayable governance**  
   Merge decisions are no longer opaque reviewer intuition.

---

## Self-improvement role

Engineering quality improves by turning merge decisions into a measurable policy loop instead of ad hoc approvals.

---

## Integration metadata

- **Prerequisite**: consensus-interact flow + persona_set artifact
- **State substrate**: consensus-tools board artifacts
- **Primary output**: merge decision artifact + updated persona set
- **Primary benefit**: safer, more consistent release governance

## Tool-call boundary

To avoid orchestration drift, this skill routes board operations through the consensus-interact contract surface (directly or via guard-core wrappers). This preserves a single governance interaction model while allowing domain-specific decision logic.

## external-agent interoperability

This skill can consume externally generated agent votes (`external_agent` mode) while preserving consensus-interact board governance. That enables heterogeneous multi-agent systems to use the same arbitration and audit trail without adopting persona orchestration.
