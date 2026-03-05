# Whistleblower & Ethics Hotline Framework

Build a confidential reporting system and ethics investigation workflow for your organization. Covers anonymous intake, case triage, investigation protocols, regulatory obligations, and retaliation prevention.

## What This Skill Does

When activated, guide the user through:

1. **Intake Channel Design** — Set up anonymous reporting (web form, hotline, email alias, physical drop box). Ensure no metadata leaks caller identity. Recommend third-party platforms (EthicsPoint, NAVEX, AllVoices) vs self-hosted.

2. **Case Triage Matrix**
   | Severity | Examples | Response SLA | Escalation |
   |----------|----------|-------------|------------|
   | Critical | Fraud >$50K, safety hazard, harassment by exec | 24 hours | Board/Audit Committee + outside counsel |
   | High | Policy violation, discrimination, data breach | 72 hours | General Counsel + CHRO |
   | Medium | Conflict of interest, expense abuse | 5 business days | Compliance Officer |
   | Low | Policy questions, minor conduct | 10 business days | HR Business Partner |

3. **Investigation Protocol**
   - Preserve evidence before interviewing
   - Separation of duties: investigator ≠ accused's manager
   - Interview template: open questions, avoid leading, document verbatim
   - Chain of custody for digital evidence
   - Timeline reconstruction framework
   - Findings memo template (facts only, no opinion)

4. **Regulatory Compliance by Jurisdiction**
   - **US**: SOX Section 301 (public companies must have anonymous channel), Dodd-Frank (SEC bounty program, anti-retaliation), False Claims Act (qui tam)
   - **EU**: EU Whistleblower Directive 2019/1937 (mandatory for 50+ employees, 3-month feedback deadline)
   - **UK**: Public Interest Disclosure Act 1998 (PIDA), FCA whistleblowing rules
   - **Australia**: Corporations Act 2001 Part 9.4AAA
   - **Canada**: PSDPA (federal public sector), provincial variations

5. **Retaliation Prevention Checklist**
   - Document reporter's current performance rating, comp, role BEFORE investigation
   - No adverse actions (termination, transfer, demotion, schedule change) without compliance sign-off
   - Monitor for subtle retaliation: exclusion from meetings, workload changes, peer pressure
   - Mandatory retaliation training for all managers annually
   - Exit interview flag: "Were you ever discouraged from reporting concerns?"

6. **Board Reporting Template**
   - Quarterly: # reports received, # open, # closed, avg resolution time, category breakdown
   - Annual: trends, benchmarking vs industry (NAVEX Hotline Benchmark Report), policy changes made, training completion rates

7. **Policy Document Generator**
   Output a complete Whistleblower Protection Policy covering:
   - Purpose and scope
   - Protected disclosures definition
   - Reporting channels
   - Confidentiality and anonymity guarantees
   - Investigation process overview
   - Non-retaliation commitment
   - Record retention (7 years minimum)
   - Annual review clause

8. **10-Industry Benchmarks**
   | Industry | Avg Reports per 100 Employees | Top Category | Compliance Focus |
   |----------|-------------------------------|-------------|-----------------|
   | Financial Services | 1.4 | Fraud/Theft | SOX, BSA/AML, FCA |
   | Healthcare | 1.8 | Patient Safety | HIPAA, False Claims Act |
   | Manufacturing | 0.9 | Safety/Environment | OSHA, EPA |
   | Technology | 0.7 | HR/Discrimination | SOX (if public), GDPR |
   | Government | 1.2 | Waste/Abuse | Inspector General, PSDPA |
   | Education | 0.8 | Title IX, Safety | Clery Act, Title IX |
   | Retail | 1.1 | Theft/HR | FLSA, state wage laws |
   | Energy | 1.0 | Safety/Environment | NRC, EPA, OSHA |
   | Legal/Professional | 0.6 | Conflicts of Interest | Bar rules, SOX |
   | Construction | 1.3 | Safety/Wage | OSHA, Davis-Bacon |

## Output Format

Deliver as structured markdown with clear sections. Include jurisdiction-specific callouts based on user's location. Provide copy-paste policy language where appropriate.

---

*Built by AfrexAI — AI agent context packs for every business function.*
*Browse all packs: https://afrexai-cto.github.io/context-packs/*
