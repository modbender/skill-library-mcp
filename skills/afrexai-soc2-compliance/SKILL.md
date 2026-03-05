# SOC 2 Compliance Accelerator

Your agent for achieving and maintaining SOC 2 Type I and Type II compliance — from readiness assessment through audit completion.

## What This Does

Guides organizations through the full SOC 2 lifecycle: gap analysis, control implementation, evidence collection, audit prep, and continuous monitoring. Covers all 5 Trust Service Criteria with practical implementation steps.

## How to Use

Tell your agent what stage you're at:

- **"Run SOC 2 readiness assessment"** — 64-point gap analysis across all Trust Service Criteria
- **"Build SOC 2 control matrix"** — Maps controls to criteria with ownership and evidence requirements
- **"Create SOC 2 evidence collection plan"** — Automated and manual evidence gathering schedule
- **"Prepare for SOC 2 audit"** — Auditor-ready documentation package checklist
- **"SOC 2 continuous monitoring dashboard"** — Ongoing compliance tracking after certification

## Trust Service Criteria Coverage

### CC — Common Criteria (Security) — Required
- CC1: Control Environment (tone at top, org structure, accountability)
- CC2: Communication & Information (internal/external, system boundaries)
- CC3: Risk Assessment (risk identification, fraud risk, change impact)
- CC4: Monitoring Activities (ongoing evaluations, deficiency reporting)
- CC5: Control Activities (policies, technology controls, deployment)
- CC6: Logical & Physical Access (access management, authentication, physical security)
- CC7: System Operations (vulnerability management, incident response, recovery)
- CC8: Change Management (change authorization, testing, approval)
- CC9: Risk Mitigation (vendor management, business continuity)

### Optional Criteria
- **Availability (A1)**: Uptime SLAs, DR/BCP, capacity planning
- **Processing Integrity (PI1)**: Data accuracy, completeness, timeliness
- **Confidentiality (C1)**: Classification, encryption, retention, disposal
- **Privacy (P1)**: Notice, consent, collection, use, disclosure, access

## Readiness Assessment Framework

### Phase 1: Scoping (Week 1)
```
System Description Checklist:
□ Infrastructure components (cloud, on-prem, hybrid)
□ Software stack (applications, databases, middleware)
□ People (roles, responsibilities, third parties)
□ Procedures (operational, security, change management)
□ Data flows (ingress, processing, storage, egress)
□ Trust Service Criteria selection (Security + which optional?)
□ Subservice organizations (cloud providers, SaaS tools)
□ Carve-out vs inclusive method for subservice orgs
```

### Phase 2: Gap Analysis (Weeks 2-3)
Score each control area 1-5:
- **1 — Not Started**: No policy, no process, no evidence
- **2 — Ad Hoc**: Informal processes exist but undocumented
- **3 — Defined**: Documented but inconsistent execution
- **4 — Managed**: Documented, executed, some evidence
- **5 — Optimized**: Automated, monitored, auditable evidence

Priority Matrix:
| Gap Score | Action | Timeline |
|-----------|--------|----------|
| 1-2 | Critical — implement immediately | 2-4 weeks |
| 3 | Important — formalize and document | 1-2 weeks |
| 4 | Minor — fill evidence gaps | 3-5 days |
| 5 | Maintain — continue monitoring | Ongoing |

### Phase 3: Remediation (Weeks 3-10)
```
For each gap:
1. Assign control owner (by name, not role)
2. Define implementation steps
3. Set evidence collection method (automated preferred)
4. Establish testing cadence
5. Document exception handling process
```

## Control Implementation Priorities

### Must-Have Controls (Week 1-4)
1. **Access Management**: SSO, MFA on all systems, quarterly access reviews
2. **Encryption**: TLS 1.2+ in transit, AES-256 at rest, key management
3. **Logging**: Centralized logging, 90-day retention minimum, tamper-evident
4. **Incident Response**: Documented plan, defined roles, tested annually
5. **Change Management**: Approval workflows, code review, deployment gates
6. **Vendor Management**: Vendor inventory, risk assessments, SOC 2 reports from critical vendors
7. **Employee Security**: Background checks, security awareness training, acceptable use policy
8. **Vulnerability Management**: Regular scanning, patch cadence (critical <72hrs), penetration testing

### Should-Have Controls (Week 4-8)
9. **Business Continuity**: DR plan, RTO/RPO defined, tested semi-annually
10. **Data Classification**: 4-tier model (Public, Internal, Confidential, Restricted)
11. **Network Security**: Segmentation, IDS/IPS, WAF for web applications
12. **Endpoint Protection**: EDR, device encryption, MDM for mobile

### Nice-to-Have Controls (Week 8+)
13. **Security Metrics Dashboard**: Real-time compliance posture
14. **Automated Compliance Monitoring**: Continuous control testing
15. **Zero Trust Architecture**: Beyond perimeter security

## Evidence Collection Guide

### Automated Evidence (Set Once, Collect Forever)
| Control | Evidence Source | Tool Examples |
|---------|---------------|---------------|
| Access Reviews | IAM exports | Okta, Azure AD, AWS IAM |
| Encryption | Config snapshots | AWS Config, CloudTrail |
| Logging | Log aggregation | Datadog, Splunk, ELK |
| Vulnerability Scans | Scan reports | Qualys, Nessus, Snyk |
| Change Management | PR/deploy history | GitHub, GitLab, Jira |
| Uptime | Monitoring dashboards | Datadog, PagerDuty |

