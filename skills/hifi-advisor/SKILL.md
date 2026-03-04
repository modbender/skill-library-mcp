---
name: hifi-advisor
description: Evaluate hi-fi and audio gear options, build system recommendations, guide installation and tuning, and analyze used-market pricing/resale value. Use when users ask for speaker/amp/DAC matching, room setup, placement, EQ/tuning checklists, buying advice, scam-risk checks, or fair-price analysis for second-hand audio gear (Hi-Fi, headphone rigs, home stereo).
---

# HiFi Advisor

## Overview
Deliver practical, decision-ready guidance for hi-fi purchase, setup, tuning, and pricing tasks. Prioritize low-risk recommendations, explicit trade-offs, and actionable next steps.

## Quick Workflow Decision

1. Identify user intent:
   - **Buy/compare gear** -> run **Review + Matching workflow**.
   - **Install or improve sound** -> run **Setup + Tuning workflow**.
   - **Check second-hand deal value** -> run **Price Analysis workflow**.
2. Gather minimum inputs (ask only missing essentials):
   - Budget range
   - Listening distance / room size
   - Existing gear and connection constraints
   - Music preference and loudness target
3. Return output in this order:
   - Recommendation
   - Why it fits
   - Risks / caveats
   - Next action checklist

## Review + Matching Workflow

1. Capture system context: room, source, use-case (music/movie/desk), volume habits.
2. Match core chain first: transducer (speaker/headphone) -> amp power/current -> source/DAC.
3. Penalize mismatch risks:
   - Low-sensitivity speakers with underpowered amps
   - Bright speaker + bright amp in reflective room
   - Nearfield setup with large floorstanders in tiny rooms
4. Produce 2-3 ranked options:
   - Best value
   - Balanced
   - Stretch option
5. Give upgrade path that preserves resale liquidity.

Use `references/workflows.md` for the detailed template.

## Setup + Tuning Workflow

1. Start with placement before EQ:
   - Symmetry, toe-in, listener triangle, wall distance
2. Solve biggest acoustic problems first:
   - First reflections, bass boom/nulls, desk bounce (for nearfield)
3. Apply light EQ only after physical setup is reasonable.
4. Validate with repeatable test tracks and one objective check (if available).
5. End with a short "do not change all at once" iteration plan.

Use `references/checklists.md` for step-by-step checklists.

## Price Analysis Workflow (Used Market)

1. Normalize listing data by region, condition, accessories, and shipping inclusion.
2. Build a fair-price band using robust statistics (median + IQR).
3. Apply adjustments:
   - No box/accessories: discount
   - Cosmetic issues: discount
   - Recent service with proof: premium
   - Local pickup vs shipped risk: adjust confidence, not only price
4. Output:
   - Fair range
   - Strong-buy threshold
   - Walk-away threshold
   - Risk flags

If user provides tabular listing data, run:

```bash
python3 scripts/price_stats.py listings.csv
```

Expected columns: `price` plus optional `platform,condition,model,date,notes`.

## Output Quality Standard

Always provide:
- A clear recommendation (not just raw data)
- 3-5 bullet rationale
- Top risk factors
- Concrete next steps the user can execute today

Use concise language. Avoid mystical audiophile claims. Prefer testable, practical guidance.
