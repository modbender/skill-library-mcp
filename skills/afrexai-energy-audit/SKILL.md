# Energy Audit — Commercial Building Assessment

Run a full energy audit for commercial or industrial facilities. Identifies waste, models savings, and generates a prioritized retrofit roadmap with ROI timelines.

## What It Does

- Collects utility data (electric, gas, water, steam) across 12+ months
- Benchmarks consumption against ASHRAE and ENERGY STAR baselines
- Identifies the top 10 energy conservation measures (ECMs) ranked by payback period
- Calculates simple payback, IRR, and lifecycle cost for each measure
- Generates an ASHRAE Level II audit report with executive summary
- Flags utility rate optimization opportunities (demand response, TOU shifting)
- Maps available rebates and incentive programs by state/region

## How to Use

Tell your agent:
- "Run an energy audit for our 45,000 sq ft office building"
- "Analyze our utility bills and find savings opportunities"
- "Create a retrofit roadmap for our warehouse — budget is $200K"

Provide:
1. **Building type** — office, retail, warehouse, manufacturing, healthcare, education
2. **Square footage** and location (climate zone matters)
3. **12 months of utility bills** (or monthly kWh/therms if summarized)
4. **Operating hours** — shifts, weekend usage, seasonal patterns
5. **Major equipment** — HVAC age/type, lighting, compressed air, process loads

## Audit Framework

### Benchmarking
- EUI (Energy Use Intensity) = total kBtu ÷ sq ft
- Compare against CBECS median by building type
- ENERGY STAR score target: 75+ (top quartile)

### Energy Conservation Measures (ECMs)

| Category | Typical Savings | Payback |
|----------|----------------|---------|
| LED retrofit | 40-60% lighting | 1-3 years |
| HVAC controls/BMS | 15-25% HVAC | 2-4 years |
| VFDs on motors/fans | 20-50% motor | 1-3 years |
| Envelope (insulation, air sealing) | 10-20% heating/cooling | 3-7 years |
| Demand response enrollment | 5-15% peak demand | Immediate |
| Solar PV | 30-70% electric | 5-8 years (with ITC) |
| Heat recovery | 10-30% thermal | 2-5 years |

### Financial Analysis
For each ECM:
- **Simple payback** = cost ÷ annual savings
- **IRR** = internal rate of return over equipment life
- **Lifecycle cost** = install + maintenance - savings - rebates over useful life
- **Avoided cost** = include utility escalation rate (typically 2-4%/year)

### Rebate & Incentive Check
- Federal: ITC (30% solar), 179D deduction ($0.50-$5.00/sq ft)
- State: DSIRE database lookup by ZIP code
- Utility: custom incentive programs ($/kWh saved, $/kW reduced)

## Output Format

```
ENERGY AUDIT REPORT
Building: [name] | Type: [type] | Size: [sq ft] | Location: [city, state]

CURRENT PERFORMANCE
Annual Energy Cost: $XXX,XXX
EUI: XX.X kBtu/sq ft (benchmark: XX.X — [above/below] median)
ENERGY STAR Score: XX/100

TOP RECOMMENDATIONS (ranked by payback)
#1: [ECM] — $XX,XXX savings/yr | $XX,XXX cost | X.X yr payback | XX% IRR
#2: [ECM] — ...

TOTAL OPPORTUNITY
Combined Savings: $XXX,XXX/yr (XX% reduction)
Total Investment: $XXX,XXX
Blended Payback: X.X years
Available Rebates: $XX,XXX

IMPLEMENTATION ROADMAP
Phase 1 (0-6 mo): [quick wins — LED, controls, demand response]
Phase 2 (6-18 mo): [HVAC, VFDs, envelope]
Phase 3 (18-36 mo): [renewables, major retrofits]
```

## Why This Matters

Commercial buildings waste 30% of the energy they consume (DOE). A $500K/year energy bill typically has $150K+ in recoverable savings. Most measures pay for themselves in 2-4 years, then it's pure margin.

---

Built by [AfrexAI](https://afrexai-cto.github.io/context-packs/) — AI context packs for real business operations.

Explore more tools:
- [AI Revenue Calculator](https://afrexai-cto.github.io/ai-revenue-calculator/) — find where your business leaks money
- [Agent Setup Wizard](https://afrexai-cto.github.io/agent-setup/) — deploy AI agents in minutes
- [Context Packs](https://afrexai-cto.github.io/context-packs/) — $47 industry-specific agent configs for Manufacturing, Professional Services, and more
