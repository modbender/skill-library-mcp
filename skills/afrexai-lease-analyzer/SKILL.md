---
name: Commercial Lease Analyzer
description: Analyze commercial leases (office, retail, industrial, warehouse)
  for hidden costs, unfavorable terms, and negotiation leverage. Use when
  reviewing a new lease, renegotiating a renewal, or comparin...
---

# Commercial Lease Analyzer

Analyze commercial leases (office, retail, industrial, warehouse) for hidden costs, unfavorable terms, and negotiation leverage. Use when reviewing a new lease, renegotiating a renewal, or comparing multiple lease options.

## When to Use
- Signing a new commercial lease
- Lease renewal negotiation
- Comparing multiple lease proposals
- Auditing existing lease for cost reduction
- Subleasing or assignment analysis

## What You Need from the User
1. **Lease type**: Office, retail, industrial, warehouse, mixed-use
2. **Lease terms**: Base rent, term length, renewal options
3. **Cost structure**: NNN, modified gross, full-service gross
4. **Square footage**: Usable vs rentable (load factor)
5. **Location/market**: City, submarket (for comp analysis)

## Analysis Framework

### 1. Cost Breakdown (True Occupancy Cost)
```
Base Rent ($/SF/yr)
+ CAM Charges (Common Area Maintenance)
+ Property Tax Pass-Through
+ Insurance Pass-Through
+ Utility Estimates
+ Parking Costs
+ Janitorial (if not included)
= Total Occupancy Cost ($/SF/yr)
÷ 12 = Monthly Cost
× Term = Total Lease Liability
```

### 2. Load Factor Analysis
```
Rentable SF ÷ Usable SF = Load Factor
Industry benchmarks:
- Class A Office: 1.15-1.20 (15-20% common area)
- Class B Office: 1.12-1.18
- Retail: 1.05-1.10
- Industrial: 1.02-1.05

Flag if load factor > benchmark. Every 1% = real money.
Example: 5,000 USF at 1.20 = paying for 6,000 RSF
At $30/SF = $30,000/yr for hallways and lobbies
```

### 3. Escalation Modeling
Project total cost over full term including:
- **Fixed increases**: 3% annual is standard. Flag >3.5%
- **CPI-linked**: Model at 2.5%, 4%, 6% scenarios
- **Market reset**: Compare to projected market rents
- **CAM escalation caps**: If uncapped, model 5-8% annual increases

Output a year-by-year cost table showing base rent, estimated CAM, total cost.

### 4. Critical Clause Review

**Red Flags** (flag immediately):
- Personal guarantee without sunset clause
- Demolition clause (landlord can terminate for redevelopment)
- Radius restriction >3 miles (retail)
- Continuous operation clause without co-tenancy protection
- Uncapped CAM with no audit rights
- Relocation clause (landlord can move you)
- No assignment/sublease rights
- Holdover rate >150% of final rent

**Yellow Flags** (negotiate):
- No rent abatement for construction delays
- No exclusive use clause (retail)
- HVAC maintenance fully on tenant
- No cap on controllable operating expenses
- Restoration clause requiring original condition
- No early termination option after year 3-5
- Insurance requirements above standard

**Green (Standard/Favorable):**
- TI allowance ($30-60/SF office, $15-30 retail)
- Free rent period (1 month per year of term)
- Right of first refusal on adjacent space
- Renewal option at fair market value
- CAM audit rights
- Assignment rights with reasonable consent

### 5. Negotiation Leverage Points
Based on market conditions, identify:
- **Tenant's market** (vacancy >15%): Push for higher TI, more free rent, lower escalations
- **Landlord's market** (vacancy <8%): Focus on caps, flexibility clauses, termination rights
- **Balanced** (8-15%): Standard negotiations, pick 3-4 priorities

Rank negotiation items by dollar impact over lease term.

### 6. Comparison Matrix (Multiple Options)
If comparing leases, output a side-by-side table:
| Factor | Option A | Option B | Option C |
|--------|----------|----------|----------|
| Effective Rent ($/SF) | | | |
| Total 5-Year Cost | | | |
| TI Allowance | | | |
| Free Rent (months) | | | |
| Escalation Type/Rate | | | |
| Termination Option | | | |
| Load Factor | | | |
| Parking Ratio | | | |

### 7. Financial Impact Summary
- Total lease liability (ASC 842 / IFRS 16)
- NPV of all lease payments (discount at 6-8%)
- Break-even occupancy cost per employee
- Cost per revenue dollar (if revenue data provided)

## Output Format
```
LEASE ANALYSIS: [Property Address]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

VERDICT: [FAVORABLE / NEGOTIATE / WALK AWAY]

TRUE COST
Monthly: $XX,XXX
Annual: $XXX,XXX
Full Term: $X,XXX,XXX
Per Employee: $X,XXX/mo (at XX headcount)

RED FLAGS: [count]
[List with dollar impact]

TOP 3 NEGOTIATION PRIORITIES:
1. [Item] — potential savings: $XX,XXX over term
2. [Item] — potential savings: $XX,XXX over term
3. [Item] — potential savings: $XX,XXX over term

YEAR-BY-YEAR PROJECTION:
[Table]
```

## Industry Benchmarks (2025-2026)
| Market | Office ($/SF) | Retail ($/SF) | Industrial ($/SF) |
|--------|--------------|---------------|-------------------|
| NYC | $65-85 | $80-200+ | $18-25 |
| SF/Bay | $55-75 | $45-80 | $15-22 |
| LA | $40-55 | $35-65 | $14-20 |
| Chicago | $28-42 | $25-50 | $8-12 |
| Dallas | $25-38 | $22-40 | $6-10 |
| Miami | $42-58 | $40-75 | $12-16 |
| Atlanta | $25-35 | $20-38 | $6-9 |
| Denver | $28-40 | $22-38 | $8-12 |
| Austin | $35-48 | $28-45 | $10-14 |
| National Avg | $32-45 | $25-45 | $8-14 |

TI allowances: $30-60/SF (office), $15-30/SF (retail), $5-15/SF (industrial)
Free rent: 1 month per year of term is standard in balanced markets

---

*Built by [AfrexAI](https://afrexai-cto.github.io/context-packs/) — AI agents that actually know your industry. Browse our [context packs](https://afrexai-cto.github.io/context-packs/) for deep vertical expertise.*
