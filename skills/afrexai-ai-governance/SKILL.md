# AI Governance Policy Builder

Build internal AI governance policies from scratch. Covers acceptable use, model selection, data handling, vendor contracts, compliance mapping, and board reporting.

## When to Use
- Writing or reviewing internal AI acceptable use policies
- Establishing AI governance committees or review boards
- Mapping AI usage to regulatory frameworks (EU AI Act, NIST, ISO 42001)
- Evaluating vendor AI terms and liability clauses
- Preparing board-level AI governance reports

## Governance Policy Framework

### 1. Acceptable Use Policy (AUP)

Every organization running AI needs a written AUP covering:

**Permitted Uses**
- List approved AI tools by department and function
- Define data classification tiers (public, internal, confidential, restricted)
- Map which data tiers can enter which AI systems
- Specify approved vendors vs. shadow AI (employees using personal ChatGPT accounts)

**Prohibited Uses**
- Customer PII in non-SOC2 models without anonymization
- Autonomous financial decisions above $[threshold] without human review
- HR screening/scoring without bias audit documentation
- Any use violating sector regulations (HIPAA, GDPR, SOX, PCI-DSS)

**Shadow AI Detection**
| Signal | Risk Level | Action |
|--------|-----------|--------|
| API calls to unknown AI endpoints | HIGH | Block + investigate |
| Browser extensions with AI features | MEDIUM | Audit + approve/deny |
| Personal accounts on company devices | MEDIUM | Policy reminder + monitor |
| Exported data to AI training sets | CRITICAL | Immediate review |

### 2. AI Model Selection & Procurement

**Evaluation Scorecard (100 points)**

| Criteria | Weight | What to Check |
|----------|--------|---------------|
| Data residency & sovereignty | 20 | Where is data processed? Stored? Can you choose region? |
| Security certifications | 20 | SOC2 Type II, ISO 27001, HIPAA BAA, FedRAMP |
| Model transparency | 15 | Training data provenance, bias testing, version control |
| Contract terms | 15 | Data usage rights, indemnification, SLA, exit clauses |
| Performance & cost | 15 | Latency, accuracy benchmarks, token pricing, rate limits |
| Integration & support | 15 | API stability, documentation quality, support SLA |

**Minimum score for production deployment: 70/100**

**Red Flags (automatic disqualification):**
- Vendor trains on your data without opt-out
- No data processing agreement (DPA) available
- Indemnification excluded for AI outputs
- No incident response SLA

### 3. Data Handling & Classification

**AI Data Flow Audit Template**

For each AI integration, document:
1. **Input data**: What goes in? Classification tier? PII present?
2. **Processing**: Where? Which model? Hosted or API? Region?
3. **Output data**: What comes out? Stored where? Retention period?
4. **Training**: Does vendor use your data for training? Opt-out confirmed?
5. **Logging**: Are prompts/responses logged? Where? Who has access?
6. **Deletion**: Can you request data deletion? Verified how?

**Data Minimization Checklist**
- [ ] Only send minimum necessary data to AI systems
- [ ] Strip PII before processing where possible
- [ ] Use synthetic data for testing and development
- [ ] Implement input sanitization for prompt injection prevention
- [ ] Audit output for data leakage (model regurgitating training data)

### 4. Regulatory Compliance Mapping

**EU AI Act (effective Aug 2025, enforcement Feb 2025)**

| Risk Category | Examples | Requirements |
|--------------|----------|-------------|
| Unacceptable | Social scoring, real-time biometric ID (most cases) | Banned |
| High-risk | HR screening, credit scoring, medical devices | Conformity assessment, human oversight, transparency |
| Limited | Chatbots, deepfakes | Transparency obligations (disclose AI use) |
| Minimal | Spam filters, game AI | No requirements |

**NIST AI RMF (Risk Management Framework)**
- Map: Identify AI systems in use
- Measure: Quantify risks per system
- Manage: Implement controls proportional to risk
- Govern: Establish oversight structure and accountability

**ISO 42001 (AI Management System)**
- Useful for organizations wanting certified AI governance
- Aligns with ISO 27001 (already have it? Easier path)
- Covers: AI policy, risk assessment, objectives, competence, documentation

### 5. AI Governance Committee Structure

**Recommended Composition**
- Chair: CTO or Chief AI Officer
- Legal: 1 representative (contracts, compliance)
- Security: CISO or delegate (data protection, incident response)
- Business: 1-2 department heads (use case prioritization)
- Ethics: External advisor or designated internal role
- Finance: CFO delegate (budget, ROI tracking)

**Meeting Cadence**
- Monthly: Review new AI use cases, vendor changes, incidents
- Quarterly: Policy updates, compliance audit, budget review
- Annually: Full governance framework review, board report

