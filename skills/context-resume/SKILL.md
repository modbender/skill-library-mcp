---
name: context-resume
version: 1.0.0
description: >
  Reconstructs your full working context when you return to a task after
  an interruption — meeting, lunch, sleep, weekend, or three-week vacation.
  Not session restore. Mental state restore. Answers the question every
  developer asks ten times a week: "Where was I?"
author: J. DeVere Cooley
category: everyday-tools
tags:
  - context-switching
  - productivity
  - workflow
  - daily-driver
metadata:
  openclaw:
    emoji: "🧵"
    os: ["darwin", "linux", "win32"]
    cost: free
    requires_api: false
    tags:
      - zero-dependency
      - everyday
      - productivity
---

# Context Resume

> "The average developer is interrupted every 11 minutes. It takes 23 minutes to fully resume deep work. Do the math — most developers never reach deep work at all."

## What It Does

You close your laptop Friday evening mid-feature. Monday morning you open it. Your files are there. Your branch is there. Your terminal history is there.

But **you** aren't there. The mental model you had — which function you were about to write, which edge case you just discovered, which test was failing and why, which approach you'd decided on and which you'd rejected — that's gone.

Context Resume rebuilds your mental state from the artifacts you left behind.

## What It Recovers

### 1. Where You Were

```
LAST SESSION ANALYSIS:
├── Branch: feature/checkout-v2
├── Last commit: "wip: tax calculation for multi-currency" (uncommitted changes present)
├── Modified files (uncommitted):
│   ├── src/checkout/tax.ts ......... +47 lines (function incomplete, ends mid-logic)
│   ├── src/checkout/tax.test.ts .... +12 lines (2 tests, 1 failing)
│   └── src/types/currency.ts ....... +3 lines (new type added)
├── Last meaningful edit: src/checkout/tax.ts:84 (3:47 PM Friday)
├── Git stash: 1 entry ("experimental: flat tax approach — didn't work")
└── Uncommitted deletions: none
```

### 2. What You Were Doing

```
ACTIVITY RECONSTRUCTION:
├── Primary task: Implementing multi-currency tax calculation
├── Current state: Mid-implementation
│   ├── calculateTax() is 60% complete (has happy path, missing edge cases)
│   ├── One test is passing (USD → USD, simple case)
│   ├── One test is FAILING: "should handle JPY zero-decimal currency"
│   │   └── Error: Expected 100, got 1.00 (decimal handling bug)
│   └── CurrencyType enum was just added but not yet used in calculateTax
├── Approach taken: Per-currency decimal precision lookup table
├── Approach rejected: Flat percentage (stashed, labeled "didn't work")
└── Likely next step: Fix decimal handling for zero-decimal currencies (JPY, KRW)
```

### 3. What You'd Decided

```
DECISION CONTEXT (reconstructed from commits, comments, and stash):
├── Decided FOR: Lookup table approach for currency decimals
│   └── Evidence: Current implementation uses this pattern
├── Decided AGAINST: Flat percentage approach
│   └── Evidence: Stashed with note "didn't work"
├── Open question: How to handle currencies not in the lookup table
│   └── Evidence: TODO comment on line 67: "// fallback for unknown currencies?"
└── Unresolved: Whether to round before or after tax application
    └── Evidence: Both orderings present in different test cases
```

### 4. What Was Blocking You

```
BLOCKERS DETECTED:
├── ACTIVE: JPY test failing (zero-decimal currency handling)
│   └── This was likely the last thing you were working on
├── PENDING: No test for rounding edge cases
│   └── TODO on line 72: "// test rounding: 33.33% of $10?"
└── EXTERNAL: None detected
```

## How It Works

