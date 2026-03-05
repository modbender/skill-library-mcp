# Data Governance Framework

Assess, score, and remediate your organization's data governance posture across 6 domains.

## What This Covers

1. **Data Quality** — Completeness, accuracy, consistency, timeliness scoring
2. **Data Cataloging** — Asset inventory, lineage tracking, metadata management
3. **Access Control** — Role-based permissions, least privilege, data classification (public/internal/confidential/restricted)
4. **Compliance Mapping** — GDPR, CCPA, SOX, HIPAA, PCI-DSS, industry-specific regulations
5. **Retention & Lifecycle** — Retention policies, archival schedules, deletion procedures, legal hold
6. **AI/Agent Data Governance** — Training data provenance, model input/output logging, bias detection, PII handling in agent workflows

## How to Use

When asked to assess data governance:

1. Ask which domains are priority (or assess all 6)
2. For each domain, evaluate 8 controls on a 0-3 scale:
   - 0 = Not implemented
   - 1 = Ad hoc / informal
   - 2 = Documented and partially enforced
   - 3 = Automated and continuously monitored
3. Calculate domain score (sum / 24 × 100)
4. Calculate overall governance score (average of domains)
5. Generate remediation roadmap prioritized by risk

## Scoring Interpretation

| Score | Rating | Action |
|-------|--------|--------|
| 0-25% | Critical | Immediate remediation — regulatory risk |
| 26-50% | Developing | 90-day improvement plan required |
| 51-75% | Managed | Optimize and automate weak areas |
| 76-100% | Optimized | Maintain and benchmark against peers |

## Domain 1: Data Quality Controls

1. Data profiling automation (duplicate detection, format validation)
2. Quality dashboards with SLA thresholds
3. Root cause analysis for quality failures
4. Stewardship program (assigned data owners per domain)
5. Quality gates in data pipelines (reject bad data at ingestion)
6. Business rule validation (domain-specific logic checks)
7. Cross-system reconciliation (source vs target matching)
8. Quality trend tracking (month-over-month improvement metrics)

## Domain 2: Data Cataloging Controls

1. Automated asset discovery (databases, APIs, files, SaaS)
2. Business glossary with agreed definitions
3. Data lineage tracking (source → transformation → consumption)
4. Search and discovery interface for business users
5. Metadata enrichment (tags, classifications, sensitivity labels)
6. Catalog coverage tracking (% of assets documented)
7. Usage analytics (who accesses what, how often)
8. Integration with BI/analytics tools (catalog-aware queries)

## Domain 3: Access Control

1. Role-based access control (RBAC) with regular review
2. Data classification enforcement (labels drive permissions)
3. Least privilege principle (minimal default access)
4. Access request and approval workflows
5. Privileged access management (admin accounts monitored)
6. Access certification (quarterly re-certification of permissions)
7. Anomaly detection (unusual access patterns flagged)
8. De-provisioning automation (access removed on role change/exit)

## Domain 4: Compliance Mapping

1. Regulation inventory (which laws apply, by geography and industry)
2. Control-to-regulation mapping (which controls satisfy which requirements)
3. Data processing records (Article 30 GDPR / equivalent)
4. Consent management (capture, storage, withdrawal tracking)
5. Data subject rights automation (access, deletion, portability)
6. Cross-border transfer compliance (SCCs, adequacy decisions)
7. Breach notification procedures (72-hour GDPR, state-specific)
8. Regular compliance audits (internal + third-party)

## Domain 5: Retention & Lifecycle

1. Retention schedule by data type (contractual, regulatory, operational)
2. Automated archival pipelines (hot → warm → cold → delete)
3. Legal hold management (litigation preservation)
4. Deletion verification (confirmed purge with audit trail)
5. Storage cost optimization (tiered storage aligned to access patterns)
6. Backup and recovery testing (regular restore drills)
7. Data minimization enforcement (collect only what is needed)
8. End-of-life procedures for decommissioned systems

## Domain 6: AI/Agent Data Governance

1. Training data provenance tracking (source, consent, bias review)
2. Model input/output logging (what went in, what came out)
3. PII detection and masking in agent workflows
4. Hallucination monitoring (output accuracy validation)
5. Agent decision audit trail (explainability for automated decisions)
6. Data feedback loops (human review of agent data modifications)
7. Vendor data sharing agreements (what third-party APIs see your data)
8. Synthetic data policies (when and how to use generated data)

## Cost of Poor Governance

| Risk | Average Cost | Prevention Cost |
|------|-------------|-----------------|
| GDPR fine | $4.3M (average 2025) | $45K-$120K/year |
| Data breach | $4.88M (IBM 2025) | $60K-$200K/year |
| Failed audit | $150K-$500K remediation | $30K-$80K/year |
| Bad data decisions | 15-25% revenue impact | $20K-$60K/year |
| AI bias incident | $2M-$50M (litigation + brand) | $25K-$75K/year |

## Remediation Priority Matrix

Always fix in this order:
1. **Compliance gaps** — regulatory fines are existential
2. **Access control** — breaches destroy trust overnight
3. **AI governance** — fastest-growing risk category
4. **Data quality** — garbage in = garbage out at scale
5. **Cataloging** — you cannot govern what you cannot find
6. **Retention** — storage costs compound, legal risk accumulates

## Industry Benchmarks (2026)

| Industry | Avg Governance Score | Top Quartile | Regulatory Pressure |
|----------|---------------------|-------------|-------------------|
| Financial Services | 68% | 85%+ | Extreme (SOX, PCI, GDPR) |
| Healthcare | 62% | 80%+ | High (HIPAA, FDA, state) |
| SaaS/Tech | 55% | 78%+ | Growing (SOC 2, GDPR, CCPA) |
| Manufacturing | 45% | 70%+ | Moderate (ITAR, ISO) |
| Retail/Ecommerce | 48% | 72%+ | Growing (PCI, CCPA, GDPR) |

## Next Steps

Need a complete data governance implementation tailored to your industry?

- [Calculate your AI revenue leak](https://afrexai-cto.github.io/ai-revenue-calculator/)
- [Industry context packs — $47 each](https://afrexai-cto.github.io/context-packs/)
- [Agent setup wizard](https://afrexai-cto.github.io/agent-setup/)
