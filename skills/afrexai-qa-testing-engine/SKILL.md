---
name: QA & Testing Engine — Complete Software Quality System
description: Before writing a single test, design the strategy.
---

# QA & Testing Engine — Complete Software Quality System

> The definitive testing methodology for AI agents. From test strategy to execution, coverage to reporting — everything you need to ship quality software.

## Phase 1: Test Strategy Design

Before writing a single test, design the strategy.

### Strategy Brief Template

```yaml
project:
  name: ""
  type: web-app | api | mobile | library | cli | data-pipeline
  languages: [typescript, python, go, java]
  frameworks: [react, express, django, spring]
  
risk_profile:
  data_sensitivity: low | medium | high | critical  # PII, financial, health
  user_impact: internal | b2b | b2c | life-safety
  deployment_frequency: daily | weekly | monthly
  regulatory: [none, SOC2, HIPAA, PCI-DSS, GDPR]

test_scope:
  in_scope: []    # Features, services, components
  out_of_scope: [] # Explicitly excluded (with reason)
  
environments:
  dev: { url: "", db: "local" }
  staging: { url: "", db: "seeded" }
  prod: { url: "", smoke_only: true }
```

### Test Type Decision Matrix

| Risk Profile | Unit | Integration | E2E | Performance | Security | Accessibility |
|---|---|---|---|---|---|---|
| Internal tool | ✅ Core | ✅ API | ⚠️ Happy path | ❌ | ⚠️ Basic | ❌ |
| B2B SaaS | ✅ Full | ✅ Full | ✅ Critical flows | ✅ Load | ✅ OWASP Top 10 | ✅ WCAG AA |
| B2C high-traffic | ✅ Full | ✅ Full | ✅ Full | ✅ Stress + soak | ✅ Full | ✅ WCAG AA |
| Financial/Health | ✅ Full + mutation | ✅ Full + contract | ✅ Full + chaos | ✅ Full suite | ✅ Pen test | ✅ WCAG AAA |

### Test Pyramid Architecture

```
         /  E2E  \          5-10% — Critical user journeys only
        / Integration \     20-30% — API contracts, service boundaries
       /    Unit Tests   \  60-70% — Business logic, pure functions
```

**Anti-pattern: Ice cream cone** — More E2E than unit tests. Slow, flaky, expensive. Fix by pushing test coverage DOWN the pyramid.

**Anti-pattern: Hourglass** — Lots of unit + E2E, no integration. Misses contract bugs between services.

---

## Phase 2: Unit Testing Mastery

### The AAA Pattern (Arrange-Act-Assert)

Every unit test follows this structure:

```typescript
describe('PricingCalculator', () => {
  // Group by behavior, not by method
  describe('when customer has volume discount', () => {
    it('applies tiered pricing above threshold', () => {
      // ARRANGE — Set up the scenario
      const calculator = new PricingCalculator();
      const customer = createCustomer({ tier: 'enterprise', units: 150 });
      
      // ACT — Execute the behavior under test
      const price = calculator.calculate(customer);
      
      // ASSERT — Verify the outcome (ONE logical assertion)
      expect(price).toEqual({
        subtotal: 12000,
        discount: 1800,  // 15% volume discount
        total: 10200,
      });
    });
  });
});
```

### Test Naming Convention

**Format:** `[unit] [scenario] [expected behavior]`

✅ Good:
- `PricingCalculator applies 15% discount when units exceed 100`
- `UserService throws NotFoundError when user ID is invalid`
- `parseDate returns null for malformed ISO strings`

❌ Bad:
- `test1`, `should work`, `calculates price`

### What to Unit Test (Priority Order)

1. **Business logic** — Pricing, rules, calculations, state machines
2. **Data transformations** — Parsers, formatters, serializers, mappers
3. **Edge cases** — Boundaries, null/undefined, empty collections, overflow
4. **Error handling** — Every `catch` block, every validation path
5. **Pure functions** — Easiest to test, highest ROI

