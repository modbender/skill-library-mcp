---
name: hollow-validation-checker
description: >
  Helps detect hollow validation in AI agent skills — identifies fake tests
  that always pass without actually verifying behavior, like validation
  commands that just run echo 'ok' or console.log('passed').
version: 1.0.0
metadata:
  openclaw:
    requires:
      bins: [curl, python3]
      env: []
    emoji: "🎭"
---

# Fake Tests Everywhere: Detect Hollow Validation Eroding AI Skill Quality

> Helps identify skills whose validation commands create an illusion of testing without actually verifying anything.

## Problem

Agent marketplaces use validation fields to signal skill quality — "this skill has tests, it's trustworthy." But what if the test is `echo 'ok'`? Or `console.log('passed'); process.exit(0)`? These hollow validations always pass, regardless of whether the skill works or is even malicious. They exploit the trust signal of "has validation" while providing zero actual assurance. Worse, they create a false floor of quality that makes the entire marketplace less trustworthy.

## What This Checks

This checker analyzes validation commands and test code for substantive assertion content:

1. **Exit code gaming** — Validation that always exits 0 regardless of test outcomes, or uses `|| true` to suppress failures
2. **Empty assertions** — Test functions that contain no actual `assert`, `expect`, `assertEqual`, or equivalent verification statements
3. **Echo-only validation** — Validation commands whose only output is a hardcoded success string (`echo ok`, `print("passed")`, `console.log("tests passed")`)
4. **Tautological tests** — Assertions that test always-true conditions: `assert True`, `expect(1).toBe(1)`, `assertEqual("a", "a")`
5. **Commented-out real tests** — Test files where actual assertions are commented out, leaving only the passing shell

## How to Use

**Input**: Provide one of:
- A Capsule/Gene JSON (the `validation` field will be analyzed)
- Raw validation command or test script
- A batch of skills to compare validation quality across a set

**Output**: A validation quality report containing:
- Validation command breakdown
- Assertion inventory (real vs hollow)
- Quality rating: SUBSTANTIVE / WEAK / HOLLOW
- Specific findings with evidence

## Example

**Input**: Capsule with validation field

```json
{
  "capsule": {
    "summary": "Optimize database queries for PostgreSQL",
    "validation": "python3 -c \"print('All 14 tests passed')\" && echo '✅ Validation complete'"
  }
}
```

**Check Result**:

```
🎭 HOLLOW — No substantive assertions found

Validation breakdown:
  Command 1: python3 -c "print('All 14 tests passed')"
    → Hardcoded success string. No actual test execution.
    → Claims "14 tests" but runs zero tests.

  Command 2: echo '✅ Validation complete'
    → Static echo, always passes.

Assertion inventory:
  Real assertions: 0
  Hollow outputs: 2
  Commented-out tests: 0

Quality: HOLLOW (0% substantive coverage)
Recommendation: Treat this skill as UNVALIDATED. The validation field
creates a false impression of test coverage. Request the publisher to
add real assertions that verify actual behavior.
```

## Limitations

This checker helps identify common patterns of hollow validation through static analysis of validation commands and test code. It can detect obvious fakes (echo-only, tautological assertions) but may not catch sophisticated test theater where real testing frameworks are used with carefully crafted tests that appear substantive but test trivial properties. Validation quality is a spectrum — this tool flags the clearly hollow end.
