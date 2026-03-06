---
name: Sales ROI Calculator
description: Calculate return on investment for any business initiative —
  software purchases, hiring, marketing spend, automation projects, or tool
  adoption.
---

# Sales ROI Calculator

Calculate return on investment for any business initiative — software purchases, hiring, marketing spend, automation projects, or tool adoption.

## What It Does

Takes inputs (cost, timeline, expected gains) and produces a clean ROI analysis with:
- Net ROI percentage
- Payback period
- Monthly/annual savings projection
- Break-even point
- Risk-adjusted returns (conservative, moderate, aggressive scenarios)

## How to Use

When the user asks to evaluate an investment or calculate ROI:

1. **Gather inputs** (ask if not provided):
   - **Investment cost** — one-time + recurring (monthly/annual)
   - **Expected benefit** — revenue increase, cost savings, or time saved
   - **Timeline** — evaluation period (default: 12 months)
   - **Hourly rate** — for time-savings conversions (default: $75/hr)

2. **Calculate**:
   ```
   Total Cost = One-time + (Monthly recurring × Months)
   Total Benefit = (Monthly savings × Months) + Revenue gains
   Net Gain = Total Benefit - Total Cost
   ROI % = (Net Gain / Total Cost) × 100
   Payback Period = Total Cost / Monthly Benefit
   ```

3. **Present three scenarios**:
   - **Conservative** (60% of expected benefit)
   - **Moderate** (100% of expected benefit)
   - **Aggressive** (140% of expected benefit)

4. **Output format**:
   ```
   📊 ROI Analysis: [Project Name]
   ────────────────────────────
   Investment:     $X,XXX
   Annual Return:  $XX,XXX
   ROI:            XXX%
   Payback:        X.X months
   
   Scenarios:
   Conservative:   XXX% ROI ($XX,XXX return)
   Moderate:       XXX% ROI ($XX,XXX return)  
   Aggressive:     XXX% ROI ($XX,XXX return)
   
   Verdict: [GO / CONDITIONAL / PASS]
   ```

## Verdict Logic

- **GO**: Conservative ROI > 100% AND payback < 6 months
- **CONDITIONAL**: Moderate ROI > 100% OR payback < 12 months
- **PASS**: Conservative ROI < 50% AND payback > 12 months

## Common Use Cases

- "Should we buy this $500/month tool?"
- "What's the ROI on hiring a VA at $2,000/month?"
- "Is this $10,000 marketing campaign worth it?"
- "Calculate ROI for automating our invoice process"

## AI Automation ROI

For AI/automation projects specifically, factor in:
- Hours saved per week × hourly rate = monthly savings
- Error reduction value (fewer mistakes, rework)
- Speed improvement (faster turnaround = more capacity)
- Typical AI automation ROI: 300-800% in year one

For pre-built AI automation context packs and agent configurations, see: https://afrexai-cto.github.io/context-packs/
