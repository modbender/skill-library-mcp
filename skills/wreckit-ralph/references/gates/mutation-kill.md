# Gate: Mutation Kill

**Preferred tool:** Stryker Mutator (JS/TS) or mutmut (Python). See `scripts/mutation-test-stryker.sh`.
For projects without Stryker installed, fall back to `scripts/mutation-test.sh` (AI-based mutations).

**Question:** Do the tests actually catch bugs, or do they just run green?

## Process

Generate mutations — small, realistic code changes that SHOULD break something:

- Flip boolean conditions (`if (x > 0)` → `if (x < 0)`)
- Remove null checks
- Swap function arguments
- Change boundary values (`>=` → `>`)
- Remove error handling
- Return early before side effects

For each mutation:
1. Apply mutation to a copy (never mutate real code)
2. Run test suite against mutated copy
3. Tests still pass → **mutation survived** (tests are weak here)
4. Revert mutation, record result

## External Tools (optional, better)

- **Stryker** (JS/TS) — real mutation framework, much more thorough
- **mutmut** (Python)
- **cargo-mutants** (Rust)

If available, prefer external tools over AI-generated mutations.

## Pass/Fail

- **Pass:** ≥95% of mutations killed
- **Caution:** 90-94% kill rate
- **Fail:** <90% kill rate — tests are not trustworthy

---

## Validation Status (2026-02-23)

### Tool Availability
Checked on host: `Christian's Mac mini (Darwin 25.3.0 arm64)`

```
mutmut:       NOT INSTALLED  (pip install mutmut to enable)
stryker:      NOT INSTALLED  (npx stryker / npm install @stryker-mutator/core)
cargo-mutants: NOT INSTALLED  (cargo install cargo-mutants)
```

### AI Fallback Path — VALIDATED ✅

The AI-based mutation path in `scripts/mutation-test.sh` was validated end-to-end on:
- **Fixture:** `tests/fixtures/perfect-small` (TypeScript, vitest)
- **Result:** 7 mutations generated, 7 killed, 0 survived — **100% kill rate**
- **Verdict:** SHIP

Bug fixed: `SCRIPT_DIR` was computed _after_ `cd "$PROJECT"`, causing a path resolution failure when called with a relative path (e.g., `bash scripts/mutation-test.sh tests/fixtures/...`). Fixed by moving `SCRIPT_DIR` assignment to the top of the script before any `cd`.

### mutmut Path — NOT VALIDATED (tool not installed)

The mutmut detection block exists and correctly falls through to AI fallback when mutmut is absent:
- Script prints: `mutmut not installed. Install with: pip install mutmut`
- Continues to AI fallback path
- AI fallback works for Python files (`.py` detected, `LANG="py"` set, same mutation loop runs)

### Stryker Path — NOT VALIDATED (tool not installed)

The stryker detection block exists. When stryker is not installed:
- `npx stryker --version` returns non-zero → block skipped
- Falls through to AI mutation loop
- Note: `mutation-test-stryker.sh` exists but has not been end-to-end tested with a real Stryker install

### Next Steps to Complete Validation

1. `pip install mutmut` and run: `bash scripts/mutation-test.sh <python-project>`
2. `npm install -g @stryker-mutator/core` and run against a JS/TS project
3. Consider adding mutation-test canary to `tests/run-tests.sh`
