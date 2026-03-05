# S12+ Advanced Diligence Questions

## Project Background & Acknowledgment

This skill was built using the SOC 2 Quality Guild resources at **s2guild.org** as a baseline for quality-focused SOC 2 vendor attestation reviews.

This project was the first GRC agent I wanated to try creating with OpenClaw after setting up across multiple environments, including Raspberry Pi, Intel NUC, several LXC containers, and a cluster setup of 3 Mac Studios using EXO.

Big thanks to the **SOC 2 Quality Guild community** for sharing excellent, practical guidance that helped shape this agent.


Use this set after S1–S11 to improve real-world vendor risk decisions.

## Scoring (optional)

For each item:
- Met = sufficient evidence
- Partial = some evidence but material gaps
- Unmet = weak/no evidence
- Unknown = not provided

## S12 Scope Completeness
- Which Trust Services Categories are out of scope (Availability, Confidentiality, Processing Integrity, Privacy)?
- Why are they out of scope given the vendor’s product and data handling?

## S13 Change Delta Since Prior Report
- What major changes occurred since last cycle (architecture, products, ownership, control set, auditor)?
- Are prior-year issues closed with evidence?

## S14 Exception Severity and Remediation Proof
- What are the highest-severity exceptions?
- What was impact/blast radius?
- Is remediation complete with dated evidence?

## S15 Bridge Letter / Gap Coverage
- Is there a bridge letter from report end date to present?
- Any material control failures or incidents during bridge period?

## S16 Subservice Organization Reliance Depth
- Is the report inclusive or carve-out for critical subservice orgs?
- Which key controls are inherited vs directly operated?
- Are subservice SOC reports current and aligned to dependency risk?

## S17 Control Automation and Monitoring Maturity
- Which controls are manual vs automated?
- Are controls preventive or detective?
- Is continuous monitoring in place with tamper-resistant logs/evidence retention?

## S18 Incident and Regulatory Event Disclosure
- Any security incidents, outages, or regulator-notifiable events during/after the period?
- Were customers notified when required?

## S19 Vulnerability and Patch Performance
- Vulnerability SLA compliance by severity (critical/high/medium).
- External attack surface review cadence and findings.
- Patch latency and overdue risk acceptance evidence.

## S20 Identity Lifecycle and Privilege Governance
- JML timeliness metrics (especially leavers).
- Privileged access controls, PAM usage, break-glass process.
- Access review quality and manager attestation rigor.

## S21 Data Governance and Crypto Operations
- Current data flow map and data classification coverage.
- Retention/deletion enforcement evidence.
- Encryption at rest/in transit details and key-management ownership/rotation.
- Backup restore test success and frequency.

## S22 Resilience and DR Realism
- Latest BCP/DR test date and scope.
- Target vs achieved RTO/RPO.
- Open DR findings and target closure dates.

## S23 Independence and Commercial Pressure Signals
- Any preferred-auditor ecosystem incentives via GRC partners?
- Signs of commoditized audits (speed guarantees, guaranteed outcomes).
- Independence safeguards in engagement model.

## S24 Shared Responsibility Precision
- What controls must customers implement for effective risk coverage?
- Are customer obligations clearly mapped to product features and configurations?

## S25 Evidence Freshness Test
- Can vendor provide fresh raw evidence for 3–5 critical controls now?
- Does fresh evidence match SOC narrative and stated frequencies?

## Output requirements

For each S12+ item, provide:
1. Status (Met/Partial/Unmet/Unknown)
2. Evidence reviewed
3. Risk implication
4. Follow-up ask

If 4+ items are `Unknown`, default recommendation should be at least `Accept with conditions` (or `Escalate` for sensitive data use cases).