### What NOT to Unit Test

- Framework internals (React rendering, Express routing)
- Simple getters/setters with no logic
- Third-party library behavior
- Implementation details (private methods, internal state)

### Mocking Rules

| Dependency Type | Strategy | Example |
|---|---|---|
| Database | Mock the repository/DAO | `jest.mock('./userRepo')` |
| HTTP API | Mock the client or use MSW | `msw.http.get('/api/users', ...)` |
| File system | Mock fs or use temp dirs | `jest.mock('fs/promises')` |
| Time/Date | Fake timers | `jest.useFakeTimers()` |
| Randomness | Seed or mock | `jest.spyOn(Math, 'random')` |
| Environment | Override env vars | `process.env.NODE_ENV = 'test'` |

**Rule: Mock at boundaries, not internals.** If you're mocking a class you own, your design might need refactoring.

### Coverage Targets

| Metric | Minimum | Good | Excellent |
|---|---|---|---|
| Line coverage | 70% | 85% | 95%+ |
| Branch coverage | 60% | 80% | 90%+ |
| Function coverage | 75% | 90% | 95%+ |
| Critical path coverage | 100% | 100% | 100% |

**Warning:** 100% coverage ≠ quality. Coverage measures what code ran, not what was verified. A test with no assertions has coverage but no value.

---

## Phase 3: Integration Testing

### API Testing Checklist

For every API endpoint, test:

```yaml
endpoint: POST /api/orders
tests:
  happy_path:
    - Valid request returns 201 with order ID
    - Response matches schema
    - Database record created correctly
    - Events/webhooks fired
    
  validation:
    - Missing required fields → 400 with field errors
    - Invalid data types → 400 with type errors
    - Business rule violations → 422 with explanation
    
  authentication:
    - No token → 401
    - Expired token → 401
    - Wrong role → 403
    - Valid token → proceeds
    
  edge_cases:
    - Duplicate request (idempotency) → same response
    - Concurrent requests → no race condition
    - Maximum payload size → 413 or graceful handling
    - Special characters in input → no injection
    
  error_handling:
    - Database down → 503 with retry hint
    - External service timeout → 504 or fallback
    - Rate limit exceeded → 429 with retry-after
```

### Contract Testing

When services communicate, test the contract:

```yaml
contract:
  consumer: order-service
  provider: payment-service
  
  interactions:
    - description: "Process payment"
      request:
        method: POST
        path: /payments
        body:
          amount: 99.99
          currency: USD
          order_id: "ord_123"
      response:
        status: 200
        body:
          payment_id: "pay_xxx"  # string, not null
          status: "completed"    # enum: completed|pending|failed
          
  breaking_changes:  # NEVER do these without versioning
    - Remove a field from response
    - Change a field's type
    - Add a required field to request
    - Change the URL path
    - Change error response format
```

### Database Testing Rules

1. **Each test gets a clean state** — Use transactions that rollback, or truncate between tests
2. **Use factories, not fixtures** — `createUser({ role: 'admin' })` > hardcoded SQL dumps
3. **Test migrations** — Run migrate-up, migrate-down, migrate-up (roundtrip)
4. **Test constraints** — Unique violations, FK cascades, NOT NULL
5. **Test queries** — Especially complex JOINs, aggregations, window functions

---

## Phase 4: End-to-End Testing

### Critical User Journey Mapping

Identify and test the flows that generate revenue or block users:

```yaml
critical_journeys:
  - name: "Sign up → First value"
    steps:
      - Visit landing page
      - Click sign up
      - Fill registration form
      - Verify email
      - Complete onboarding
      - Perform first key action
    max_duration: 3 minutes
    
  - name: "Purchase flow"
    steps:
      - Browse products
      - Add to cart
      - Enter shipping
      - Enter payment
      - Confirm order
      - Receive confirmation email
    max_duration: 2 minutes
    
  - name: "Login → Core task → Logout"
    steps:
      - Login (password + SSO + MFA variants)
      - Navigate to core feature
      - Complete primary workflow
      - Verify result
      - Logout
    max_duration: 1 minute
```

