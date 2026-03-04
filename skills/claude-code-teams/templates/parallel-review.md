# Parallel Review Template

## When to Use This Pattern

✅ **Use when:**
- You need comprehensive code review covering multiple domains
- Security, performance, and test coverage are all important
- Changes span multiple files/modules
- Want parallel review to speed up PR approval process

❌ **Don't use when:**
- Changes are trivial (typo fix, formatting)
- Only one domain is relevant (e.g., pure documentation change)
- Codebase is <100 LOC (overhead > benefit)

## Team Structure

**Lead:** Coordinator who synthesizes findings
**Teammates:** 3 specialized reviewers
- **Security Reviewer:** Checks for vulnerabilities, auth issues, input validation
- **Performance Reviewer:** Identifies bottlenecks, inefficient queries, scaling issues
- **Test Coverage Reviewer:** Assesses test quality, missing edge cases, flaky tests

## File/Directory Boundaries

Each reviewer operates independently on the same codebase but produces separate output:

```
findings-security.md       # Security reviewer's findings
findings-performance.md    # Performance reviewer's findings
findings-tests.md          # Test coverage reviewer's findings
synthesis-review.md        # Lead's synthesized review (created after teammates finish)
```

## Spawn Prompt (Copy-Paste Ready)

```markdown
I need a comprehensive code review with 3 specialized perspectives: security, performance, and test coverage.

**Target:** [SPECIFY DIRECTORY OR FILES - e.g., ./src or ./pr-changes]

Spawn 3 teammates using Sonnet (tactical reviews):

1. **Security Reviewer**
   - Name: security-reviewer
   - Focus: Authentication, authorization, input validation, SQL injection, XSS, CSRF, secrets management
   - Output: findings-security.md
   - Tasks:
     * Review authentication/authorization logic
     * Check input validation and sanitization
     * Identify potential injection vulnerabilities
     * Verify secrets are not hardcoded
     * Flag any security anti-patterns

2. **Performance Reviewer**
   - Name: performance-reviewer
   - Focus: Algorithmic complexity, database queries, caching, memory leaks, scaling issues
   - Output: findings-performance.md
   - Tasks:
     * Profile algorithmic complexity (O(n²) → O(n log n) opportunities)
     * Identify N+1 queries or missing indexes
     * Check for caching opportunities
     * Flag memory leak risks (unclosed connections, large objects in memory)
     * Assess scaling implications (will this work at 10x load?)

3. **Test Coverage Reviewer**
   - Name: test-reviewer
   - Focus: Test quality, coverage gaps, edge cases, flaky tests, integration vs unit balance
   - Output: findings-tests.md
   - Tasks:
     * Assess test coverage for changed code
     * Identify missing edge case tests
     * Check for flaky test patterns (timing, non-determinism)
     * Verify integration tests cover critical paths
     * Flag untestable code (suggest refactoring for testability)

**Coordination rules:**
- Use delegate mode: I coordinate, teammates review (I don't implement)
- Each reviewer works independently (no blocking dependencies)
- Reviewers should document findings with:
  * Severity (Critical / High / Medium / Low)
  * File + line number
  * Recommendation
  * Example fix (if applicable)
- Wait for all 3 reviewers to complete before I synthesize findings

**After all teammates finish:**
1. Read all 3 findings files
2. Synthesize into synthesis-review.md with:
   - Executive summary (top 3 issues)
   - Findings by severity (Critical first)
   - Recommendations prioritized by impact
3. Report completion with summary
```

## Expected Outcomes

### Individual Findings

**findings-security.md:**
```markdown
# Security Review Findings

## Critical Issues
- [Line 42, auth.ts] SQL injection vulnerability in user lookup query
  - Recommendation: Use parameterized queries
  - Example: `db.query('SELECT * FROM users WHERE id = ?', [userId])`

## High Issues
- [Line 103, api.ts] Missing rate limiting on authentication endpoint
  - Recommendation: Add rate limiter (5 attempts per 15 minutes)

## Medium Issues
- [Line 67, config.ts] API key in environment variable without validation
  - Recommendation: Validate key format at startup
```

**findings-performance.md:**
```markdown
# Performance Review Findings

## Critical Issues
- [Line 215, posts-service.ts] N+1 query loading user data in loop
  - Recommendation: Use JOIN or batch query
  - Impact: 100 posts = 101 queries (should be 1 query)

## High Issues
- [Line 88, search.ts] Full table scan on large table
  - Recommendation: Add index on `search_term` column
```

**findings-tests.md:**
```markdown
# Test Coverage Review Findings

## Critical Issues
- Missing integration tests for payment flow (high-risk code path)
  - Recommendation: Add end-to-end test for checkout → payment → confirmation

## High Issues
- [posts.test.ts] Flaky test using `setTimeout(100)` timing assumption
  - Recommendation: Replace with explicit wait for condition
```

### Synthesized Review

**synthesis-review.md:**
```markdown
# Code Review Summary

## Executive Summary
3 critical issues found (1 security, 1 performance, 1 test coverage).
Recommend addressing critical issues before merge.

## Critical Issues (Must Fix)
1. [Security] SQL injection in auth.ts:42 → Use parameterized queries
2. [Performance] N+1 query in posts-service.ts:215 → Use JOIN
3. [Tests] Missing integration tests for payment flow → Add end-to-end test

## High Priority (Recommend Fix)
4 high-priority issues across security (1), performance (1), tests (2)
[See individual findings files for details]

## Medium Priority (Consider for Follow-up)
6 medium-priority improvements
[See individual findings files]

## Recommendations
1. Fix 3 critical issues before merge
2. Create follow-up tickets for 4 high-priority issues
3. Schedule tech debt sprint for medium-priority improvements
```

## Timing

**Sequential review:** ~45-60 minutes (15-20 min per domain)
**Parallel review:** ~20-25 minutes (all domains simultaneously)

**Speedup:** ~3x faster

## Cost Estimate

**Team:** 1 Opus lead + 3 Sonnet reviewers
**Duration:** ~20 minutes
**Estimated cost:** $12-18

## Variations

### Two-Reviewer Variant
If budget is tight, reduce to 2 reviewers:
- Security + Performance (skip test coverage)
- Security + Tests (skip performance)

Choose based on risk profile of changes.

### Five-Reviewer Deep Dive
For critical production changes, add:
- **Scalability Reviewer:** Load testing, capacity planning
- **Maintainability Reviewer:** Code clarity, documentation, tech debt

## Success Metrics

✅ **Successful if:**
- All 3 reviewers complete within 25 minutes
- Findings are actionable (file + line + recommendation)
- Synthesis prioritizes by severity
- No merge conflicts (reviewers only read, don't edit)

❌ **Red flags:**
- Reviewers editing same files (should be read-only)
- Generic findings without file/line references
- Lead synthesizing before teammates finish
- Findings overlap significantly (suggests unclear boundaries)

## Follow-Up Actions

After review:
1. Address critical issues immediately
2. Create tickets for high-priority issues (link to review findings)
3. Schedule follow-up for medium-priority items
4. Update review checklist based on common findings
