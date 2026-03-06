---
name: systematic-debugging
description: Find root cause before attempting fixes — 4-phase investigation, never guess-fix
---

# Systematic Debugging — Root Cause First

## Iron Law

NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST.

If you're about to change code to "try something," STOP. Investigate first.

## The 4 Phases

### Phase 1: Root Cause Investigation

1. **Read the error** — Read the FULL error message, stack trace, and logs. Not just the first line.

2. **Reproduce** — Can you make the error happen consistently? If not, gather more data before changing anything.

3. **Check recent changes** — What changed since it last worked?
   ```bash
   git log --oneline -10
   git diff HEAD~3
   ```

4. **Gather evidence** — Don't theorize without data. Check database state, API responses, config values.

### Phase 2: Pattern Analysis

1. **Find working examples** — Is there similar code in the project that works? Compare it.

2. **Compare** — What's different between working and broken code?

3. **Check dependencies** — Is the issue in your code or something upstream? Check library versions, external API changes.

### Phase 3: Hypothesis and Testing

1. **Form ONE hypothesis** — "The error occurs because X"
2. **Test minimally** — Change ONE thing to verify
3. **If wrong** — Return to Phase 1, don't stack guesses

### Phase 4: Implementation

1. **Write a failing test** that reproduces the bug
2. **Fix the root cause** (not the symptom)
3. **Verify the test passes**
4. **Run full test suite** — no regressions
5. **Document the failure** — Log what failed and why for future reference

## Rationalizations That Mean STOP

| Thought | Reality |
|---------|---------|
| "Let me just try this quick fix" | That's guessing. Investigate first. |
| "It's probably X" | Probably is not certainly. Verify. |
| "I'll fix it and see if it helps" | You're changing code without understanding. |
| "Multiple things might be wrong" | Fix one thing at a time. |
| "I've seen this before" | Verify in THIS codebase. Don't assume. |

## When You're Stuck (3+ Failed Fixes)

Don't keep guessing. Escalate:

1. Document what you tried and what happened
2. List your symptoms, what you investigated, and hypotheses tested
3. Ask for help with specific questions, not "it doesn't work"
4. Share the evidence you've gathered so others don't repeat your investigation
