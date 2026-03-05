---
name: test-driven-development
description: Write failing test first, then implement minimal code to pass, then refactor — no production code without a failing test
---

# Test-Driven Development — Red, Green, Refactor

## Iron Law

NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST.

If you're about to write implementation code, STOP. Write the test first.

## The Cycle

### 1. RED — Write a Failing Test

Write a test that describes the behavior you want:

```typescript
describe('GET /api/resource', () => {
  it('returns items filtered by scope', async () => {
    const response = await fetch('/api/resource?scope=test')
    const data = await response.json()
    expect(data.success).toBe(true)
    expect(data.items).toBeDefined()
  })
})
```

```python
def test_calculate_score_returns_weighted_average():
    result = calculate_score(grades=[90, 80, 70], weights=[0.5, 0.3, 0.2])
    assert result == 83.0
```

### 2. RUN — Verify It Fails

Run the test and confirm it fails for the RIGHT reason:

```bash
npm test -- --grep "returns items filtered"
# or
pytest tests/test_scoring.py::test_calculate_score -v
```

Expected: FAIL with a clear error (function not found, endpoint 404, assertion error, etc.)

If it passes without implementation — your test is wrong. Fix the test.

### 3. GREEN — Write Minimal Code

Write the MINIMUM code to make the test pass. No extra features, no "while I'm here" additions.

### 4. RUN — Verify It Passes

Run the same test again. Expected: PASS

### 5. REFACTOR — Clean Up (If Needed)

Only if the code is messy. Don't refactor for the sake of it.

### 6. COMMIT

```bash
git add -A
git commit -m "feat: [what the test proves works]"
```

## Anti-Patterns

- **"Too simple to test"** — Simple code breaks too. Write the test.
- **"I'll write tests after"** — You won't. And if you do, they'll test implementation, not behavior.
- **"Tests slow me down"** — Tests prevent 3-hour debugging sessions. They speed you up.
- **"I'll just manually test it"** — Manual tests don't run in CI. Write automated tests.
- **"Mocking everything"** — Only mock external services. Integration tests use real connections.

## What Makes a Good Test

- **Tests behavior, not implementation** — "returns filtered results" not "calls findMany with where clause"
- **One assertion per concept** — Each test proves one thing
- **Clear name** — `it('returns 401 when no auth token')` not `it('works')`
- **No test-only code in production** — Never add methods just for testing