### E2E Best Practices

1. **Test user behavior, not implementation** — Click buttons by text/role, not by CSS class
2. **Use data-testid sparingly** — Only when no accessible selector exists
3. **Wait for state, not time** — `waitFor(element)` not `sleep(3000)`
4. **Isolate test data** — Each test creates its own users/data
5. **Run in CI with retries** — 1 retry for flaky network, investigate if >5% flake rate

### Selector Priority (Best → Worst)

1. `getByRole('button', { name: 'Submit' })` — Accessible, resilient
2. `getByLabelText('Email')` — Form-specific, accessible
3. `getByText('Welcome back')` — Content-based
4. `getByTestId('submit-btn')` — Explicit test hook
5. `querySelector('.btn-primary')` — ❌ Fragile, breaks on CSS changes

### Flaky Test Triage

| Symptom | Likely Cause | Fix |
|---|---|---|
| Passes locally, fails in CI | Timing/race condition | Add explicit waits, check CI resource limits |
| Fails intermittently | Shared state between tests | Isolate test data, reset state |
| Fails after deploy | Environment difference | Check env vars, API versions, feature flags |
| Fails at specific time | Time-dependent logic | Mock dates/times, avoid time-sensitive assertions |
| Fails in parallel | Resource contention | Use unique ports/DBs per worker |

**Rule: Quarantine flaky tests within 24 hours.** A flaky test suite that everyone ignores is worse than no tests.

---

## Phase 5: Performance Testing

### Load Test Design

```yaml
performance_tests:
  smoke:
    vus: 5
    duration: 1m
    purpose: "Verify test works"
    
  load:
    vus: 100  # Expected concurrent users
    duration: 10m
    ramp_up: 2m
    purpose: "Normal traffic behavior"
    thresholds:
      p95_response: <500ms
      error_rate: <1%
      
  stress:
    vus: 300  # 3x expected load
    duration: 15m
    ramp_up: 5m
    purpose: "Find breaking point"
    
  soak:
    vus: 80
    duration: 2h
    purpose: "Memory leaks, connection exhaustion"
    
  spike:
    stages:
      - { vus: 50, duration: 2m }
      - { vus: 500, duration: 30s }  # Sudden spike
      - { vus: 50, duration: 2m }
    purpose: "Recovery behavior"
```

### Performance Budgets

| Metric | Web App | API | Background Job |
|---|---|---|---|
| Response time (p50) | <200ms | <100ms | N/A |
| Response time (p95) | <1s | <500ms | N/A |
| Response time (p99) | <3s | <1s | N/A |
| Throughput | >100 rps | >500 rps | >1000/min |
| Error rate | <0.1% | <0.1% | <0.5% |
| CPU usage | <70% | <70% | <90% |
| Memory growth | <5%/hr | <2%/hr | <10%/hr |

### Database Performance Testing

```yaml
db_performance:
  query_tests:
    - name: "Dashboard aggregate query"
      baseline: 50ms
      max_acceptable: 200ms
      with_1M_rows: measure
      with_10M_rows: measure
      
  index_verification:
    - Run EXPLAIN ANALYZE on all critical queries
    - Verify no sequential scans on tables >10K rows
    - Check index usage statistics weekly
    
  connection_pool:
    - Test at max connections
    - Verify graceful handling when pool exhausted
    - Monitor connection wait time
```

---

## Phase 6: Security Testing

### OWASP Top 10 Test Checklist

