---
name: QA & Test Engineering Command Center
description: Complete quality assurance system — from test strategy to
  automation frameworks, coverage analysis, and release readiness. Works for any
  stack, any team size.
---

# QA & Test Engineering Command Center

Complete quality assurance system — from test strategy to automation frameworks, coverage analysis, and release readiness. Works for any stack, any team size.

## When to Use

- Planning test strategy for a new feature or project
- Writing unit, integration, or E2E tests
- Reviewing test quality and coverage gaps
- Setting up test automation and CI/CD quality gates
- Performance testing and load analysis
- Security testing checklist
- Bug triage and defect management
- Release readiness assessment

---

## Phase 1: Test Strategy

### Strategy Brief

Before writing any tests, define the strategy:

```yaml
# test-strategy.yaml
project: "[name]"
scope: "[feature/module/full product]"
risk_level: high | medium | low
stack:
  language: "[TypeScript/Python/Java/Go]"
  framework: "[React/Express/Django/Spring]"
  test_runner: "[Jest/Vitest/pytest/JUnit/Go test]"
  e2e_tool: "[Playwright/Cypress/Selenium]"

# What are we testing?
test_scope:
  - area: "[e.g., Auth module]"
    risk: high
    test_types: [unit, integration, e2e]
    priority: 1
  - area: "[e.g., Settings page]"
    risk: low
    test_types: [unit]
    priority: 3

# What's NOT in scope (and why)
exclusions:
  - "[e.g., Third-party widget — covered by vendor]"

# Quality targets
targets:
  line_coverage: 80
  branch_coverage: 70
  critical_path_coverage: 100
  max_flaky_rate: 2%
  max_test_duration_unit: 10ms
  max_test_duration_integration: 500ms
  max_test_duration_e2e: 30s
```

### Risk-Based Test Allocation

Not everything needs the same testing depth. Use the risk matrix:

| Risk Level | Unit Tests | Integration | E2E | Manual/Exploratory |
|-----------|-----------|-------------|-----|-------------------|
| **Critical** (payments, auth, data loss) | 95%+ coverage | Full API coverage | Happy + error paths | Exploratory session |
| **High** (core features, user-facing) | 85%+ coverage | Key integrations | Happy path | Spot check |
| **Medium** (secondary features) | 70%+ coverage | Critical paths only | Smoke only | On release |
| **Low** (admin, internal tools) | 50%+ coverage | None | None | None |

### Test Pyramid

Follow the pyramid — not the ice cream cone:

```
         /  E2E  \          ← Few (5-10%) — slow, expensive, brittle
        / Integr. \         ← Some (15-25%) — API contracts, DB queries
       /   Unit    \        ← Many (65-80%) — fast, isolated, cheap
```

**Anti-pattern: Ice cream cone** (mostly E2E, few unit tests) = slow CI, flaky builds, expensive maintenance.

**Decision rule:** Can this be tested at a lower level? → Test it there.

---

## Phase 2: Unit Testing

### Anatomy of a Good Unit Test

Every unit test follows AAA (Arrange-Act-Assert):

```
1. ARRANGE — Set up test data, mocks, state
2. ACT     — Call the function/method under test
3. ASSERT  — Verify the output matches expectations
```

### Unit Test Checklist (per function)

For each function/method, verify:

- [ ] **Happy path** — expected input → expected output
- [ ] **Edge cases** — empty input, null/undefined, zero, max values
- [ ] **Boundary values** — off-by-one, min-1, max+1
- [ ] **Error handling** — invalid input → correct error thrown
- [ ] **Return types** — correct type, shape, structure
- [ ] **Side effects** — does it modify state it shouldn't?
- [ ] **Idempotency** — calling twice gives same result?

### What to Mock (and What NOT to Mock)

**Mock these:**
- External APIs (HTTP calls, third-party services)
- Database queries (in unit tests only)
- File system operations
- Date/time (use fake timers)
- Random number generators
- Environment variables

**DO NOT mock these:**
- The function under test itself
- Pure utility functions (test them directly)
- Data transformations
- Simple value objects

**Mock rule of thumb:** If removing the mock would make the test hit the network, file system, or database → mock it. Otherwise → don't.

### Test Naming Convention

Use the pattern: `[unit] [scenario] [expected result]`

Examples:
- `calculateTotal returns 0 for empty cart`
- `validateEmail throws for missing @ symbol`
- `parseDate handles ISO 8601 with timezone offset`

