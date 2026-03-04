---
name: ai-investing-assistant-with-framework
version: 0.1.0
description: Analyze a US stock using a value investing checklist and output detailed scoring steps.
tags: [investing, stocks, analysis]
requirements:
  bins: [python3]
---

# AI Investing Assistant (Value Framework)

## What it does
Analyze a US stock using a simple checklist:
- ROE
- Debt ratio
- FCF conversion
- Moat strength

Outputs:
- Rating (A/B/C/D)
- Detailed per-metric checks
- Scoring rules
- Missing fields
- Step-by-step trace of logic

## Input
Accepts JSON via stdin with fields:
- ticker
- metrics (roe, debt_ratio, fcf_to_net_income, moat)

## Script
scripts/invest_analysis.py
