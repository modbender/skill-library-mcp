# Workflow Details

## SCAN Mode

1. Check if `.anti-pattern-state.json` exists
   - If exists → ask: "Found existing session with X/Y fixed. Resume or start fresh?"
2. Run detector: `bunx antipattern-czar`
3. Parse output — extract file, line, pattern, snippet per issue
4. Classify severity and critical-path status
5. Write `.anti-pattern-state.json`
6. Show summary:

```
🔍 Scan Complete

Found 132 anti-patterns:
├── CRITICAL: 28 (21%)
├── HIGH: 45 (34%)
└── MEDIUM: 59 (45%)

Critical path issues: 12 (require immediate attention)

Next: Run /anti-pattern-czar review to start fixing
```

## REVIEW Mode

1. Load `.anti-pattern-state.json`
2. Filter pending issues, sorted: critical-path first → severity (critical > high > medium)
3. For each issue:

   **a. Read code** (±10 lines context using Read tool)

   **b. Explain problem:**
   ```
   ⚠️ Issue #3/28 [CRITICAL] - NO_LOGGING_IN_CATCH

   File: src/services/worker-service.ts:142
   Critical Path: YES ⛔

   try {
     await this.processJob(job);
   } catch (error) {
     // Nothing here — failures are invisible!
   }

   WHY DANGEROUS:
   • Job failures are completely silent
   • No debugging signal for production issues
   ```

   **c. Propose fix options** (offer 3–4 concrete choices):
   - Add logging
   - Add logging + rethrow
   - Remove try-catch (propagate)
   - Skip for now

   **d. Apply chosen fix** using Edit tool

   **e. Update state**, show progress, ask to continue

4. Every 5 fixes: offer to re-run detector to verify

## AUTO Mode

> ⚠️ Requires explicit user confirmation before starting

1. Ask: "Auto mode will fix X issues automatically. Proceed?"
2. For each **non-critical-path** issue:
   - Apply standard fix template from `patterns.md`
   - Log all changes
3. For **critical-path** issues: STOP → switch to REVIEW mode
   - Message: "Found critical-path issue in `<file>`. Switching to review mode for manual approval."
4. Generate final summary report

### Auto-eligible patterns
Only auto-fix patterns marked ✅ in the pattern catalog: EMPTY_CATCH, NO_LOGGING_IN_CATCH, PROMISE_EMPTY_CATCH, PARTIAL_ERROR_LOGGING, PROMISE_CATCH_NO_LOGGING.

Never auto-fix: LARGE_TRY_BLOCK, GENERIC_CATCH, ERROR_STRING_MATCHING, ERROR_MESSAGE_GUESSING, CATCH_AND_CONTINUE_CRITICAL_PATH.

## RESUME Mode

1. Load `.anti-pattern-state.json`
2. Show: "Session found. X/Y fixed. Y–X pending."
3. Start REVIEW mode from first `pending` issue

## REPORT Mode

```
═══════════════════════════════════════════════════════
              Anti-Pattern Czar — Session Report
═══════════════════════════════════════════════════════

Session: abc123 | Started: 2026-01-27 10:30 AM | Duration: 2h 15m

PROGRESS ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 45%

  Total Issues:    132
  Fixed:            52 (39%)
  Overrides:         8 (6%)
  Remaining:        72 (55%)

BY SEVERITY
┌──────────┬───────┬───────┬───────────┐
│ Severity │ Fixed │ Total │ Remaining │
├──────────┼───────┼───────┼───────────┤
│ CRITICAL │    12 │    28 │        16 │
│ HIGH     │    22 │    45 │        23 │
│ MEDIUM   │    18 │    59 │        41 │
└──────────┴───────┴───────┴───────────┘

RECENT FIXES
• worker-service.ts:142 — Added logging
• SessionStore.ts:89 — Removed empty catch
• SearchManager.ts:234 — Added type narrowing

NEXT ACTIONS
→ /anti-pattern-czar review        Continue fixing
→ /anti-pattern-czar auto --high   Auto-fix HIGH severity
═══════════════════════════════════════════════════════
```

## Completion Report

```
Anti-pattern cleanup complete!

Before:  ISSUES: 28
After:   ISSUES: 0  |  APPROVED OVERRIDES: 15

All anti-patterns resolved! 🎉
```

## Error Handling

- Detector fails → report error, ask user to check Bun and package availability (`bunx antipattern-czar --version`)
- State file corrupted → offer to backup + start fresh
- Fix application fails → rollback edit, report error, continue to next issue
