# DDD Patterns Reference

## ANALYZE → PRESERVE → IMPROVE Cycle

### ANALYZE Phase

**Goal:** Understand the existing code WITHOUT changing it.

1. **Map the codebase**
   - Entry points (API routes, CLI commands, event handlers)
   - Core business logic locations
   - External dependencies (DB, APIs, file system)
   - Shared state and side effects

2. **Identify domain boundaries**
   - Which modules are tightly coupled?
   - Where are the natural seams for testing?
   - What are the implicit contracts between modules?

3. **Document current behavior**
   ```markdown
   ## Module: {name}
   - Input: {what it receives}
   - Output: {what it produces}
   - Side effects: {DB writes, API calls, file I/O}
   - Dependencies: {other modules it calls}
   - Known issues: {bugs, tech debt}
   ```

### PRESERVE Phase

**Goal:** Lock down current behavior with characterization tests.

1. **Characterization test pattern**
   ```
   test('captures current behavior of calculatePrice', () => {
     // Call the function with known inputs
     const result = calculatePrice(100, 'premium', 'KR');
     
     // Record what it ACTUALLY returns (not what it SHOULD return)
     expect(result).toBe(88000);  // Whatever the current output is
   });
   ```

2. **Priority order for characterization tests**
   - Public API endpoints
   - Core business logic functions
   - Data transformation pipelines
   - Functions you plan to modify

3. **Coverage target for PRESERVE phase**
   - Cover ALL code paths you plan to touch
   - Include error paths and edge cases of existing code
   - Minimum: every function being modified has at least one test

### IMPROVE Phase

**Goal:** Make changes safely under test protection.

1. **Golden rule:** One change at a time, test after each
2. **Safe refactoring moves:**
   - Extract method/function
   - Rename for clarity
   - Replace magic numbers with constants
   - Simplify conditionals
   - Remove dead code (confirmed by analysis)

3. **When a characterization test breaks:**
   - STOP — this means behavior changed
   - Decide: Is this an intentional improvement or accidental breakage?
   - If intentional: Update test to reflect new behavior, document the change
   - If accidental: Revert and try a smaller change

## When to Choose DDD Over TDD

| Signal | Methodology |
|--------|-------------|
| No tests exist | DDD |
| Tests exist but coverage < 10% | DDD |
| Legacy code with unclear behavior | DDD |
| New feature on tested codebase | TDD |
| Greenfield project | TDD |
| Bug fix with reproduction test | TDD |

## Strangler Fig Pattern

For large legacy rewrites:
1. Build new implementation alongside old
2. Route traffic gradually to new code
3. Keep old code as reference until new is verified
4. Remove old code only after full confidence