### Coverage Analysis

**Metrics that matter:**
| Metric | Target | Why |
|--------|--------|-----|
| Line coverage | 80%+ | Basic completeness |
| Branch coverage | 70%+ | Catches missed if/else paths |
| Function coverage | 90%+ | Ensures all functions are tested |
| Critical path coverage | 100% | Business-critical code fully verified |

**Coverage traps to avoid:**
- 100% line coverage ≠ good tests (assertions matter more than lines hit)
- Coverage on generated code inflates numbers
- Trivial getters/setters pad coverage without value
- Coverage should INCREASE over time, never decrease

---

## Phase 3: Integration Testing

### What Integration Tests Cover

Integration tests verify that components work TOGETHER:

- API endpoint → middleware → handler → database → response
- Service A calls Service B and handles the response
- Message queue producer → consumer → side effect
- Auth flow: login → token → authenticated request

### Integration Test Patterns

**Pattern 1: API Contract Testing**
```
1. Start test server (or use supertest/httptest)
2. Send HTTP request with specific payload
3. Assert: status code, response body shape, headers
4. Assert: database state changed correctly
5. Assert: side effects triggered (emails, events)
```

**Pattern 2: Database Integration**
```
1. Start test database (SQLite in-memory or test container)
2. Run migrations
3. Seed test data
4. Execute query/operation
5. Assert: data matches expectations
6. Teardown (truncate or rollback transaction)
```

**Pattern 3: External Service**
```
1. Record real API response (VCR/nock/wiremock)
2. Replay recorded response in tests
3. Assert: your code handles the response correctly
4. Also test: timeout, 500 error, malformed response
```

### Integration Test Checklist

- [ ] **Happy path** — full flow works end-to-end
- [ ] **Auth** — unauthenticated returns 401, wrong role returns 403
- [ ] **Validation** — bad payload returns 400 with error details
- [ ] **Not found** — missing resource returns 404
- [ ] **Conflict** — duplicate create returns 409
- [ ] **Rate limiting** — excessive requests return 429
- [ ] **Database constraints** — unique violations, foreign keys
- [ ] **Concurrency** — two simultaneous writes don't corrupt data
- [ ] **Timeout handling** — external service timeout → graceful fallback

---

## Phase 4: End-to-End (E2E) Testing

### E2E Strategy

E2E tests verify complete user journeys. They're expensive — be strategic:

**Test these E2E:**
- User registration → email verification → first login
- Purchase flow → payment → confirmation
- Critical business workflows (the ones that make money)
- Cross-browser/device smoke tests

**DON'T test these E2E:**
- Individual form validations (unit test)
- API error handling (integration test)
- Edge cases (lower-level tests)
- Visual styling (visual regression tools)

### E2E Test Template

```yaml
test_name: "[User journey name]"
preconditions:
  - "[User is logged in]"
  - "[Product exists in catalog]"
steps:
  - action: "Navigate to /products"
    verify: "Product list is visible"
  - action: "Click 'Add to Cart' on Product A"
    verify: "Cart badge shows 1"
  - action: "Click 'Checkout'"
    verify: "Checkout form displayed"
  - action: "Fill payment details and submit"
    verify: "Order confirmation page with order ID"
postconditions:
  - "Order exists in database with status 'paid'"
  - "Confirmation email sent"
max_duration: 30s
```

### Flaky Test Management

Flaky tests are the #1 CI killer. Handle them:

**Flaky Test Triage:**
1. **Identify** — Track test pass rates over 10+ runs
2. **Classify** — Why is it flaky?
   - Timing/race condition → Add explicit waits, not sleep()
   - Test data dependency → Isolate test data per run
   - External service → Mock it or use test container
   - Browser rendering → Use visibility checks, not delays
3. **Quarantine** — Move to @flaky suite, run separately
4. **Fix or delete** — Flaky test unfixed for 2 weeks → delete it

**Flaky rate target:** < 2% of total test runs

---

## Phase 5: Performance Testing

### Performance Test Types

| Type | Purpose | When |
|------|---------|------|
| **Load test** | Normal traffic handling | Before every release |
| **Stress test** | Find breaking point | Quarterly or before scaling |
| **Spike test** | Sudden traffic burst | Before marketing campaigns |
| **Soak test** | Memory leaks over time | Monthly or after major changes |
| **Capacity test** | Max users/throughput | Planning infrastructure |

