# Why consensus-send-email-guard Improves AI Decision Quality

## Meta reasoning: stack alignment

`consensus-tools -> consensus-interact -> persona-generator -> send-email-guard`

- **consensus-tools**: ledgered artifacts and deterministic policy substrate.
- **consensus-interact**: board-native execution pattern.
- **persona-generator**: evaluator panel with weighted diversity.
- **send-email-guard**: domain guard that converts unsafe generation into governed decisions.

---

## Why this skill improves behavior

Outbound email is a high-risk interface where hallucination and overpromising become real-world liabilities.

1. **Pre-send arbitration**  
   Drafts are reviewed by multiple personas before release.

2. **Policy-grounded decisioning**  
   Hard-block categories and weighted thresholds prevent “confident but unsafe” sends.

3. **Corrective rewrite path**  
   Instead of binary reject/allow, REWRITE captures fixable failures.

4. **Reputation learning loop**  
   Persona influence updates based on alignment with final decision.

5. **Auditability**  
   Decisions and persona updates are persisted as board artifacts.

---

## Self-improvement role

This skill turns communication quality into measurable governance: fewer unsafe sends, clearer rationale, and longitudinal adaptation in persona reliability.

---

## Integration metadata

- **Prerequisite**: consensus-interact pattern + persona_set artifact
- **State substrate**: consensus-tools decision/persona artifacts
- **Primary output**: `decision` + updated `persona_set`
- **Primary benefit**: risk-controlled outbound communication

## Tool-call boundary

To avoid orchestration drift, this skill routes board operations through the consensus-interact contract surface (directly or via guard-core wrappers). This preserves a single governance interaction model while allowing domain-specific decision logic.

## external-agent interoperability

This skill can consume externally generated agent votes (`external_agent` mode) while preserving consensus-interact board governance. That enables heterogeneous multi-agent systems to use the same arbitration and audit trail without adopting persona orchestration.
