# Systematic Debugging Reference

Source: obra/superpowers systematic-debugging skill

## The Iron Law

```
NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST
```

Random fixes waste time and create new bugs. Symptom fixes are failure.

## When to Use

Any technical issue:
- Test failures
- Bugs in production
- Unexpected behaviour
- Performance problems
- Build failures
- Integration issues

Use this ESPECIALLY when under time pressure, when "one quick fix" seems obvious,
or when previous fixes didn't work. Rushing guarantees rework.

## The Four Phases

Complete each phase before proceeding to the next.

### Phase 1: Root Cause Investigation

**BEFORE attempting ANY fix:**

1. **Read error messages carefully**
   - Don't skim past errors or warnings
   - Read stack traces completely
   - Note line numbers, file paths, error codes

2. **Reproduce consistently**
   - Can you trigger it reliably?
   - What are the exact steps?
   - If not reproducible → gather more data, don't guess

3. **Check recent changes**
   - What changed that could cause this?
   - `git diff`, recent commits, new dependencies, config changes

4. **Gather evidence in multi-component systems**

   When the system has multiple layers (API → service → database, CI → build → signing):
   
   Before proposing fixes, add diagnostic instrumentation at each boundary:
   ```
   For each component boundary:
     - Log what data enters
     - Log what data exits
     - Verify config/env propagation
   Run once to see WHERE it breaks, THEN investigate that layer
   ```

5. **Trace data flow**
   - Where does the bad value originate?
   - What called this with the bad value?
   - Trace up the call stack until you find the source
   - Fix at source, not at symptom

### Phase 2: Pattern Analysis

**Find the pattern before fixing:**

1. Find working examples of similar code in the codebase
2. Compare against references — read completely, don't skim
3. List every difference between working and broken
4. Understand all dependencies and assumptions

### Phase 3: Hypothesis + Testing

1. Form one clear hypothesis: "I think X is the root cause because Y"
2. Write it down explicitly
3. Design a minimal test to prove/disprove it
4. Run the test
5. If disproved → form new hypothesis, repeat
6. If proved → proceed to fix

### Phase 4: Fix + Verification

1. Fix at root cause, not symptom
2. Write a test that would have caught this bug
3. Verify fix works
4. Verify no regressions (run full test suite)
5. Commit with clear message explaining root cause

## Anti-Patterns

- **"Just try this"** — random fixes without root cause
- **"It's probably X"** — guessing without evidence
- **"Quick patch"** — symptom fix leaving root cause intact
- **Fixing multiple things at once** — makes it impossible to know what worked
- **Skipping reproduction** — debugging something you can't trigger consistently