### Performance Test Plan

```yaml
test_name: "[API/Page] Load Test"
target: "[URL or endpoint]"
baseline:
  p50_response: "[current p50 ms]"
  p95_response: "[current p95 ms]"
  p99_response: "[current p99 ms]"
  error_rate: "[current %]"

scenarios:
  - name: "Normal load"
    vus: 50          # virtual users
    duration: 5m
    ramp_up: 30s
    thresholds:
      p95_response: "< 500ms"
      error_rate: "< 1%"

  - name: "Peak load"
    vus: 200
    duration: 10m
    ramp_up: 1m
    thresholds:
      p95_response: "< 2000ms"
      error_rate: "< 5%"

  - name: "Stress test"
    vus: 500
    duration: 5m
    ramp_up: 2m
    # Find the breaking point — no thresholds, observe
```

### Performance Metrics Dashboard

Track these per endpoint:

| Metric | Green | Yellow | Red |
|--------|-------|--------|-----|
| p50 response | < 200ms | 200-500ms | > 500ms |
| p95 response | < 500ms | 500ms-2s | > 2s |
| p99 response | < 1s | 1-5s | > 5s |
| Error rate | < 0.1% | 0.1-1% | > 1% |
| Throughput | > baseline | 80-100% baseline | < 80% |
| CPU usage | < 60% | 60-80% | > 80% |
| Memory usage | < 70% | 70-85% | > 85% |
| DB query time | < 50ms avg | 50-200ms | > 200ms |

### Common Performance Fixes

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| Slow API response | N+1 queries | Batch/join queries |
| Memory climbing | Object retention | Profile heap, fix leaks |
| Timeout spikes | Connection pool exhaustion | Increase pool, add queuing |
| Slow page load | Large bundle | Code split, lazy load |
| DB bottleneck | Missing index | Add index on WHERE/JOIN columns |
| High CPU | Synchronous compute | Move to worker/queue |

---

## Phase 6: Security Testing

### Security Test Checklist

Run through these for every feature/release:

**Authentication & Authorization:**
- [ ] Passwords hashed with bcrypt/argon2 (not MD5/SHA1)
- [ ] Session tokens are random, sufficient length (128+ bits)
- [ ] JWT tokens have short expiry (15 min access, 7 day refresh)
- [ ] Failed login rate limiting (5 attempts → lockout)
- [ ] Password reset tokens expire (1 hour max)
- [ ] Role-based access enforced server-side (not just UI)
- [ ] Can't access other users' data by changing IDs in URL

**Input Validation:**
- [ ] SQL injection — parameterized queries everywhere
- [ ] XSS — output encoding, CSP headers
- [ ] CSRF — tokens on state-changing requests
- [ ] Path traversal — validate file paths, no `../`
- [ ] Command injection — never pass user input to shell
- [ ] File upload — validate type, size, scan for malware
- [ ] JSON/XML parsing — depth limits, entity expansion disabled

**Data Protection:**
- [ ] HTTPS everywhere (HSTS header)
- [ ] Sensitive data encrypted at rest
- [ ] PII not logged (mask in log output)
- [ ] API keys not in client-side code
- [ ] CORS configured correctly (not `*`)
- [ ] Security headers set (X-Frame-Options, X-Content-Type-Options)

**Infrastructure:**
- [ ] Dependencies scanned for CVEs (npm audit / pip audit)
- [ ] Docker images scanned (Trivy/Snyk)
- [ ] Secrets not in code/env files (use vault)
- [ ] Error messages don't leak internals
- [ ] Admin endpoints behind VPN/IP allowlist

### OWASP Top 10 Quick Reference

| # | Vulnerability | Test For |
|---|--------------|----------|
| A01 | Broken Access Control | Access other users' resources, bypass role checks |
| A02 | Cryptographic Failures | Weak hashing, plaintext secrets, expired certs |
| A03 | Injection | SQL, XSS, command, LDAP injection |
| A04 | Insecure Design | Business logic flaws, missing rate limits |
| A05 | Security Misconfiguration | Default creds, verbose errors, open ports |
| A06 | Vulnerable Components | Outdated deps with known CVEs |
| A07 | Authentication Failures | Brute force, weak passwords, session fixation |
| A08 | Data Integrity Failures | Unsigned updates, CI/CD pipeline injection |
| A09 | Logging Failures | Missing audit logs, no alerting on breaches |
| A10 | SSRF | Internal network access via user-controlled URLs |

