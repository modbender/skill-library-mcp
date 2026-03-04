---
name: investing-analyst
description: "Thesis-driven equity and options trading analyst. Use when: (1) evaluating a trade idea before entering a position, (2) analyzing options pricing via IV vs Historical Volatility, (3) planning earnings catalyst plays, (4) reviewing a losing position and deciding whether to hold or exit, (5) checking for emotional/FOMO trading patterns, (6) running a pre-trade checklist. NOT for: general financial education, portfolio-level asset allocation, or tax advice."
---

# Investing Analyst

Structured workflow for thesis-driven equity and options trading. Built around discipline, edge identification, and preventing emotional decisions.

## Pre-Trade Checklist (3 Gates)

Run all 3 before every options entry. See `references/pre-trade-framework.md` for full detail.

| Gate | Question | Pass Condition |
|------|----------|----------------|
| 1. Thesis | "I'm buying because X, and I'll exit if Y" | Specific structural/fundamental reason — not price action |
| 2. Edge | Do you have real informational advantage on this name? | Names you've researched deeply for >3 months |
| 3. Entry Timing | Thesis confirmation or price movement? | Thesis confirmation + technical trigger |

**If any gate fails → don't trade.**

## Options Pricing Workflow (IV vs HV)

Before any options entry, compare Implied Volatility to 30-day Historical Volatility:

- **IV > HV significantly** → Options EXPENSIVE. Prefer spreads to reduce premium paid.
- **IV ≈ HV** → Fair pricing. Long calls acceptable with clean thesis.
- **IV < HV** → Options CHEAP. Long calls or straddles can make sense.

Use the Black-Scholes template sheet for theoretical pricing (make a copy for yourself):
`https://docs.google.com/spreadsheets/d/1_Q9ZpGzA2zmuaBmE0R2XVdZHpRnWA2PRNSfmpDXf1as/`

See `references/options-signals.md` for expected move calculations and earnings IV crush guidance.

## Position Management Rules (Non-Negotiable)

- **Set max loss before entry. No exceptions.**
- **Never add to a losing options position. Ever.** (The Escalation Rule — see references/pre-trade-framework.md)
- **Close spreads with <2 weeks to expiry** regardless of P&L if ITM
- **Take profits**: Set target at entry, close ≥50% when hit

## Trade Types

| Type | Examples | Edge Level |
|------|----------|-----------|
| Earnings Catalyst | Names you know deeply — earnings cadence, metrics, guidance patterns | High |
| Contrarian Structural | Stocks at technical extremes with fundamental thesis | High (with trigger) |
| Macro/Index | SPY, QQQ LEAPs | Medium — size small |
| Momentum/FOMO | Hot names during runs without a thesis | None — avoid |

Full playbook per trade type: `references/pre-trade-framework.md`

## Trade Log Template

Fill before every entry. If you can't fill it, don't trade:

```
Date:
Ticker:
Structure (e.g. $30C 3/20, bull call spread $190/195):
Entry debit/credit:
Max profit / Max loss:

THESIS: I'm buying because...
INVALIDATION: I'll exit early if...
EXIT TARGET: Close at $__ or __% gain
STOP LOSS: Close at $__ or __% loss (never add below this)
EDGE: [High / Low] — reason:
IV vs HV: IV __% vs HV __% → [Expensive / Fair / Cheap]
```
