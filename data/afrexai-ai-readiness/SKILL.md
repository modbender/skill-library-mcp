---
name: AI Readiness Assessment
description: Run a structured AI readiness audit for any organization. Scores 8
  dimensions, identifies gaps, produces a prioritized 90-day action plan with
  budget ranges.
---

# AI Readiness Assessment

Run a structured AI readiness audit for any organization. Scores 8 dimensions, identifies gaps, produces a prioritized 90-day action plan with budget ranges.

## When to Use
- Before investing in AI/automation tools
- Board or leadership requesting AI strategy
- Evaluating build vs buy decisions
- Annual technology planning

## How It Works

Score each dimension 1-5 (1=not started, 5=optimized):

### 1. Data Infrastructure (Weight: 3x)
- [ ] Centralized data warehouse or lakehouse operational
- [ ] Data quality monitoring automated (freshness, completeness, accuracy)
- [ ] API-first architecture for core systems
- [ ] Data governance policy documented and enforced
- [ ] PII/PHI classification and access controls active

**Score 1:** Spreadsheets and siloed databases
**Score 3:** Warehouse exists, some pipelines automated
**Score 5:** Real-time streaming, quality >99%, full lineage

### 2. Process Documentation (Weight: 2x)
- [ ] Top 20 revenue-impacting processes mapped end-to-end
- [ ] Decision trees documented for each process
- [ ] Exception handling paths defined
- [ ] Time-per-task benchmarks established
- [ ] Process owners assigned

**Score 1:** Tribal knowledge, nothing written down
**Score 3:** Major processes documented, some outdated
**Score 5:** Living documentation, updated quarterly, covers 80%+ of operations

### 3. Technical Talent (Weight: 2x)
- [ ] At least 1 person understands ML/AI concepts at implementation level
- [ ] Engineering team comfortable with APIs and integrations
- [ ] DevOps/infrastructure person can deploy and monitor services
- [ ] Data analyst can query and interpret model outputs
- [ ] Security team understands AI-specific attack surfaces

**Score 1:** No technical staff beyond basic IT
**Score 3:** Good engineering team, AI knowledge is theoretical
**Score 5:** Dedicated AI/ML engineer, cross-functional AI literacy program

### 4. Budget & ROI Framework (Weight: 2x)
- [ ] AI budget allocated (not pulled from "innovation" slush fund)
- [ ] ROI measurement criteria defined before project starts
- [ ] Kill criteria established (when to stop a failing project)
- [ ] Total cost of ownership model includes maintenance, retraining, monitoring
- [ ] Benchmarks set against current manual process costs

**Budget Reality by Company Size:**
| Company Size | Year 1 Investment | Expected ROI Timeline |
|---|---|---|
| 15-50 employees | $24K-$80K | 4-8 months |
| 50-200 employees | $80K-$300K | 3-6 months |
| 200-1000 employees | $300K-$1.2M | 6-12 months |
| 1000+ employees | $1.2M-$5M+ | 8-18 months |

### 5. Change Management (Weight: 1.5x)
- [ ] Executive sponsor identified and actively involved
- [ ] Communication plan for affected teams drafted
- [ ] Training budget allocated
- [ ] Pilot team identified (volunteers, not voluntolds)
- [ ] Success metrics shared openly with organization

**Score 1:** Leadership says "just do AI" with no plan
**Score 3:** Exec sponsor exists, some team buy-in
**Score 5:** Change management playbook active, regular town halls, feedback loops

### 6. Security & Compliance (Weight: 2.5x)
- [ ] AI-specific data handling policy written
- [ ] Vendor security assessment process includes AI criteria
- [ ] Model output logging and audit trail planned
- [ ] Regulatory requirements mapped (GDPR, HIPAA, SOX, SOC 2, EU AI Act)
- [ ] Incident response plan covers AI failures

**Score 1:** No AI-specific security considerations
**Score 3:** General security strong, AI gaps identified
**Score 5:** AI governance framework active, regular audits, compliance automated

