---
name: work-receipt
version: 1.0.0
description: >
  Generates a detailed receipt of everything you accomplished in a coding
  session — files changed, problems solved, decisions made, debt incurred,
  and what's left for tomorrow. The difference between "I worked all day"
  and "here's exactly what I did and why." Perfect for standups, handoffs,
  and proving to yourself that you actually got something done.
author: J. DeVere Cooley
category: everyday-tools
tags:
  - productivity
  - documentation
  - standups
  - tracking
metadata:
  openclaw:
    emoji: "🧾"
    os: ["darwin", "linux", "win32"]
    cost: free
    requires_api: false
    tags:
      - zero-dependency
      - everyday
      - productivity
---

# Work Receipt

> "If you can't explain what you did today in three sentences, you either did nothing or you did everything. Both need a receipt."

## What It Does

End of your session. You've been coding for hours. Someone asks "what did you work on?" and you say "...stuff. The checkout thing. I think I fixed a bug?" Your commit messages say `wip`, `fix`, `fix again`, `actually fix`, and `please work`.

Work Receipt analyzes your session's artifacts — git history, file changes, test results, terminal commands — and produces a structured summary of:

1. **What you accomplished** (shipped, fixed, built)
2. **What you changed** (files, lines, architecture)
3. **What you decided** (and why)
4. **What you left behind** (TODOs, known issues, next steps)
5. **What it cost** (time, complexity added, debt incurred)

## The Receipt

```
╔══════════════════════════════════════════════════════════════╗
║                       WORK RECEIPT                          ║
║                                                              ║
║  Session: Tuesday, March 3, 2026                            ║
║  Duration: 4h 22m (1:15 PM — 5:37 PM)                      ║
║  Branch: feature/multi-currency-checkout                     ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  ACCOMPLISHED:                                               ║
║  ✓ Multi-currency tax calculation (USD, EUR, GBP, JPY)      ║
║  ✓ Zero-decimal currency handling (JPY, KRW)                ║
║  ✓ Tax rounding edge case for sub-cent amounts               ║
║  ~ Partial: Currency conversion caching (70% complete)       ║
║                                                              ║
║  CHANGED:                                                    ║
║  ├── Modified: 6 files (+184 lines, -47 lines)              ║
║  │   ├── src/checkout/tax.ts .......... +89 / -12           ║
║  │   ├── src/checkout/currency.ts ..... +42 / -8            ║
║  │   ├── src/types/currency.ts ........ +18 / -3            ║
║  │   ├── src/checkout/tax.test.ts ..... +24 / -6            ║
║  │   ├── src/checkout/currency.test.ts  +11 / -18           ║
║  │   └── src/config/rates.json ........ +0 / -0 (reformatted)║
║  ├── Created: 1 file                                         ║
║  │   └── src/checkout/decimal-precision.ts (29 lines)        ║
║  └── Commits: 4                                              ║
║      ├── "feat: multi-currency tax calculation"              ║
║      ├── "fix: zero-decimal currency handling (JPY/KRW)"     ║
║      ├── "fix: sub-cent rounding edge case"                  ║
║      └── "wip: currency conversion caching (incomplete)"     ║
║                                                              ║
║  DECISIONS MADE:                                             ║
║  ├── Used per-currency precision lookup (not flat decimal)   ║
║  │   Reason: JPY/KRW have 0 decimals, BHD has 3 decimals    ║
║  ├── Round after tax, not before                             ║
║  │   Reason: Rounding before creates up to 0.5% error        ║
║  └── Separate decimal-precision module (not inline)          ║
║      Reason: Reusable for display, export, and reporting     ║
║                                                              ║
║  TESTS:                                                      ║
║  ├── Added: 4 new tests                                      ║
║  ├── Modified: 2 existing tests                              ║
║  ├── Status: 23/23 passing ✓                                 ║
║  └── Coverage: 91% → 94% (+3%) for checkout/                ║
║                                                              ║
║  LEFT BEHIND:                                                ║
║  ├── TODO: Currency conversion cache TTL (hardcoded to 1h)   ║
║  ├── TODO: Add tests for BHD (3-decimal currency)            ║
║  ├── WIP: Caching layer ~70% done (needs invalidation logic) ║
║  └── DEBT: No test for concurrent currency conversions       ║
║                                                              ║
║  SESSION METRICS:                                            ║
║  ├── Complexity: Net +12 cyclomatic complexity               ║
║  ├── Debt: 1 new entry (concurrent test, ~2h to fix)         ║
║  ├── Dependencies: 0 new dependencies added                  ║
║  └── Breaking changes: 0                                     ║
║                                                              ║
║  STANDUP SUMMARY:                                            ║
║  "Implemented multi-currency tax calculation supporting      ║
║  22 currencies including zero-decimal (JPY/KRW). Fixed       ║
║  rounding edge case for sub-cent amounts. Currency conversion ║
║  caching is 70% done, will finish tomorrow."                 ║
╚══════════════════════════════════════════════════════════════╝
```

