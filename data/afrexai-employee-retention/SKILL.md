---
name: Employee Retention & Turnover Risk Analyzer
description: Diagnose why people leave. Fix it before they do.
---

# Employee Retention & Turnover Risk Analyzer

Diagnose why people leave. Fix it before they do.

## What This Does

Runs a structured retention risk assessment across 8 dimensions, scores each 0-100, identifies flight-risk employees and departments, calculates replacement costs, and generates a 90-day action plan.

## 8 Retention Dimensions

1. **Compensation Competitiveness** — market benchmarking, pay equity, total comp analysis
2. **Career Progression** — promotion velocity, skill development, internal mobility
3. **Manager Quality** — span of control, 1:1 frequency, team tenure under each manager
4. **Workload Balance** — overtime patterns, PTO usage, burnout indicators
5. **Culture & Belonging** — eNPS trends, DEI metrics, team cohesion signals
6. **Recognition & Feedback** — frequency, quality, peer-to-peer vs top-down
7. **Flexibility & Autonomy** — remote policy, schedule control, decision authority
8. **Onboarding & Early Tenure** — 90-day attrition, ramp time, buddy program effectiveness

## How to Use

Give the agent your team data (headcount, tenure distribution, recent departures, eNPS scores, comp bands) and it will:

1. Score each dimension 0-100
2. Flag dimensions below 60 as critical
3. Calculate cost-of-turnover by role level:
   - Entry level: 50-60% of salary
   - Mid level: 75-100% of salary
   - Senior/specialist: 100-150% of salary
   - Executive: 200-400% of salary
4. Identify top 3 retention levers (highest ROI interventions)
5. Generate 90-day retention action plan with owner assignments

## Replacement Cost Formula

```
Replacement Cost = (Recruiting fees + Lost productivity + Training + Ramp time) × Role multiplier

Quick estimate:
- $65K role → $39K-$65K replacement cost
- $120K role → $90K-$180K replacement cost  
- $200K role → $200K-$800K replacement cost
```

## 2026 Retention Benchmarks

| Metric | Good | Average | Poor |
|--------|------|---------|------|
| Annual voluntary turnover | <10% | 10-18% | >18% |
| 90-day new hire attrition | <5% | 5-12% | >12% |
| eNPS | >40 | 10-40 | <10 |
| Avg tenure | >3yr | 1.5-3yr | <1.5yr |
| Internal mobility rate | >15% | 8-15% | <8% |
| Manager quality score | >80 | 60-80 | <60 |

## Industry Turnover Rates (2026)

| Industry | Avg Voluntary Turnover | Top Quartile |
|----------|----------------------|--------------|
| Tech/SaaS | 13.2% | 8.1% |
| Financial Services | 12.8% | 7.4% |
| Healthcare | 19.5% | 11.2% |
| Retail/Ecommerce | 24.1% | 14.8% |
| Manufacturing | 14.7% | 9.3% |
| Professional Services | 16.3% | 10.1% |
| Construction | 21.4% | 13.6% |
| Legal | 11.9% | 7.2% |
| Real Estate | 15.8% | 9.7% |
| Recruitment/Staffing | 28.3% | 16.9% |

## AI Impact on Retention (2026 Factors)

New retention risks specific to the AI transition:
- **Role anxiety**: 34% of employees report fear of AI replacement (Gallup 2025)
- **Skills obsolescence**: Roles with >60% automatable tasks see 2.3x higher attrition
- **AI tool fatigue**: Teams forced to adopt >3 new AI tools in 6 months show 40% higher burnout
- **Upskilling gap**: Companies investing <2% of payroll in AI training lose senior talent 1.8x faster

Retention plays that work in 2026:
- AI upskilling budgets ($2K-$5K/employee/year)
- Role redesign workshops (quarterly, collaborative not top-down)
- "AI productivity dividends" — share efficiency gains as comp/time off
- Internal AI project rotations

## Red Flags Dashboard

Watch for these combinations:
- eNPS dropping + PTO usage declining = burnout spiral
- Senior departures clustering in one team = manager problem
- Glassdoor sentiment shift + job posting views up = flight risk wave
- Promotion rate <5% + tenure >2yr cohort growing = stagnation crisis

## Output Format

```
RETENTION RISK ASSESSMENT
========================
Overall Score: [X]/100
Risk Level: [LOW/MODERATE/HIGH/CRITICAL]

DIMENSION SCORES:
[Dimension]: [Score]/100 — [Status emoji] [One-line finding]

TOP 3 RISKS:
1. [Risk] — Est. cost if unaddressed: $[X]/year
2. [Risk] — Est. cost if unaddressed: $[X]/year
3. [Risk] — Est. cost if unaddressed: $[X]/year

RECOMMENDED ACTIONS (90-day):
Week 1-2: [Quick wins]
Week 3-6: [Structural changes]
Week 7-12: [Culture/process shifts]

TOTAL ESTIMATED SAVINGS: $[X]/year from reduced turnover
```

## Get the Full Workforce AI Toolkit

This skill covers retention diagnostics. For the complete workforce transformation stack — AI readiness assessment, role redesign, hiring optimization, and productivity benchmarking:

- **SaaS Context Pack**: https://afrexai-cto.github.io/context-packs/ ($47)
- **AI Revenue Calculator**: https://afrexai-cto.github.io/ai-revenue-calculator/
- **Agent Setup Wizard**: https://afrexai-cto.github.io/agent-setup/
- **Pick 3 Bundle**: https://buy.stripe.com/... ($97)
- **All 10 Packs**: https://buy.stripe.com/... ($197)

Built by AfrexAI — turning AI into revenue since 2025.
