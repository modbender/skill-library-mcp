# TDD Patterns Reference

## RED → GREEN → REFACTOR Cycle

### RED Phase Rules
1. Write ONE test at a time — never batch
2. Test must describe BEHAVIOR, not implementation
3. Test name format: `should {expected behavior} when {condition}`
4. Run test and verify it FAILS for the RIGHT reason
5. If test passes immediately — the test is wrong or feature exists

### GREEN Phase Rules
1. Write the SIMPLEST code that makes the test pass
2. Hardcoding is acceptable to pass a single test
3. Do NOT add logic for future tests
4. Do NOT refactor during GREEN
5. Run ONLY the new test first, then full suite

### REFACTOR Phase Rules
1. No new functionality during refactor
2. All tests must stay green after every change
3. Extract duplicated code
4. Improve naming and readability
5. Simplify complex conditionals

## Test Structure: Arrange-Act-Assert

```
test('should return total with tax applied', () => {
  // Arrange — Set up test data
  const cart = new Cart([{ price: 100, qty: 2 }]);

  // Act — Execute the behavior
  const total = cart.totalWithTax(0.1);

  // Assert — Verify the outcome
  expect(total).toBe(220);
});
```

## What to Test (Priority Order)

1. **Happy path** — Normal expected behavior
2. **Edge cases** — Empty input, null, zero, max values
3. **Error cases** — Invalid input, network failure, timeout
4. **Boundary conditions** — Off-by-one, limits, overflow

## Test Doubles

| Type | Purpose | When |
|------|---------|------|
| **Stub** | Return predetermined data | External API responses |
| **Mock** | Verify interactions | Check if function was called |
| **Fake** | Simplified implementation | In-memory DB instead of real DB |
| **Spy** | Record calls without changing behavior | Logging verification |

## Anti-Patterns to Avoid

- ❌ Testing implementation details (private methods, internal state)
- ❌ Tests that depend on execution order
- ❌ Mocking everything (only mock boundaries)
- ❌ Testing framework behavior
- ❌ Ignoring flaky tests