## What It Captures

### 1. Accomplishments (from commits and diffs)

```
SOURCE:
├── Commit messages (especially conventional commit prefixes: feat, fix, refactor)
├── Diff analysis (what changed functionally, not just syntactically)
├── Test additions (new tests = new verified behavior)
└── Branch description / PR draft

CLASSIFICATION:
├── ✓ Complete: Committed, tested, ready for review
├── ~ Partial: Work in progress, documented but unfinished
├── ✗ Abandoned: Started but reverted or stashed
└── ⟳ Refactored: Changed structure without changing behavior
```

### 2. Decisions (from code patterns and comments)

```
DETECTION:
├── Stashed alternatives (you tried X, went with Y)
├── TODO/FIXME comments (you noted a decision to defer)
├── Reverted commits (you chose against something)
├── Code comments with "because", "instead of", "rather than"
└── Config changes (explicit choices about values/settings)
```

### 3. What's Left (from WIP state)

```
DETECTION:
├── Uncommitted changes (work still in progress)
├── TODO/FIXME added during this session
├── Failing tests that were added but not yet fixed
├── Incomplete function signatures (return type is any/unknown)
├── Empty function bodies or placeholder implementations
└── WIP commits (literally "wip" in the message)
```

### 4. Cost Analysis (from code metrics)

```
METRICS:
├── Lines of code: net addition/reduction
├── Complexity: cyclomatic complexity change
├── Test coverage: percentage change
├── Dependencies: new libraries added
├── Debt: shortcuts taken, tests skipped, TODOs added
├── Files touched: total surface area of changes
└── Breaking changes: interface/schema modifications
```

## Receipt Formats

### Standup Format (3 sentences)
```
Yesterday: Implemented multi-currency tax calculation for 22 currencies.
Fixed zero-decimal currency handling and rounding edge cases.
Today: Will complete currency conversion caching and add BHD tests.
Blockers: None.
```

### Handoff Format (for passing work to a colleague)
```
HANDOFF: feature/multi-currency-checkout
├── STATUS: 85% complete
├── WHAT'S DONE: Tax calc works for all currencies, fully tested
├── WHAT'S LEFT: Caching layer needs invalidation logic (see TODO in currency.ts:42)
├── WATCH OUT FOR: JPY and KRW are zero-decimal — don't assume 2 decimal places
├── DECISIONS LOCKED: Round after tax, not before. Precision lookup table in decimal-precision.ts
├── OPEN QUESTIONS: Cache TTL — 1h is a guess, may need tuning in production
└── RUN: npm test -- checkout/ (should be 23/23 green)
```

### PR Description Format
```
## Multi-Currency Tax Calculation

Adds support for 22 currencies in the checkout tax calculation,
including zero-decimal currencies (JPY, KRW) and 3-decimal currencies (BHD).

### Changes
- New `decimal-precision.ts` module with per-currency precision lookup
- Updated `tax.ts` to use precision-aware calculation
- Fixed rounding: now rounds after tax application (not before)
- 4 new tests, 2 updated tests (91% → 94% coverage)

### Not Included
- Currency conversion caching (separate PR, in progress)
- Concurrent conversion tests (tracked as tech debt)
```

### Commit Log Cleanup
When your session has messy commits, Work Receipt suggests a clean rewrite:

```
CURRENT COMMITS:
├── "wip"
├── "fix stuff"
├── "actually fix the thing"
└── "wip: caching maybe"

SUGGESTED REWRITE:
├── "feat: multi-currency tax calculation with precision lookup"
├── "fix: handle zero-decimal currencies (JPY, KRW) in tax calc"
├── "fix: round after tax application to prevent sub-cent errors"
└── "wip: currency conversion caching (invalidation pending)"
```

## When to Invoke

- **End of every work session.** Make it a habit.
- Before standup (generate your update in 5 seconds instead of 5 minutes of remembering)
- Before creating a PR (auto-generate the description)
- Before handing off work (structured handoff instead of "uh, it's on the branch")
- End of sprint (aggregate daily receipts into sprint summary)
- When you feel like you accomplished nothing (the receipt proves otherwise)

## Why It Matters

Developers consistently underestimate what they accomplished and overestimate what they have left. Without a receipt, work becomes invisible — to managers, to teammates, and to yourself.

Work Receipt makes invisible work **visible**. Every decision documented. Every line accounted for. Every TODO tracked.

Zero external dependencies. Zero API calls. Pure git and filesystem analysis.