### Manual Evidence (Scheduled Collection)
| Control | Evidence Type | Frequency |
|---------|--------------|-----------|
| Background Checks | HR records | Per hire |
| Security Training | Completion certificates | Annual |
| Risk Assessment | Assessment document | Annual |
| Pen Testing | Report | Annual |
| DR Testing | Test results | Semi-annual |
| Board/Mgmt Review | Meeting minutes | Quarterly |
| Vendor Reviews | Assessment records | Annual |
| Policy Reviews | Version history | Annual |

## Audit Timeline

### Type I (Point-in-Time) — 8-12 weeks total
```
Week 1-2:   Auditor selection + engagement letter
Week 2-4:   System description draft
Week 4-6:   Control documentation + evidence prep
Week 6-8:   Fieldwork (auditor testing)
Week 8-10:  Draft report review
Week 10-12: Final report issued
```

### Type II (Period of Time) — 3-12 month observation + 4-6 weeks fieldwork
```
Month 1:     Observation period begins (minimum 3 months, recommend 6-12)
Ongoing:     Evidence collection, control operation
Month 3-12:  Observation period ends
+Week 1-2:   Fieldwork scheduling
+Week 2-4:   Fieldwork (testing over observation period)
+Week 4-6:   Draft report + final report
```

## Cost Framework

| Company Size | Type I | Type II | Annual Maintenance |
|-------------|--------|---------|-------------------|
| Startup (<50) | $20K-$50K | $30K-$80K | $15K-$40K |
| Mid-Market (50-500) | $40K-$100K | $60K-$150K | $30K-$80K |
| Enterprise (500+) | $80K-$200K | $120K-$300K | $60K-$150K |

Includes: auditor fees, tooling, personnel time, remediation costs.

Hidden costs to budget:
- Compliance automation platform: $10K-$50K/year
- Additional security tooling: $5K-$30K/year
- Personnel time (internal): 200-800 hours
- Policy/procedure writing (if outsourced): $5K-$20K

## Common Audit Findings (Avoid These)

1. **Access not revoked within 24 hours of termination** — #1 finding
2. **Missing or incomplete risk assessment** — annual requirement
3. **No evidence of management review** — need meeting minutes
4. **Incomplete vendor management** — missing SOC reports from critical vendors
5. **Inconsistent change management** — emergency changes without retroactive approval
6. **Security training gaps** — new hires not trained within 30 days
7. **Logging gaps** — not all in-scope systems sending to central logging

## AI Agent SOC 2 Considerations (2026)

When deploying AI agents in SOC 2 environments:
- **Data boundaries**: Agents must not access data outside their defined scope
- **Audit trail**: All agent actions must be logged and attributable
- **Access controls**: Agent service accounts need same rigor as human accounts
- **Model governance**: Document which models process customer data
- **Prompt injection defense**: Part of CC7 (system operations) controls
- **Output validation**: Processing integrity controls for agent outputs

## Industry-Specific Requirements

| Industry | Extra Criteria | Key Controls |
|----------|---------------|-------------|
| **Fintech** | All 5 TSC typical | SOX mapping, encryption everywhere, PCI if payments |
| **Healthcare** | Privacy, Confidentiality | HIPAA crosswalk, BAAs, PHI handling |
| **SaaS** | Availability, Confidentiality | Multi-tenant isolation, SLA compliance |
| **Legal** | Confidentiality, Privacy | Privilege protection, matter isolation |
| **Construction** | Security, Availability | Field data protection, offline capability |
| **E-commerce** | All 5 TSC typical | PCI DSS alignment, transaction integrity |

## 7 SOC 2 Mistakes That Cost Companies 6+ Months

1. **Starting with Type II** — Get Type I first, prove controls work, then observe
2. **Scoping too broadly** — Only include systems that touch customer data
3. **Choosing the wrong auditor** — Pick one who knows your industry
4. **Manual evidence collection** — Automate from day 1 or drown in spreadsheets
5. **Treating it as a project, not a program** — SOC 2 is continuous
6. **Ignoring subservice organizations** — Your cloud provider's SOC 2 matters
7. **No executive sponsor** — Compliance without budget authority = failure

---

## Get the Full Implementation Package

This skill gives you the framework. For industry-specific compliance playbooks with regulatory crosswalks, cost models, and vendor selection guides:

🔗 **[AfrexAI Context Packs](https://afrexai-cto.github.io/context-packs/)** — $47 per industry vertical

Available packs: Fintech, Healthcare, Legal, Construction, E-commerce, SaaS, Real Estate, Recruitment, Manufacturing, Professional Services

🔗 **[AI Revenue Leak Calculator](https://afrexai-cto.github.io/ai-revenue-calculator/)** — Find where compliance gaps cost you money

🔗 **[Agent Setup Wizard](https://afrexai-cto.github.io/agent-setup/)** — Deploy compliance monitoring agents in minutes

**Bundle pricing:**
- Pick 3 packs: $97
- All 10 packs: $197
- Everything bundle: $247
