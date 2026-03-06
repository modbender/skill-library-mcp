# Gate: Test Quality

**Question:** Are the tests actually testing anything?

## Checks (NOT just line coverage)

- **Assertion density per test** — tests with zero or one assertion are suspect
- **Branch coverage** — did both sides of every if/else execute?
- **Edge case presence** — tests for: empty input, null, boundary values, error paths?
- **Independence** — does each test fail independently or share mutable state?
- **Naming** — do test names describe behavior or just method names?

## Scripts

Run `scripts/coverage-stats.sh` for raw coverage numbers, then AI-analyze the test files.

## Pass/Fail

- **Pass:** Every public function has ≥1 test with ≥2 meaningful assertions. Edge cases covered for critical paths.
- **Fail:** Any public function with zero tests. Any test that's just `expect(true).toBe(true)`.