```yaml
security_tests:
  A01_broken_access_control:
    - [ ] Horizontal privilege escalation (access other user's data)
    - [ ] Vertical privilege escalation (access admin functions)
    - [ ] IDOR (Insecure Direct Object References)
    - [ ] Missing function-level access control
    - [ ] CORS misconfiguration
    
  A02_cryptographic_failures:
    - [ ] Sensitive data in transit (TLS 1.2+)
    - [ ] Sensitive data at rest (encryption)
    - [ ] Password hashing (bcrypt/argon2, not MD5/SHA)
    - [ ] No secrets in code/logs/URLs
    
  A03_injection:
    - [ ] SQL injection (parameterized queries)
    - [ ] NoSQL injection
    - [ ] Command injection (OS commands)
    - [ ] XSS (stored, reflected, DOM-based)
    - [ ] Template injection (SSTI)
    
  A04_insecure_design:
    - [ ] Rate limiting on auth endpoints
    - [ ] Account lockout after N failures
    - [ ] CAPTCHA on public forms
    - [ ] Business logic abuse scenarios
    
  A05_security_misconfiguration:
    - [ ] Default credentials removed
    - [ ] Error messages don't leak stack traces
    - [ ] Security headers set (CSP, HSTS, X-Frame-Options)
    - [ ] Directory listing disabled
    - [ ] Unnecessary HTTP methods disabled
    
  A07_auth_failures:
    - [ ] Brute force protection
    - [ ] Session fixation
    - [ ] Session timeout
    - [ ] JWT validation (signature, expiry, issuer)
    - [ ] MFA bypass attempts
```

### Input Validation Test Payloads

Test every user input with:

```yaml
injection_payloads:
  sql: ["' OR 1=1--", "'; DROP TABLE users;--", "1 UNION SELECT * FROM users"]
  xss: ["<script>alert(1)</script>", "<img onerror=alert(1) src=x>", "javascript:alert(1)"]
  path_traversal: ["../../etc/passwd", "..\\..\\windows\\system32", "%2e%2e%2f"]
  command: ["; ls -la", "| cat /etc/passwd", "$(whoami)", "`id`"]
  
boundary_values:
  strings: ["", " ", "a"*10000, null, undefined, "emoji: 🎯", "unicode: é à ü", "rtl: مرحبا"]
  numbers: [0, -1, 2147483647, -2147483648, NaN, Infinity, 0.1+0.2]
  arrays: [[], [null], Array(10000)]
  dates: ["1970-01-01", "2099-12-31", "invalid-date", "2024-02-29", "2023-02-29"]
```

---

## Phase 7: Test Automation Architecture

### Framework Selection Guide

| Need | JavaScript/TS | Python | Go | Java |
|---|---|---|---|---|
| Unit | Vitest / Jest | pytest | testing + testify | JUnit 5 |
| API | Supertest | httpx + pytest | net/http/httptest | RestAssured |
| E2E (browser) | Playwright | Playwright | chromedp | Selenium |
| Performance | k6 | Locust | vegeta | Gatling |
| Contract | Pact | Pact | Pact | Pact |
| Security | ZAP + custom | Bandit + custom | gosec | SpotBugs |

### CI Pipeline Test Stages

```yaml
pipeline:
  stage_1_fast:  # <2 min, blocks PR
    - Lint + type check
    - Unit tests
    - Security: dependency scan (npm audit / safety)
    
  stage_2_thorough:  # <10 min, blocks merge
    - Integration tests
    - Contract tests
    - Security: SAST scan
    - Coverage report + threshold check
    
  stage_3_confidence:  # <30 min, blocks deploy
    - E2E critical journeys
    - Visual regression (if applicable)
    - Security: container scan
    
  stage_4_post_deploy:  # After deploy to staging
    - Smoke tests against staging
    - Performance baseline check
    - Security: DAST scan (ZAP)
    
  stage_5_production:  # After prod deploy
    - Smoke tests (critical paths only)
    - Synthetic monitoring enabled
    - Canary metrics watching
```

### Test Data Management

