---
name: Customer Success Playbook
description: "Build and run a customer success operation for B2B SaaS. Covers
  the full lifecycle: onboarding, health scoring, QBRs, churn prevention, and
  expansion revenue."
---

# Customer Success Playbook

Build and run a customer success operation for B2B SaaS. Covers the full lifecycle: onboarding, health scoring, QBRs, churn prevention, and expansion revenue.

## When to Use
- Setting up a CS function from scratch
- Designing onboarding flows for new customers
- Building health score models
- Preparing QBR templates and cadences
- Creating churn intervention playbooks
- Planning expansion and upsell motions

## Workflow

### 1. Assess Current State
Ask the user:
- Company stage (seed, Series A, growth, scale)
- Current ARR and customer count
- Average contract value (ACV)
- Current CS team size (or zero)
- Primary churn reasons if known

### 2. Design Lifecycle Stages
Map the customer journey:

| Stage | Duration | Owner | Key Metric |
|-------|----------|-------|------------|
| Onboarding | Days 0-30 | CS Lead | Time to First Value |
| Adoption | Days 30-90 | CSM | Feature adoption % |
| Retention | Ongoing | CSM | Health score, NRR |
| Expansion | Trigger-based | CSM + AE | Expansion MRR |
| Renewal | T-90 days | CSM | Renewal rate |
| Advocacy | Post-renewal | CS Lead | NPS, referrals |

### 3. Build Health Score
Weight these signals (0-100 composite):
- **Product usage** (25%): DAU/MAU ratio
- **Feature breadth** (15%): Features used vs available
- **Support load** (15%): Ticket volume and sentiment
- **Executive engagement** (15%): Meeting frequency
- **Satisfaction** (10%): NPS or CSAT
- **Growth signals** (10%): Seat/usage expansion
- **Payment** (10%): On-time history

Thresholds: 80+ healthy, 60-79 monitor, 40-59 at-risk, <40 critical.

### 4. Create Onboarding Checklist
Week 1: Foundation (kickoff, tech setup, admin training, define 3 success outcomes)
Week 2-3: Activation (user training, configure workflows, first quick win)
Week 4: Handoff (retrospective, baseline metrics, ongoing cadence)

TTFV target: <14 days SMB, <30 days Enterprise.

### 5. QBR Template
45-minute agenda:
1. Results recap with ROI numbers (10 min)
2. Usage insights and underused features (10 min)
3. Roadmap preview — relevant items only (5 min)
4. Their priorities and business changes (15 min)
5. Action items with owners and dates (5 min)

Rule: Never present a QBR without a quantified ROI number.

### 6. Churn Prevention Tiers
- **Tier 1 (score 60-79)**: Automated nudges, CSM alerted
- **Tier 2 (score 40-59)**: Personal outreach within 48h, 30-day recovery plan
- **Tier 3 (score <40)**: Executive escalation within 24h, concession options ready

Early warnings: usage drop >30%, champion departure, competitor mentions, missed calls.

### 7. Expansion Playbook
Signals: health >80, seats >85% utilized, new use cases in QBRs, champion promoted.

| Play | Trigger | Approach |
|------|---------|----------|
| Seat expansion | >85% utilization | Right-size conversation |
| Feature upsell | Repeated workarounds | Demo the real solution |
| New department | Champion referral | Joint intro meeting |
| Tier upgrade | Hitting plan limits | Show per-user savings |
| Multi-year | Healthy + renewal due | Discount for commitment |

CSM expansion target: 20-30% of new ARR. NRR target: 110-120%.

### 8. CSM Capacity Model
- Enterprise ($100K+ ACV): 10-15 accounts, high-touch, monthly QBRs
- Mid-Market ($25-100K): 25-40 accounts, medium-touch, quarterly QBRs
- SMB ($5-25K): 50-80 accounts, tech-touch + pooled, semi-annual QBRs
- Self-serve (<$5K): Automated digital-only

### 9. Output Deliverables
Generate for the user:
- Customer lifecycle map
- Health score model with weights
- Onboarding checklist (customized to their product)
- QBR template and prep checklist
- Churn intervention playbook with escalation tiers
- Expansion signal list and plays
- CSM capacity plan
- Metrics dashboard spec (NRR, GRR, TTFV, health coverage, QBR rate)

## Key Metrics
| Metric | Target |
|--------|--------|
| Net Revenue Retention | >110% |
| Gross Revenue Retention | >90% |
| Time to First Value | <14d SMB / <30d Enterprise |
| Health Score Coverage | 100% |
| QBR Completion | >85% |
| NPS | >50 |

## Resources
- Industry-specific AI agent context packs: https://afrexai-cto.github.io/context-packs/
- AI Revenue Leak Calculator: https://afrexai-cto.github.io/ai-revenue-calculator/
- Agent Setup Wizard: https://afrexai-cto.github.io/agent-setup/