```
Phase 1: ARTIFACT COLLECTION
├── Git state: branch, commits, diff, stash, reflog
├── File state: modification times, partial edits, cursor bookmarks
├── Test state: last test run results, which tests are failing and why
├── Comment state: TODOs, FIXMEs, HACKs, and inline questions
├── Terminal state: recent commands (build, test, run attempts)
└── Time analysis: order of modifications, last-touch timestamps

Phase 2: NARRATIVE RECONSTRUCTION
├── From artifacts, reconstruct the story:
│   ├── What task were you working on? (branch name, commit messages)
│   ├── What approach did you take? (code pattern analysis)
│   ├── What did you reject? (stashes, reverted changes, deleted code in diff)
│   ├── What was working? (passing tests, committed code)
│   ├── What was broken? (failing tests, incomplete functions)
│   └── What were you about to do? (partial code, TODOs, cursor position)
├── Sequence the story chronologically
└── Identify the exact point of interruption

Phase 3: CONTEXT BRIEFING
├── One-paragraph summary: "Here's where you left off"
├── Immediate next action: "You were about to..."
├── Active blockers: "This was stopping you..."
├── Open decisions: "You hadn't decided..."
└── Quick wins: "These are close to done..."

Phase 4: WARM-UP SUGGESTIONS
├── Recommend a re-entry point (easiest way back into flow)
├── Suggest running the failing test first (immediate feedback loop)
├── Flag anything that changed externally while you were away
│   └── (new commits on main, dependency updates, CI status)
└── Estimated time to full context recovery: X minutes
```

## The Context Briefing

```
╔══════════════════════════════════════════════════════════════╗
║                    CONTEXT RESUME                           ║
║         Branch: feature/checkout-v2                         ║
║         Away since: Friday 3:47 PM (63 hours ago)           ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  SUMMARY:                                                    ║
║  You were implementing multi-currency tax calculation.       ║
║  The USD path works. You hit a bug with zero-decimal         ║
║  currencies (JPY, KRW) — they don't use cents, so your      ║
║  decimal math produces wrong results. You were mid-fix       ║
║  when you stopped.                                           ║
║                                                              ║
║  RESUME POINT:                                               ║
║  → src/checkout/tax.ts:84 — Fix decimal precision for JPY   ║
║  → Run: npm test -- tax.test.ts (1 failing, 1 passing)      ║
║                                                              ║
║  YOUR DECISIONS SO FAR:                                      ║
║  ✓ Using per-currency precision lookup (not flat %)          ║
║  ✗ Rejected flat percentage (stashed, didn't handle edge     ║
║    cases)                                                    ║
║  ? Open: fallback for unknown currencies                     ║
║  ? Open: round before or after tax?                          ║
║                                                              ║
║  WHILE YOU WERE AWAY:                                        ║
║  ├── 3 commits landed on main (none touch checkout/)         ║
║  ├── CI: green on main                                       ║
║  └── No dependency updates                                   ║
║                                                              ║
║  WARM-UP:                                                    ║
║  1. Run the failing test (see the error fresh)               ║
║  2. Fix JPY decimal handling on line 84                      ║
║  3. Add the KRW test case (same pattern)                     ║
║  Estimated context recovery: ~5 minutes                      ║
╚══════════════════════════════════════════════════════════════╝
```

## When to Invoke

- **Every morning.** First thing. Before you touch code.
- After any meeting longer than 30 minutes
- When switching between branches/tasks
- When picking up someone else's abandoned branch
- After a vacation or time off
- When a colleague asks "where did you leave off on X?"

## The Cost of Not Resuming

| Context Loss | Time Wasted | Risk |
|---|---|---|
| Forgot which approach you rejected | 30-60 min re-exploring dead end | Re-making a mistake you already made |
| Forgot which test was failing | 10-20 min re-discovering the bug | Thinking you introduced a new bug |
| Forgot the open design decision | Hours of rework | Choosing inconsistently with prior work |
| Forgot what changed externally | Variable | Building on stale assumptions |
| Complete context loss | 1-4 hours | Starting over on solved problems |

## Why It Matters

Context switching isn't just about closing and opening files. It's about **loading a mental model** — the web of decisions, discoveries, and intentions that make you productive in a specific area of code. Without that model, you're a tourist in your own codebase.

Context Resume doesn't save your session. It saves your **understanding**.

Zero external dependencies. Zero API calls. Pure git and filesystem analysis.
