# Test-Driven Development Reference

Source: obra/superpowers test-driven-development skill

## The Iron Law

```
NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST
```

Wrote code before the test? Delete it. Start over. No exceptions.
- Don't keep it as "reference"
- Don't "adapt" it while writing tests
- Delete means delete

## Red-Green-Refactor

### RED — Write Failing Test

Write one minimal test showing what should happen.

**Good:**
```python
def test_retries_failed_operations_three_times():
    attempts = 0
    def operation():
        nonlocal attempts
        attempts += 1
        if attempts < 3:
            raise Exception("fail")
        return "success"
    result = retry(operation)
    assert result == "success"
    assert attempts == 3
```

**Bad:** vague name, tests mocks not real code, multiple behaviours in one test.

Requirements:
- One behaviour per test
- Clear descriptive name
- Real code (no mocks unless unavoidable)

### Verify RED — Watch It Fail

**MANDATORY. Never skip.**

Run the test. Confirm:
- Test fails (not errors)
- Failure is expected ("function not defined", assertion error)
- Fails because feature is missing, not because of typos

If test passes immediately → you're testing existing behaviour, fix the test.

### GREEN — Minimal Code

Write the simplest code to make the test pass. No more. No extras.

Don't:
- Add options not tested
- Refactor other code
- "Improve" beyond what the test requires

### Verify GREEN — Watch It Pass

**MANDATORY.**

Run full test suite. Confirm:
- Target test passes
- All other tests still pass
- No new warnings or errors

If tests fail → fix code, not the test.

### REFACTOR — Clean Up

After green only:
- Remove duplication
- Improve names
- Extract helpers

Keep tests green throughout. Never add behaviour here.

## Good Test Qualities

| Quality | Good | Bad |
|---------|------|-----|
| Minimal | One thing | "and" in name? Split it |
| Clear | Describes behaviour | `test1`, `test_works` |
| Shows intent | Demonstrates desired API | Hides what code should do |

## Why TDD Order Matters

Tests written after code pass immediately — this proves nothing:
- Might test wrong thing
- Might test implementation, not behaviour
- You never saw it catch the bug

Test-first forces you to see the test fail, proving it actually tests something.

## Exceptions (ask Rich first)

- Throwaway prototypes
- Generated/boilerplate code
- Configuration files

Thinking "skip TDD just this once"? That's rationalisation. Don't.
