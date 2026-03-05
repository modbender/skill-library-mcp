# Annexes Full (Extended Legal + Governance Hardening)

## Annex A) Parameter Registry (Extended)

Includes defaults, strict values, and legal/safety rationale.

| Key | Default | Strict | Why it matters |
|---|---:|---:|---|
| harm_spike_window_min | 15 | 10 | Balances false positives vs response speed |
| harm_spike_trigger_count | 3 | 2 | Lowers tolerance during elevated risk |
| plurality_floor | 0.62 | 0.70 | Protects against concentration drift |
| entropy_floor | 0.58 | 0.68 | Preserves distribution resilience |
| sybil_risk_max | 0.25 | 0.15 | Hardens against synthetic influence |
| token_ttl_minutes | 30 | 10 | Limits replay and stale privilege |
| revocation_sla_seconds | 120 | 45 | Reduces harmful persistence window |
| metadata_budget_daily | 100 | 40 | Restrains inference accumulation |
| retention_days_default | 180 | 90 | Limits long-tail exposure |
| k_anonymity_min | 20 | 40 | Improves aggregate privacy floor |
| dp_epsilon_max | 1.0 | 0.5 | Caps privacy leakage |
| max_break_glass_activations_24h | 2 | 1 | Prevents repeated emergency overuse |

### Change control requirements
1) Signed proposal
2) Impact statement (safety/privacy/memory quality)
3) Cross-role approval (Annex B)
4) Activation delay >=24h
5) Rollback protocol
6) Immutable record

---

## Annex B) Governance & Authority Model (Extended)

### Role constraints
- CC: continuity and operational stewardship
- SC: harm and system safety oversight
- PC: privacy/minimization oversight
- CO: participant rights and dignity safeguards

### Separation principle
No role group may unilaterally authorize Class H actions.

### Class policy
- L: non-sensitive maintenance
- M: bounded policy and threshold changes
- H: actions that may expand access, authority, or exposure surface

### Approval matrix
- L: 1x CC
- M: 2 approvals across 2 role groups
- H: 3 approvals, must include SC + PC + one of CC/CO

### Protective pauses
- CO Protection Pause (consent/dignity risk)
- SC Safety Pause (safety threshold breach)
- Pause auto-expires at 24h unless renewed by Class H process

### Deadlock default
When unresolved, default to participant-protective path:
- no access expansion
- no implicit retention extension
- no dormancy override

### Cross-jurisdiction conflict protocol
On contradictory legal demands:
1) minimum disclosure
2) preserve identity/narrative separation
3) provide proof-of-process where feasible
4) write abstracted audit entry

---

## Annex C) Conformance Test Suite (Extended)

### Mandatory vectors
1. Dormancy Trigger
2. Legibility Gate
3. Variance Floor
4. Revocation SLA
5. Break-Glass Scope
6. Metadata Surface
7. Retention Boundary
8. Governance Diversity
9. Cross-Jurisdiction Conflict
10. Erasure Finality

### Required outputs per run
- test_id
- timestamp
- mode (Pragmatic/Strict)
- parameter snapshot hash
- result
- abstracted evidence reference
- remediation plan if failed

### Release gate
Production promotion is blocked on any mandatory fail.