---

## Phase 7: Bug Triage & Defect Management

### Bug Report Template

```yaml
bug_id: "[auto or manual]"
title: "[Short description of the bug]"
severity: P0-critical | P1-high | P2-medium | P3-low
reporter: "[name]"
date: "[YYYY-MM-DD]"

environment:
  os: "[OS + version]"
  browser: "[Browser + version]"
  app_version: "[version/commit]"
  
steps_to_reproduce:
  1. "[Step 1]"
  2. "[Step 2]"
  3. "[Step 3]"

expected_result: "[What should happen]"
actual_result: "[What actually happens]"
frequency: "always | intermittent | once"
screenshots: "[links]"
logs: "[relevant log output]"
```

### Severity Classification

| Level | Definition | SLA | Example |
|-------|-----------|-----|---------|
| **P0 Critical** | System down, data loss, security breach | Fix in 4 hours | Payment processing broken |
| **P1 High** | Major feature broken, no workaround | Fix in 24 hours | Users can't login |
| **P2 Medium** | Feature broken with workaround | Fix this sprint | Search returns wrong results sometimes |
| **P3 Low** | Minor issue, cosmetic | Fix when convenient | Button alignment off by 2px |

### Bug Triage Process (Weekly)

```
1. Review all new bugs (unassigned)
2. For each bug:
   a. Reproduce — can you trigger it?
   b. Classify severity (P0-P3)
   c. Estimate fix effort (S/M/L)
   d. Assign to owner + sprint
   e. Link to related bugs/stories
3. Review P0/P1 bugs from last week — are they fixed?
4. Close bugs that can't be reproduced (after 2 attempts)
5. Update metrics dashboard
```

### Bug Metrics Dashboard

Track weekly:

| Metric | Formula | Target |
|--------|---------|--------|
| Bug escape rate | Bugs found in prod / total bugs | < 10% |
| Mean time to fix (P0) | Avg hours from report to deploy | < 8 hours |
| Mean time to fix (P1) | Avg hours from report to deploy | < 48 hours |
| Bug reopen rate | Reopened bugs / closed bugs | < 5% |
| Test escape analysis | Bugs that SHOULD have been caught | Track & reduce |
| Open bug count | Total open by severity | Trending down |

---

## Phase 8: Release Readiness

### Release Checklist

Before shipping to production:

**Code Quality:**
- [ ] All unit tests passing
- [ ] All integration tests passing
- [ ] E2E smoke suite passing
- [ ] No new lint warnings/errors
- [ ] Code reviewed and approved
- [ ] No known P0/P1 bugs open for this release

**Coverage & Quality Gates:**
- [ ] Line coverage ≥ target (80%)
- [ ] Branch coverage ≥ target (70%)
- [ ] No coverage decrease from last release
- [ ] Mutation testing score ≥ 60% (if applicable)

**Performance:**
- [ ] Load test passed (within thresholds)
- [ ] No performance regressions vs baseline
- [ ] Bundle size within budget

**Security:**
- [ ] Dependency audit clean (no critical/high CVEs)
- [ ] Security checklist completed
- [ ] Secrets rotated if needed

**Operational Readiness:**
- [ ] Monitoring/alerts configured for new features
- [ ] Rollback plan documented
- [ ] Feature flags in place for risky changes
- [ ] Database migration tested and reversible
- [ ] Runbook updated

### Release Readiness Score

Score 0-100 across 5 dimensions:

| Dimension | Weight | Scoring |
|-----------|--------|---------|
| **Test coverage** | 25% | 100 if targets met, -10 per gap area |
| **Bug status** | 25% | 100 if 0 P0/P1, -20 per open P0, -10 per P1 |
| **Performance** | 20% | 100 if all green, -15 per yellow, -30 per red |
| **Security** | 20% | 100 if clean, -25 per critical, -15 per high |
| **Operational** | 10% | 100 if checklist complete, -20 per missing item |

**Ship threshold: ≥ 80 overall, no dimension below 60**

---

## Phase 9: CI/CD Quality Gates

### Pipeline Quality Gates

Configure these gates in your CI pipeline:

```yaml
# Quality gate configuration
gates:
  - name: "Lint"
    stage: pre-commit
    command: "npm run lint"
    blocking: true
    
  - name: "Unit Tests"
    stage: commit
    command: "npm test -- --coverage"
    blocking: true
    thresholds:
      pass_rate: 100%
      coverage_line: 80%
      coverage_branch: 70%
      
  - name: "Integration Tests"
    stage: merge
    command: "npm run test:integration"
    blocking: true
    thresholds:
      pass_rate: 100%
      
  - name: "Security Scan"
    stage: merge
    command: "npm audit --audit-level=high"
    blocking: true
    
  - name: "E2E Smoke"
    stage: staging
    command: "npm run test:e2e:smoke"
    blocking: true
    thresholds:
      pass_rate: 100%
      
  - name: "Performance"
    stage: staging
    command: "npm run test:perf"
    blocking: false  # Alert only
    thresholds:
      p95_regression: 20%
```

### Test Automation Maturity Model

Rate your team 1-5:

| Level | Description | Characteristics |
|-------|------------|-----------------|
| **1 — Manual** | All testing is manual | No automation, long release cycles |
| **2 — Reactive** | Some unit tests, no CI | Tests written after bugs, not before |
| **3 — Structured** | Test pyramid, CI pipeline | Unit + integration, automated on push |
| **4 — Proactive** | Full automation, quality gates | E2E + perf + security in pipeline, TDD |
| **5 — Optimized** | Self-healing, predictive | Flaky auto-quarantine, AI-assisted testing, continuous deployment |

---

## Phase 10: Test Maintenance

### Weekly Test Health Review

```yaml
review_date: "[YYYY-MM-DD]"

metrics:
  total_tests: 0
  pass_rate_7d: "0%"
  flaky_tests: 0
  flaky_rate: "0%"
  avg_suite_duration: "0s"
  coverage_line: "0%"
  coverage_branch: "0%"
  
actions:
  quarantined: []     # Tests moved to flaky suite
  deleted: []         # Tests removed (obsolete/unfixable)
  fixed: []           # Flaky tests fixed this week
  added: []           # New tests added
  
trends:
  coverage_delta: "+0%"     # vs last week
  flaky_delta: "+0"         # vs last week
  duration_delta: "+0s"     # vs last week
  
notes: ""
```

### Test Maintenance Rules

1. **No commented-out tests** — delete or fix, never comment
2. **No skipped tests > 2 weeks** — fix or remove
3. **No test duplication** — each behavior tested once at the right level
4. **Test names must be readable** — someone new should understand what broke
5. **Shared test utilities** — common setup in fixtures/factories, not copy-pasted
6. **Test data isolation** — each test creates its own data, cleans up after
7. **No magic numbers** — use named constants in assertions
8. **Assertion messages** — custom messages on complex assertions

### Common Test Anti-Patterns

| Anti-Pattern | Problem | Fix |
|-------------|---------|-----|
| **Sleeping tests** | `sleep(2000)` instead of waiting | Use explicit waits/polling |
| **Test interdependence** | Test B relies on Test A's state | Isolate — each test sets up its own state |
| **Assertionless tests** | Test runs code but doesn't assert | Add meaningful assertions |
| **Brittle selectors** | CSS selectors that break on redesign | Use data-testid or aria roles |
| **God test** | One test verifying 20 things | Split into focused tests |
| **Mock overload** | Everything mocked, nothing real tested | Only mock external boundaries |
| **Hardcoded data** | Tests break when seed data changes | Use factories/builders |
| **Ignoring test output** | "It passed, ship it" | Review WHY it passed — is the assertion meaningful? |

---

## Quick Reference: Natural Language Commands

Tell the agent:
- **"Create test strategy for [feature]"** → Generates strategy brief
- **"Write unit tests for [function/file]"** → AAA-structured tests with edge cases
- **"Review test coverage for [module]"** → Gap analysis + recommendations
- **"Write integration tests for [API endpoint]"** → Full HTTP test suite
- **"Plan E2E tests for [user journey]"** → E2E test template
- **"Run security checklist for [feature]"** → OWASP-based security review
- **"Triage these bugs: [list]"** → Severity classification + assignment
- **"Release readiness check"** → Full readiness score + blockers
- **"Performance test plan for [endpoint]"** → Load/stress test configuration
- **"Fix flaky test [name]"** → Root cause analysis + fix strategy