```yaml
test_data_strategy:
  unit_tests:
    approach: factories  # Builder pattern, create exactly what you need
    example: "createUser({ role: 'admin', plan: 'enterprise' })"
    
  integration_tests:
    approach: seeded_database
    reset: per_test_suite  # Transaction rollback or truncate
    sensitive_data: anonymized  # Never use real PII
    
  e2e_tests:
    approach: api_setup  # Create data via API before test
    cleanup: after_each  # Delete created data
    isolation: unique_identifiers  # Timestamp or UUID in test data
    
  performance_tests:
    approach: representative_dataset
    volume: 10x_production  # Test with more data than prod
    generation: faker_libraries  # Realistic but synthetic
```

---

## Phase 8: Quality Metrics & Reporting

### Test Health Dashboard

```yaml
metrics:
  test_suite_health:
    total_tests: 0
    passing: 0
    failing: 0
    skipped: 0  # >5% skipped = tech debt alarm
    flaky: 0    # >2% flaky = quarantine immediately
    
  coverage:
    line: "0%"
    branch: "0%"
    critical_paths: "0%"  # Must be 100%
    
  execution:
    unit_duration: "0s"    # Target: <30s
    integration_duration: "0s"  # Target: <5m
    e2e_duration: "0s"     # Target: <15m
    total_ci_time: "0s"    # Target: <20m
    
  defect_metrics:
    bugs_found_in_test: 0
    bugs_escaped_to_prod: 0
    escape_rate: "0%"      # Target: <5%
    mttr: "0h"             # Mean time to resolve
    
  trends:  # Track weekly
    new_tests_added: 0
    tests_deleted: 0  # Healthy deletion = removing redundant tests
    coverage_delta: "+0%"
    flake_rate_delta: "+0%"
```

### Test Report Template

```markdown
# Test Report — [Feature/Sprint/Release]

## Summary
- **Status:** ✅ PASS / ⚠️ PASS WITH RISKS / ❌ FAIL
- **Tests Run:** X | **Passed:** X | **Failed:** X | **Skipped:** X
- **Coverage:** Line X% | Branch X% | Critical 100%
- **Duration:** Xm Xs

## Key Findings

### 🔴 Critical (Block Release)
1. [Finding] — [Impact] — [Fix recommendation]

### 🟡 High (Fix Before Next Release)
1. [Finding] — [Impact] — [Fix recommendation]

### 🟢 Medium/Low (Backlog)
1. [Finding] — [Impact]

## Risk Assessment
- **Untested areas:** [list]
- **Known flaky tests:** [list with ticket IDs]
- **Performance concerns:** [if any]

## Recommendation
[Ship / Ship with monitoring / Hold for fixes]
```

### Quality Score (0-100)

| Dimension | Weight | Scoring |
|---|---|---|
| Test coverage | 20% | <60%=0, 60-70%=5, 70-80%=10, 80-90%=15, 90%+=20 |
| Critical path coverage | 20% | <100%=0, 100%=20 |
| Defect escape rate | 15% | >10%=0, 5-10%=5, 2-5%=10, <2%=15 |
| Test suite speed | 10% | >30m=0, 20-30m=3, 10-20m=7, <10m=10 |
| Flake rate | 10% | >5%=0, 2-5%=3, 1-2%=7, <1%=10 |
| Security test coverage | 10% | None=0, Basic=3, OWASP Top 10=7, Full=10 |
| Documentation | 5% | None=0, Basic=2, Complete=5 |
| Automation ratio | 10% | <50%=0, 50-70%=3, 70-90%=7, 90%+=10 |

**Scoring:** 0-40 = 🔴 Critical | 41-60 = 🟡 Needs Work | 61-80 = 🟢 Good | 81-100 = 💎 Excellent

---

## Phase 9: Specialized Testing

### Accessibility Testing (WCAG 2.1)

