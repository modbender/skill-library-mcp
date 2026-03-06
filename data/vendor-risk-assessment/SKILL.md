---
name: vendor-risk-assessment
description: >
  Assess third-party vendor risk for AI and SaaS products. Evaluates security posture,
  data handling, compliance, financial stability, and operational resilience. Use when
  onboarding new vendors, conducting annual reviews, or building a vendor management program.
  Generates a scored risk report with mitigation recommendations. Built by AfrexAI.
metadata:
  version: 1.0.0
  author: AfrexAI
  tags: [vendor-risk, security, compliance, procurement, enterprise]
---

# Vendor Risk Assessment

Evaluate any AI/SaaS vendor across 6 risk dimensions. Outputs a scored report with go/no-go recommendation.

## When to Use
- Onboarding a new SaaS or AI vendor
- Annual vendor review cycle
- Evaluating build-vs-buy decisions
- Due diligence for partnerships or acquisitions
- Compliance requirements (SOC2, ISO 27001, GDPR)

## How to Use

The user provides vendor details (name, product, website, any available documentation).
The agent researches and scores the vendor across 6 dimensions.

### Input Format
```
Vendor: [Company Name]
Product: [Product/Service Name]
Website: [URL]
Use Case: [What you'd use it for]
Data Sensitivity: [low/medium/high/critical]
Additional Context: [Any docs, certifications, or concerns]
```

## Assessment Framework

### 6 Risk Dimensions (each scored 1-10)

#### 1. Security Posture
- SOC2 Type II certification?
- Penetration testing cadence
- Encryption (at rest + in transit)
- Access controls and authentication
- Incident response plan
- Bug bounty program

#### 2. Data Handling & Privacy
- Data residency and sovereignty
- Data retention and deletion policies
- Sub-processor transparency
- GDPR/CCPA compliance
- Data portability (can you get your data out?)
- AI training opt-out policies

#### 3. Compliance & Certifications
- SOC2, ISO 27001, HIPAA, FedRAMP
- Industry-specific (PCI-DSS, HITRUST, etc.)
- AI-specific (EU AI Act readiness, NIST AI RMF)
- Audit frequency and transparency
- Regulatory track record

#### 4. Financial Stability
- Funding stage and runway
- Revenue indicators (public or estimated)
- Customer concentration risk
- Acquisition risk
- Pricing stability history

#### 5. Operational Resilience
- Uptime SLA and historical performance
- Disaster recovery plan
- Multi-region availability
- Dependency on single cloud provider
- Support responsiveness and escalation paths
- Change management process

#### 6. Contractual Terms
- Termination and exit clauses
- Liability caps and indemnification
- IP ownership clarity
- Auto-renewal traps
- Price increase limitations
- SLA breach remedies

## Output Format

```markdown
# Vendor Risk Assessment: [Vendor Name]
**Date:** YYYY-MM-DD
**Assessor:** AI Agent (AfrexAI)
**Data Sensitivity Level:** [low/medium/high/critical]

## Overall Risk Score: [X/10] — [LOW/MEDIUM/HIGH/CRITICAL]

## Dimension Scores
| Dimension | Score | Risk Level | Key Finding |
|-----------|-------|------------|-------------|
| Security Posture | X/10 | LOW/MED/HIGH | ... |
| Data Handling | X/10 | LOW/MED/HIGH | ... |
| Compliance | X/10 | LOW/MED/HIGH | ... |
| Financial Stability | X/10 | LOW/MED/HIGH | ... |
| Operational Resilience | X/10 | LOW/MED/HIGH | ... |
| Contractual Terms | X/10 | LOW/MED/HIGH | ... |

## Recommendation: [APPROVE / APPROVE WITH CONDITIONS / REJECT]

## Critical Findings
- [Finding 1]
- [Finding 2]

## Mitigation Requirements (if Approve with Conditions)
1. [Requirement 1 — deadline]
2. [Requirement 2 — deadline]

## Research Sources
- [Source 1]
- [Source 2]
```

## Scoring Guide
- **9-10:** Excellent — minimal risk, enterprise-grade
- **7-8:** Good — acceptable for most use cases
- **5-6:** Moderate — proceed with caution, mitigations needed
- **3-4:** Poor — significant concerns, conditional approval only
- **1-2:** Critical — recommend rejection or major remediation

## Overall Risk Calculation
- Average of 6 dimensions, weighted by data sensitivity:
  - Low sensitivity: equal weights
  - Medium: Security 2x, Data 2x
  - High: Security 3x, Data 3x, Compliance 2x
  - Critical: Security 4x, Data 4x, Compliance 3x, Financial 2x

## Research Process
1. Check vendor website for security/compliance pages
2. Search for SOC2/ISO certifications and trust pages
3. Check status pages for uptime history
4. Search for breach history or security incidents
5. Review pricing page for contract terms indicators
6. Check Crunchbase/LinkedIn for financial stability signals
7. Search for customer reviews mentioning reliability/support

## Pro Tips
- Request the vendor's SOC2 Type II report directly — if they hesitate, that's a signal
- Check their status page history (statuspage.io, etc.) for real uptime data
- For AI vendors specifically: ask about model training on your data, output ownership, and hallucination liability
- Compare their security page to competitors — vague = red flag

---

*Need help managing vendor risk across your entire stack? AfrexAI builds autonomous AI agents that monitor vendors continuously — not just at onboarding. Visit [afrexai.com](https://afrexai.com) or book a call: [calendly.com/cbeckford-afrexai/30min](https://calendly.com/cbeckford-afrexai/30min)*
