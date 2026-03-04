# Medical Billing & Revenue Cycle Management

Analyze medical billing workflows, identify revenue leaks, optimize claim submissions, and reduce denial rates. Built for healthcare practices, billing companies, and revenue cycle teams.

## What This Covers

### CPT/ICD-10 Coding Accuracy
- Common coding errors by specialty (top 10 per specialty)
- Modifier usage: 25, 59, 76, 77, AI, AS — when required vs when it triggers audit
- E/M level selection (2021 guidelines): time-based vs MDM-based
- Evaluation matrix: does documentation support the code billed?

### Claim Denial Analysis
- Denial reason code lookup (CARC/RARC codes)
- Top 20 denial reasons across commercial + Medicare + Medicaid
- Root cause mapping: front-desk error, coding error, clinical documentation, payer policy
- Appeal letter framework by denial type (with timelines)
- Clean claim rate benchmark: 95%+ target

### Revenue Cycle KPIs
| Metric | Target | Red Flag |
|--------|--------|----------|
| Days in A/R | <35 | >50 |
| Clean claim rate | >95% | <90% |
| First-pass resolution | >90% | <80% |
| Denial rate | <5% | >10% |
| Collection rate | >95% | <90% |
| Cost to collect | <4% | >7% |
| Net collection rate | >96% | <92% |

### Payer Contract Analysis
- Fee schedule comparison: Medicare vs commercial rates by CPT
- Allowed amount benchmarking (what you should be getting paid)
- Underpayment detection: compare ERA/835 to contracted rates
- Rate negotiation prep: volume data, market rates, quality metrics

### Compliance & Audit Readiness
- OIG Work Plan items relevant to your specialty
- Stark Law / Anti-Kickback safe harbors checklist
- False Claims Act risk factors
- Internal audit sampling methodology (statistically valid)
- Documentation improvement programs (CDI)

### Charge Capture Optimization
- Missed charge identification by department
- Charge lag analysis (days from service to charge entry)
- Superbill/encounter form design best practices
- Common missed revenue: vaccines, injections, supplies, time-based codes

### Patient Financial Responsibility
- Eligibility verification workflow (real-time vs batch)
- Prior authorization tracking and requirements by payer
- Patient estimate generation (good faith estimate compliance)
- Collections strategy: statements → calls → agency threshold
- No Surprises Act compliance checklist

## Usage

Give the agent your:
- **Specialty** (orthopedics, cardiology, primary care, etc.)
- **Payer mix** (% Medicare, Medicaid, commercial, self-pay)
- **Current KPIs** (denial rate, days in A/R, collection rate)
- **Problem area** (denials, underpayments, coding, compliance)

The agent will analyze against benchmarks and give specific, actionable recommendations.

## Example Prompts

- "Our orthopedic practice has a 12% denial rate. Top reasons are CO-4 and CO-16. Analyze root causes."
- "Compare our cardiology fee schedule to Medicare rates for our top 20 CPTs."
- "Build an appeal letter for a CO-197 denial on CPT 99214 with modifier 25."
- "Audit our E/M coding distribution — we're billing 80% level 3. Is that normal for family medicine?"
- "Our days in A/R jumped from 32 to 48 in two months. What should we investigate?"

## Industry Context

Medical billing errors cost US healthcare $935 million per week. The average practice loses 5-10% of revenue to preventable billing issues. Denial management alone can recover 2-5% of net revenue when done right.

---

Built by [AfrexAI](https://afrexai-cto.github.io/context-packs/) — AI agent context packs for regulated industries. Get the full Healthcare AI Context Pack with 50+ frameworks at our [storefront](https://afrexai-cto.github.io/context-packs/).
