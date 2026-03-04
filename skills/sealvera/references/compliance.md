# SealVera — Regulation Mapping

## EU AI Act (August 2, 2026 enforcement)

Applies to high-risk AI systems: hiring, credit, insurance, healthcare, law enforcement, migration, administration of justice.

| Requirement | Article | SealVera coverage |
|---|---|---|
| Log all outputs from high-risk AI | Art. 12 | Every decision logged automatically |
| Retain records 10 years | Art. 12(1) | Enterprise plan — configurable retention |
| Transparency about AI decision-making | Art. 13 | Full evidence trail, factor-level reasoning |
| Human oversight — anomaly detection | Art. 9, 14 | Behavioral monitoring + alert rules |
| Ongoing conformance demonstration | Art. 9 | Chain integrity + compliance reports |
| Right to explanation | Art. 13 | Per-decision evidence trail, exportable |

**Action:** Set `SEALVERA_AGENT` to match the regulated system name. Ensure Enterprise plan for 10-year retention.

---

## FINRA / SEC

Applies to financial services firms using AI in customer-facing or trading decisions.

| Requirement | SealVera coverage |
|---|---|
| Decision records with full context | Full — inputs, reasoning, outcome |
| Tamper-evident records (WORM) | RSA signatures + hash chain |
| 6-year retention | Enterprise plan |
| Supervisory evidence | Alert acknowledgment log + monitoring history |

---

## HIPAA

Applies to AI systems processing Protected Health Information (PHI).

| Control | SealVera coverage |
|---|---|
| Audit controls §164.312(b) | Full decision records with tamper-evident signatures |
| Integrity controls | Hash chain + RSA signatures detect any modification |
| Access controls | Org-scoped API keys |
| Transmission security | TLS in transit |

**Note:** If decisions involve PHI, a BAA may be required. Contact SealVera before connecting.

---

## GDPR Article 22

Right not to be subject to solely automated decisions with legal/significant effects. Right to explanation.

| Requirement | SealVera coverage |
|---|---|
| Meaningful explanation of logic | Factor-level evidence trail |
| Actual values observed | Each reasoning_step includes the real value from input data |
| Right to contest | Full record exportable per subject access request |

**Action:** Set `userId` on every log call so records are searchable by individual. Use `GET /api/logs?search=<userId>` to retrieve.

---

## SOC 2

Increasingly expected for enterprise AI systems. SealVera addresses:

| Trust criterion | Control | SealVera |
|---|---|---|
| CC7.2 — System monitoring | Monitor AI for anomalies | Behavioral baseline + drift detection |
| CC7.3 — Evaluate and respond | Document anomaly response | Alert acknowledgment log with timestamps |
| PI1 — Processing integrity | Outputs complete, valid, accurate | Full records with integrity verification |

---

## SV-10 Standard

The SealVera open standard for AI agent accountability. 10 requirements across 5 sections.

Full standard: `https://app.sealvera.com/standard`
Self-assessment: `https://app.sealvera.com/standard#assessment`

An agent connected to SealVera with auto-reasoning enabled satisfies:
- SV-01 through SV-05 (records, retention, attestation, chain, replay)
- SV-06 through SV-08 (monitoring, alerts, traces) — automatically
- SV-09 and SV-10 (reporting) — via compliance report endpoint
