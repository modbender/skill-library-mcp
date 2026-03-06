---
name: Payroll Compliance Auditor
description: Run a full payroll audit in under 10 minutes. Catches the errors
  that cost companies $845 per violation.
---

# Payroll Compliance Auditor

Run a full payroll audit in under 10 minutes. Catches the errors that cost companies $845 per violation.

## What It Does
- Classifies workers (W-2 vs 1099) using the IRS 20-factor test
- Audits overtime calculations against FLSA rules
- Checks tax withholding accuracy (federal, state, local)
- Flags misclassification risk with dollar-amount exposure estimates
- Generates quarterly compliance checklists
- Produces audit-ready reports for DOL or state agency reviews

## How to Use

Tell your agent:

**Full payroll audit:**
"Run a payroll compliance audit for [company]. We have [X] employees across [states]. Pay frequency is [weekly/biweekly/monthly]."

**Worker classification check:**
"Check if these roles should be W-2 or 1099: [list roles with descriptions]."

**Overtime audit:**
"Audit overtime compliance. Our employees work [schedule]. We're in [state]. Current OT policy: [describe]."

**Tax withholding review:**
"Review tax withholding setup for employees in [states]. We use [payroll provider]."

## Audit Framework

### 1. Worker Classification (IRS 20-Factor Test)
Score each worker across three categories:
- **Behavioral Control** (6 factors): Instructions, training, integration, personal services, hiring assistants, work hours
- **Financial Control** (5 factors): Business expenses, investment, profit/loss opportunity, market availability, method of payment
- **Relationship Type** (4 factors): Written contracts, benefits, permanency, key services

**Risk levels:**
- 0-4 factors toward employee → Low risk (likely contractor)
- 5-9 factors → Medium risk (review needed)
- 10+ factors → High risk (likely misclassified)

**Penalty exposure per misclassified worker:**
- Back employment taxes: 15.3% of wages
- FLSA overtime liability: up to 3 years back pay
- Benefits liability: retirement, health, PTO
- IRS penalties: $50-$260 per W-2 failure
- State penalties vary: $5K-$25K per violation (CA, NY, MA highest)

### 2. Overtime Compliance (FLSA + State)
Check against federal AND state rules (state wins when more generous):

| Rule | Federal (FLSA) | California | New York | Washington |
|------|---------------|------------|----------|------------|
| OT threshold | 40 hrs/week | 8 hrs/day OR 40/week | 40 hrs/week | 40 hrs/week |
| OT rate | 1.5x | 1.5x (2x after 12 hrs/day) | 1.5x | 1.5x |
| Salary exemption | $58,656/yr (2026) | $66,560/yr | $62,400/yr (NYC) | $67,724.80/yr |
| 7th day rule | None | 1.5x first 8 hrs, 2x after | None | None |

**Common violations:**
- Averaging hours across two weeks (illegal under FLSA)
- Not paying OT on bonuses/commissions
- Misclassifying non-exempt as exempt
- Rounding errors exceeding 7-minute threshold
- Auto-deducting meal breaks not actually taken

### 3. Tax Withholding Accuracy
Verify against current tables:

**Federal:**
- 2026 FICA: 6.2% SS (wage base $174,900) + 1.45% Medicare
- Additional Medicare: 0.9% above $200K single / $250K married
- FUTA: 6.0% first $7,000 (5.4% credit = 0.6% effective)

**State cross-checks:**
- SUI rates (experience-rated — verify annual notice)
- SDI/PFL (CA, NJ, NY, WA, MA, CT, OR, CO, MD)
- Local taxes (NYC, Philadelphia, San Francisco, etc.)
- Reciprocity agreements (employees in different state than work)

### 4. Quarterly Compliance Checklist

**Monthly:**
- [ ] Reconcile payroll register to GL
- [ ] Verify new hire reporting (within 20 days)
- [ ] Check garnishment calculations
- [ ] Review PTO accrual accuracy

**Quarterly:**
- [ ] File Form 941 (federal) by last day of following month
- [ ] File state unemployment reports
- [ ] Reconcile YTD withholdings to pay stubs
- [ ] Review contractor payments approaching $600 threshold
- [ ] Audit benefit deductions against enrollment

**Annual:**
- [ ] W-2 distribution by January 31
- [ ] 1099-NEC filing by January 31
- [ ] ACA reporting (1095-C) by March 2
- [ ] Update salary exemption thresholds
- [ ] Review state minimum wage changes
- [ ] Workers' comp audit preparation

### 5. Audit Report Format

```
PAYROLL COMPLIANCE AUDIT REPORT
Company: [Name]
Period: [Q1/Q2/Q3/Q4 YYYY]
Employees: [Count]
States: [List]
Audit Date: [Date]

EXECUTIVE SUMMARY
Overall Risk Score: [Low/Medium/High/Critical]
Issues Found: [Count]
Estimated Exposure: $[Amount]

FINDINGS
[F-001] [Category] - [Severity]
Description: [What's wrong]
Exposure: $[Amount]
Remediation: [Fix]
Deadline: [Date]

RECOMMENDATIONS
1. [Priority action]
2. [Secondary action]
3. [Long-term improvement]
```

## Cost of Getting It Wrong

| Violation | Average Penalty |
|-----------|----------------|
| Misclassification (per worker) | $12,000-$25,000 |
| FLSA overtime (per employee) | $1,000-$10,000 + back pay |
| Late W-2/1099 filing | $50-$580 per form |
| Failure to deposit taxes | 2%-15% of deposit |
| Willful failure | $100K+ fine + criminal |

The DOL recovered $274M in back wages in 2024. Average investigation finds $1,150 per employee owed.

## Who This Is For
- HR teams without dedicated payroll compliance staff
- Growing companies expanding to new states
- Businesses using contractors heavily (tech, construction, healthcare)
- Anyone who just got a DOL audit letter

---

*Built by [AfrexAI](https://afrexai-cto.github.io/context-packs/) — AI context packs for business operations. Full compliance automation: [$47 Professional Services Pack](https://afrexai-cto.github.io/context-packs/).*

*Calculate what payroll errors are costing you: [AI Revenue Calculator](https://afrexai-cto.github.io/ai-revenue-calculator/)*

*Set up your own compliance agent in 5 minutes: [Agent Setup Wizard](https://afrexai-cto.github.io/agent-setup/)*