### 7. Integration Readiness (Weight: 1.5x)
- [ ] Core systems have APIs (CRM, ERP, HRIS, etc.)
- [ ] Authentication/authorization supports service accounts
- [ ] Webhook or event-driven architecture available
- [ ] Test/staging environment mirrors production
- [ ] Rollback procedures documented

**Score 1:** Legacy systems, no APIs, manual data entry
**Score 3:** Major systems have APIs, some manual bridges
**Score 5:** API-first architecture, event-driven, CI/CD for integrations

### 8. Strategic Alignment (Weight: 1x)
- [ ] AI initiatives map to specific business objectives (not "innovation")
- [ ] 3-year technology roadmap includes AI milestones
- [ ] Competitive landscape analysis includes AI adoption by rivals
- [ ] Board/leadership educated on AI capabilities and limitations
- [ ] Failure tolerance defined (acceptable experiment failure rate)

**Score 1:** AI is a buzzword, no concrete strategy
**Score 3:** Strategy exists, loosely connected to business goals
**Score 5:** AI embedded in strategic plan, quarterly reviews, competitive moat building

## Scoring

**Weighted Total = Sum of (Score × Weight) / Max Possible × 100**

| Range | Rating | Recommendation |
|---|---|---|
| 0-25 | 🔴 Not Ready | Fix foundations first. 6-12 months of groundwork before AI projects. |
| 26-50 | 🟡 Early Stage | Pick ONE high-impact, low-risk pilot. Build muscle. |
| 51-75 | 🟢 Ready | Deploy 2-3 agents in validated use cases. Scale what works. |
| 76-100 | 🔵 Advanced | Multi-agent deployment, autonomous operations, competitive moat. |

## 90-Day Action Plan Template

**Days 1-30: Foundation**
- Complete this assessment with honest scores
- Document top 5 processes by time spent × error rate
- Audit data infrastructure gaps
- Set budget and kill criteria

**Days 31-60: Pilot**
- Select highest-scoring use case (high data readiness + clear ROI)
- Deploy single agent or automation
- Measure daily: time saved, error rate, cost
- Weekly review with stakeholders

**Days 61-90: Scale or Kill**
- If pilot ROI > 2x: plan 2 more deployments
- If pilot ROI < 1x: diagnose root cause, pivot or kill
- Document learnings regardless of outcome
- Update 3-year roadmap based on reality

## 7 Assessment Mistakes

1. **Scoring yourself too high** — External validation beats internal optimism
2. **Ignoring data quality** — AI on bad data = faster wrong answers
3. **Skipping change management** — Technical success + team rejection = failure
4. **No kill criteria** — Zombie projects drain budget and credibility
5. **Buying before understanding** — Tool purchases before process documentation = shelfware
6. **Ignoring security until audit** — Retrofitting AI security costs 3-5x more than building it in
7. **Comparing to tech companies** — Your readiness bar is YOUR industry, not Silicon Valley

## Industry Benchmarks (2026)

| Industry | Avg Score | Top Quartile | First AI Win |
|---|---|---|---|
| Fintech | 62 | 78+ | Fraud detection, KYC |
| Healthcare | 41 | 58+ | Clinical documentation, scheduling |
| Legal | 38 | 52+ | Contract review, research |
| Construction | 29 | 44+ | Safety monitoring, estimation |
| Ecommerce | 58 | 74+ | Personalization, inventory |
| SaaS | 65 | 82+ | Support, onboarding, churn prediction |
| Real Estate | 35 | 48+ | Lead scoring, valuation |
| Recruitment | 45 | 62+ | Screening, outreach |
| Manufacturing | 42 | 56+ | QC, predictive maintenance |
| Professional Services | 48 | 64+ | Proposal generation, time tracking |

---

**Get your industry-specific context pack ($47) →** https://afrexai-cto.github.io/context-packs/

**Calculate your AI revenue leak →** https://afrexai-cto.github.io/ai-revenue-calculator/

**Set up your first AI agent →** https://afrexai-cto.github.io/agent-setup/

**Bundles:** Pick 3 for $97 | All 10 for $197 | Everything Pack $247
