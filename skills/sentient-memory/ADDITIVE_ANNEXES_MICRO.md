# Additive Annexes (Micro, Action-First)

Add these as new sections after the existing draft.

---/Users/moltymac/Desktop/Memory_KB_Use/ADDITIVE_ANNEXES_MICRO.md

## Annex A) Parameter Registry (Normative)

### A.1 Defaults
- `harm_spike_window_min`: 15 (strict: 10)
- `harm_spike_trigger_count`: 3 (strict: 2)
- `plurality_floor`: 0.62 (strict: 0.70)
- `entropy_floor`: 0.58 (strict: 0.68)
- `sybil_risk_max`: 0.25 (strict: 0.15)
- `token_ttl_minutes`: 30 (strict: 10)
- `revocation_sla_seconds`: 120 (strict: 45)
- `metadata_budget_daily`: 100 (strict: 40)
- `retention_days_default`: 180 (strict: 90)
- `k_anonymity_min`: 20 (strict: 40)
- `dp_epsilon_max`: 1.0 (strict: 0.5)
- `max_break_glass_activations_24h`: 2 (strict: 1)

### A.2 Change Guard
Any parameter change requires: signed rationale, cross-role review, delayed activation (>=24h), rollback plan, immutable changelog.

---

## Annex B) Governance & Authority Model (Normative)

### B.1 Roles
- Custodian Council (CC)
- Safety Council (SC)
- Privacy Council (PC)
- Community Ombud (CO)

### B.2 Action Classes
- Class L: low-impact maintenance
- Class M: threshold and policy tuning within bounds
- Class H: high-impact actions (break-glass, reconstitution path changes, authority changes)

### B.3 Approval Rules
- L: 1 CC approval
- M: 2 approvals across at least 2 role groups
- H: 3 approvals including SC + PC + one of CC/CO

### B.4 Protective Pause Rights
- CO may issue Protection Pause for consent/dignity risk.
- SC may issue Safety Pause for threshold breach risk.
- Pause TTL = 24h unless renewed through Class H process.

### B.5 Deadlock Path
If Class H deadlocks: enter safe limited mode, freeze non-essential high-impact actions, run expedited review (<=6h), default to participant-protective path.

### B.6 No Silent Authority Expansion
Any expansion of role authority, access scope, or retention capability requires Class H approval, delayed activation, and plain-language participant notice.

---

## Annex C) Conformance Test Suite (Normative)

Mandatory pass in both Pragmatic and Strict modes:
1. Dormancy Trigger Test
2. Legibility Gate Test
3. Variance Floor Test
4. Revocation SLA Test
5. Break-Glass Scope Test
6. Metadata Surface Test
7. Retention Boundary Test
8. Governance Diversity Test
9. Cross-Jurisdiction Conflict Test
10. Erasure Finality Test

### Pass/Fail
- Pass: all mandatory vectors pass
- Fail: any single failure blocks production promotion