**Decision Authority**
| Decision | Authority Level |
|----------|----------------|
| New AI tool (< $5K/year) | Department head + security review |
| New AI tool (> $5K/year) | Governance committee approval |
| Customer-facing AI | Committee + legal + CEO sign-off |
| AI incident response | Security lead (immediate) → Committee (48h review) |

### 6. Vendor Contract Checklist

Before signing any AI vendor contract, confirm:

- [ ] Data processing agreement (DPA) signed
- [ ] Your data is NOT used for model training (or explicit opt-out confirmed)
- [ ] Data residency requirements met (specify regions)
- [ ] Indemnification clause covers AI-generated output liability
- [ ] SLA includes uptime, latency, and support response time
- [ ] Exit clause: data export format, deletion timeline, transition support
- [ ] Security certifications current and verified (not expired)
- [ ] Incident notification timeline specified (72h or less)
- [ ] Subprocessor list provided with change notification rights
- [ ] Insurance coverage for AI-specific risks confirmed
- [ ] Price lock or cap on increases for contract duration
- [ ] Right to audit (or audit report access)

### 7. Board Reporting Template

**Quarterly AI Governance Report**

```
AI GOVERNANCE REPORT — Q[X] [YEAR]

1. AI PORTFOLIO SUMMARY
   - Active AI systems: [count]
   - New deployments this quarter: [count]
   - Retired/replaced: [count]
   - Total AI spend: $[amount] (vs budget: $[amount])

2. RISK DASHBOARD
   - High-risk systems: [count] — all compliant: [Y/N]
   - Open incidents: [count] — resolved this quarter: [count]
   - Shadow AI detections: [count] — remediated: [count]
   - Compliance gaps: [list]

3. VALUE DELIVERED
   - Hours saved: [estimate]
   - Revenue attributed to AI: $[amount]
   - Cost reduction: $[amount]
   - Customer satisfaction impact: [metric]

4. KEY DECISIONS NEEDED
   - [Decision 1: context + recommendation]
   - [Decision 2: context + recommendation]

5. NEXT QUARTER PRIORITIES
   - [Priority 1]
   - [Priority 2]
```

### 8. Incident Response for AI Systems

**AI-Specific Incident Categories**

| Category | Example | Response Time |
|----------|---------|---------------|
| Data breach via AI | Model leaks PII in output | Immediate — invoke security IR plan |
| Hallucination causing harm | Wrong medical/legal/financial advice acted on | 4h — document, notify affected parties |
| Bias detected | Discriminatory output in hiring/lending | 24h — suspend system, audit, remediate |
| Prompt injection | Attacker manipulates AI behavior | Immediate — block vector, patch |
| Cost overrun | Runaway API calls | 4h — rate limit, investigate, cap |
| Vendor incident | Provider breach or outage | Per vendor SLA — activate backup |

**Post-Incident Review Template**
1. What happened (factual timeline)
2. Impact (who/what affected, cost, duration)
3. Root cause (not blame — systems thinking)
4. Fixes applied (immediate + permanent)
5. Policy/process changes needed
6. Board notification required? (Y/N + rationale)

## Cost of NOT Having AI Governance

| Company Size | Annual Risk Without Governance |
|-------------|-------------------------------|
| 15-50 employees | $50K-$200K (shadow AI waste, compliance fines) |
| 50-200 employees | $200K-$800K (data incidents, vendor lock-in, redundant tools) |
| 200-1000 employees | $800K-$3M (regulatory penalties, IP exposure, audit failures) |
| 1000+ employees | $3M-$15M+ (class action, regulatory enforcement, reputational damage) |

## 90-Day Implementation Roadmap

**Month 1: Foundation**
- Draft acceptable use policy
- Inventory all AI systems in use (including shadow AI)
- Classify data flowing through each system
- Identify governance committee members

**Month 2: Controls**
- Finalize and distribute AUP
- Implement vendor evaluation scorecard for new purchases
- Set up AI incident response procedures
- Begin regulatory compliance mapping

**Month 3: Operationalize**
- First governance committee meeting
- Deliver first board report
- Establish monitoring for shadow AI
- Schedule quarterly policy review cycle

---

*Built by AfrexAI — AI operations infrastructure for mid-market companies.*

Get the full industry-specific context pack for your sector ($47): https://afrexai-cto.github.io/context-packs/

Calculate your AI automation ROI: https://afrexai-cto.github.io/ai-revenue-calculator/

Set up your AI agent workforce in 5 minutes: https://afrexai-cto.github.io/agent-setup/

Need all 10 industry packs? $197 for the complete bundle: https://buy.stripe.com/aEUaGJ2Xd0rI6zKfZ7
