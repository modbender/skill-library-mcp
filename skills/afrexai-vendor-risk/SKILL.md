# Vendor Risk Assessment

Score and manage third-party vendor risk across security, financial stability, compliance, operational dependency, and data handling. Built for procurement teams, CISOs, and operations leaders managing 10+ vendors.

## Usage
Run this assessment for each critical vendor. Aggregate scores into a portfolio risk view.

## Assessment Framework

### 1. Vendor Risk Scorecard (5 Domains, 0-100 each)

**Security Posture (0-100)**
- SOC 2 Type II current? (+20)
- Penetration test within 12 months? (+15)
- Incident response plan documented? (+15)
- Data encryption at rest and transit? (+15)
- MFA enforced for all access? (+10)
- Security questionnaire completed? (+10)
- Subprocessor list disclosed? (+15)

**Financial Stability (0-100)**
- Revenue trend (growing +25, flat +10, declining 0)
- Funding runway >18 months? (+20)
- Customer concentration <20%? (+15)
- Public financials or audited statements? (+15)
- No material litigation? (+15)
- Credit rating acceptable? (+10)

**Compliance & Regulatory (0-100)**
- Industry certifications current? (+20)
- GDPR/CCPA compliant? (+20)
- Data processing agreement signed? (+15)
- Regulatory audit history clean? (+15)
- Right to audit clause? (+15)
- Data residency requirements met? (+15)

**Operational Dependency (0-100)**
- SLA with financial penalties? (+20)
- Uptime >99.9% trailing 12 months? (+20)
- Disaster recovery tested annually? (+15)
- Single point of failure for your business? (-20)
- Migration plan documented? (+15)
- API/export capability? (+15)
- Vendor lock-in risk assessment? (+15)

**Data Handling (0-100)**
- Data classification documented? (+20)
- Retention/deletion policies clear? (+20)
- Breach notification <72 hours? (+20)
- Data portability guaranteed? (+15)
- AI/ML training on your data? (opt-out available +15, no opt-out -10)
- Access logging and audit trail? (+10)

### 2. Risk Tier Classification

| Aggregate Score | Tier | Review Cadence | Action |
|----------------|------|---------------|--------|
| 400-500 | Low Risk | Annual | Standard monitoring |
| 300-399 | Moderate | Semi-annual | Remediation plan required |
| 200-299 | High Risk | Quarterly | Executive escalation, alternatives identified |
| 0-199 | Critical | Monthly | Exit plan required within 90 days |

### 3. Portfolio Risk View

```
Total vendors: ___
Critical tier: ___ (target: 0)
High risk: ___ (target: <10%)
Moderate: ___ (target: <30%)
Low risk: ___ (target: >60%)

Top 3 concentration risks:
1. [Vendor] — [function] — [% of operations dependent]
2. [Vendor] — [function] — [% of operations dependent]
3. [Vendor] — [function] — [% of operations dependent]

Annual vendor spend: $___
Spend on high/critical vendors: $___  (___%)
```

### 4. Cost of Vendor Failure

| Impact Area | Calculation |
|------------|-------------|
| Revenue loss | Daily revenue × expected downtime days |
| Recovery cost | Migration estimate + emergency procurement |
| Compliance penalty | Regulatory fine range for data breach via vendor |
| Reputation damage | Customer churn rate × LTV × affected customers |
| Operational disruption | Staff idle cost × recovery period |

### 5. Quarterly Review Template

- Score changes since last review (flag any >10 point drops)
- New subprocessors added by vendor
- SLA performance vs target
- Security incidents or near-misses
- Contract renewal timeline and negotiation leverage
- Alternative vendor benchmarking

### 6. Red Flags (Immediate Action)

- Vendor acquired by competitor
- Key personnel departures (CISO, CTO)
- Downtime exceeding SLA 2+ months
- Regulatory action or investigation
- Refusal to complete security questionnaire
- Data breach affecting other customers
- Sudden pricing changes >20%

## Industry-Specific Vendor Risks

| Industry | Critical Vendor Category | Specific Risk |
|----------|------------------------|---------------|
| Healthcare | EHR, billing, telehealth | HIPAA BAA gaps, PHI exposure |
| Financial Services | Core banking, payments, KYC | PCI DSS, regulatory reporting |
| Legal | Case management, ediscovery | Privilege breach, client data |
| SaaS | Infrastructure, auth, payments | Cascading outages, PII |
| Manufacturing | MES, supply chain, IoT | IP theft, production stoppage |
| Construction | Project management, safety | Compliance documentation gaps |
| Ecommerce | Payments, fulfillment, CDN | PCI, availability during peak |
| Recruitment | ATS, background check, payroll | Candidate PII, bias in AI screening |
| Real Estate | MLS, transaction mgmt, title | Wire fraud, closing delays |
| Professional Services | CRM, billing, document mgmt | Client confidentiality breach |

## Get the Full Playbook
- [AI Revenue Leak Calculator](https://afrexai-cto.github.io/ai-revenue-calculator/) — Quantify your total automation opportunity
- [Industry Context Packs](https://afrexai-cto.github.io/context-packs/) — $47 each, deep-dive playbooks
- [Agent Setup Wizard](https://afrexai-cto.github.io/agent-setup/) — Build your AI agent workforce
