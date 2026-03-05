# Gate: Property-Based & Fuzz Testing

**Question:** Do the invariants hold across thousands of random inputs?

Unit tests check a few known cases. Property-based testing checks your invariants
across hundreds or thousands of randomly generated cases — finding edge cases nobody
thought to test.

Run `scripts/property-test.sh [path]` first.

---

## What Are Properties

Properties are statements that must ALWAYS be true, regardless of input:

```python
# Sort: output is always ordered
assert all(result[i] <= result[i+1] for i in range(len(result)-1))

# Filter: output is always a subset
assert all(item in original for item in filtered)

# Encode/decode roundtrip
assert decode(encode(x)) == x

# Length invariant
assert len(compress(x)) <= len(x)  # compression never expands

# Idempotency
assert f(f(x)) == f(x)  # running twice = running once
```

---

## Tools by Language

| Language | Tool | Install | Run |
|----------|------|---------|-----|
| Python | hypothesis | `pip install hypothesis` | `pytest` (auto-discovers `@given`) |
| JavaScript/TypeScript | fast-check | `npm install fast-check` | `npx fast-check` or via jest/vitest |
| Rust | proptest / quickcheck | `cargo add proptest` | `cargo test` |
| Go | go-fuzz / gopter | `go get gopter` | `go test -fuzz=.` |
| Java | jqwik | Add to pom.xml | `mvn test` |
| Ruby | rantly | `gem install rantly` | `rspec` |

---

## Step-by-Step Process

### 1. Check for Existing Property Tests

Look for:
- Python: files with `@given`, `@settings`, `from hypothesis import`
- JS/TS: `import { fc } from 'fast-check'`, `fc.property`
- Rust: `#[proptest]`, `proptest!` macro, `#[quickcheck]`
- Go: `func Fuzz` functions (Go 1.18+ native fuzzing)

If found: run them. Any failure = bug.

### 2. If No Property Tests Exist — Generate Stubs

For each public function, identify testable invariants:
- Return type constraints (always returns an array, never null)
- Length constraints (output <= input length)
- Ordering constraints (sorted output)
- Roundtrip properties (parse/serialize, encode/decode)
- Idempotency (calling twice = calling once)
- Commutativity/associativity (where applicable)

Write minimal property test stubs to a `.wreckit/property-stubs/` directory.
These are starting points — they should be moved into the actual test suite.

### 3. Run the Fuzzer

Configure for at least:
- **100 examples** minimum (hypothesis default: 100, fast-check default: 100)
- **Shrinking enabled** — when a failure is found, shrink to minimal case
- **Deadline disabled** for slow functions

### 4. Crash Corpus Management

If any input crashes the function:
1. Save the crashing input to `.wreckit/crash-corpus/`
2. Add it as a regression test immediately
3. Fix the bug, re-run to confirm crash is gone
4. Keep the crashing input forever as a regression seed

---

## Pass/Fail Criteria

| Result | Verdict |
|--------|---------|
| Existing property tests found AND all pass | Pass ✅ |
| No property tests found, but stubs generated | Caution ⚠️ (note: add to test suite) |
| Property test framework installed, zero properties written | Caution ⚠️ |
| Any property test fails | Fail 🚫 |
| Any crash/exception on random input that's not handled | Fail 🚫 |
| Framework not installed and language doesn't support native fuzzing | Warn ⚠️ |

---

## Script Output

`scripts/property-test.sh [path]` outputs:
```json
{
  "framework_detected": "hypothesis|fast-check|proptest|go-fuzz|none",
  "property_tests_found": 5,
  "property_tests_run": 5,
  "failures": [],
  "crash_inputs": [],
  "stubs_generated": "path/to/.wreckit/property-stubs/",
  "verdict": "PASS|FAIL|WARN"
}
```