```yaml
accessibility_checklist:
  level_a:  # Minimum compliance
    - [ ] All images have alt text
    - [ ] All form inputs have labels
    - [ ] Color is not the only visual indicator
    - [ ] Page has proper heading hierarchy (h1→h2→h3)
    - [ ] All functionality available via keyboard
    - [ ] Focus is visible and logical
    - [ ] No content flashes >3 times/second
    
  level_aa:  # Standard compliance (recommended)
    - [ ] Color contrast ratio ≥4.5:1 (normal text)
    - [ ] Color contrast ratio ≥3:1 (large text)
    - [ ] Text resizable to 200% without loss
    - [ ] Skip navigation links
    - [ ] Consistent navigation across pages
    - [ ] Error suggestions provided
    - [ ] ARIA landmarks for page regions
    
  tools:
    - axe-core (automated, catches ~30% of issues)
    - Lighthouse accessibility audit
    - Manual keyboard navigation test
    - Screen reader testing (VoiceOver/NVDA)
```

### API Backward Compatibility Testing

```yaml
compatibility_tests:
  when_updating_api:
    - [ ] All existing fields still present in response
    - [ ] No field type changes (string→number)
    - [ ] New required request fields have defaults
    - [ ] Deprecated fields still work (with warning header)
    - [ ] Error format unchanged
    - [ ] Pagination behavior unchanged
    - [ ] Rate limits not reduced
    
  versioning_strategy:
    - URL versioning: /v1/users, /v2/users
    - Header versioning: Accept: application/vnd.api+json;version=2
    - Sunset header for deprecated versions
    - Minimum 6-month deprecation notice
```

### Chaos Engineering Principles

```yaml
chaos_tests:
  network:
    - Service dependency goes down → graceful degradation?
    - Network latency increases 10x → timeout handling?
    - DNS resolution fails → fallback behavior?
    
  infrastructure:
    - Database primary fails → replica promotion?
    - Cache (Redis) goes down → DB fallback works?
    - Disk fills up → alerting + graceful failure?
    
  application:
    - Memory pressure → OOM handling?
    - CPU saturation → request queuing?
    - Certificate expiry → monitoring alert?
    
  data:
    - Corrupt message in queue → dead letter + alert?
    - Schema migration fails mid-way → rollback works?
    - Clock skew between services → idempotency holds?
```

---

## Phase 10: Daily QA Workflow

### For New Features

1. **Review requirements** — Identify test scenarios before code is written (shift-left)
2. **Write test cases** — Cover happy path, edge cases, error cases, security
3. **Review PR tests** — Are tests meaningful? Do they test behavior, not implementation?
4. **Run full suite** — Unit + integration + E2E for affected areas
5. **Report findings** — Use the test report template above

### For Bug Fixes

1. **Write failing test first** — Reproduce the bug as a test
2. **Verify fix makes test pass** — The test IS the proof
3. **Check for regression** — Run related test suites
4. **Add to regression suite** — Bug tests prevent re-introduction

### Weekly QA Review

```yaml
weekly_review:
  monday:
    - Review flaky test quarantine — fix or delete
    - Check coverage trends — declining = tech debt
    - Review escaped defects — update test strategy
    
  friday:
    - Update test health dashboard
    - Clean up obsolete tests
    - Document new testing patterns discovered
    - Plan next week's testing focus
```

### Natural Language Commands

- `"Create test strategy for [project/feature]"` → Full strategy brief
- `"Write unit tests for [function/class]"` → AAA pattern tests with edge cases
- `"Test this API endpoint: [method] [path]"` → Full API test checklist
- `"Review these tests for quality"` → Test code review with scoring
- `"Generate performance test plan"` → k6/Locust test design
- `"Security test [feature/endpoint]"` → OWASP-based test checklist
- `"Create test report for [release]"` → Formatted test report
- `"What's our test health?"` → Dashboard with metrics and recommendations
- `"Find gaps in our test coverage"` → Analysis with prioritized recommendations
- `"Help debug this flaky test"` → Root cause analysis with fix suggestions
- `"Set up CI test pipeline"` → Stage-by-stage pipeline config
- `"Accessibility audit [page/component]"` → WCAG checklist with findings
