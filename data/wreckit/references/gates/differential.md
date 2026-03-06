# Gate: Differential Testing

**Question:** Does this implementation agree with an independent oracle on the same inputs?

The most powerful bug-catcher available. Catches "plausible but wrong" logic that no amount of
unit tests will find — because the tests and the code were written by the same AI with the same
misunderstanding.

Run `scripts/differential-test.sh [path]` first.

---

## What Is Differential Testing

You run TWO implementations on the SAME inputs and compare outputs. If they disagree,
one of them is wrong. The "oracle" can be:

1. **A reference implementation** — a trusted library doing the same thing
2. **A brute-force "obviously correct" version** — slow but simple
3. **A previous known-good version** of the code
4. **A different language's implementation** — Python vs Go, etc.
5. **Golden test outputs** — hand-verified expected outputs stored in a file

---

## Step-by-Step Process

### 1. Find or Create the Oracle

Look for:
- Existing tests with hardcoded expected values → these ARE golden tests
- A `reference/` or `oracle/` directory in the project
- A simpler brute-force implementation in comments or docs
- The same function implemented in a different file/module

If none exists, create a brute-force oracle for the core logic. Example:
- Real: optimized binary search
- Oracle: linear scan (same answer, obviously correct)

Document what oracle was used in the gate result.

### 2. Identify Test Cases

Use a mix of:
- **Boundary inputs:** empty, null, min value, max value, single element
- **Typical inputs:** representative real-world cases (3-5)
- **Adversarial inputs:** duplicates, sorted, reverse-sorted, all-same values
- **Random inputs:** at least 20 randomly generated cases

### 3. Run Both Implementations

For each test case:
1. Run the real implementation → capture output
2. Run the oracle → capture output
3. Compare outputs (exact match, or use tolerance for floats)
4. Record: input, expected (oracle), actual (real), match/mismatch

### 4. Metamorphic Testing (No Oracle Needed)

If you have no oracle, use metamorphic properties — relationships that MUST hold:

Examples:
- `sort(reverse(X)) == reverse(sort(X))`
- `len(filter(X)) <= len(X)`
- `sum(split(X)) == sum(X)` (for partitioning functions)
- `encode(decode(X)) == X` (for codecs)
- `f(f(X)) == f(X)` (for idempotent functions)

Run these properties on 50+ random inputs. Any violation is a bug.

### 5. Golden Test Verification

Check existing test files for:
- Hardcoded expected values
- Snapshot tests
- Fixture files with expected outputs

Run all of them. If any fail, it's a regression.

---

## Pass/Fail Criteria

| Result | Verdict |
|--------|---------|
| Implementation matches oracle on all inputs | Pass ✅ |
| Implementation matches oracle on all but ≤2% of random cases (float precision) | Caution ⚠️ |
| Implementation disagrees with oracle on any deterministic input | Fail 🚫 |
| No oracle found AND no metamorphic properties testable | Caution ⚠️ (note as incomplete) |
| Metamorphic property violated on any input | Fail 🚫 |
| Golden tests fail | Fail 🚫 |

---

## Script Output

`scripts/differential-test.sh [path]` outputs:
```json
{
  "oracle_type": "brute_force|golden|reference|metamorphic|none",
  "oracle_description": "What oracle was used",
  "test_cases_run": 50,
  "mismatches": [
    {
      "input": "...",
      "expected": "...",
      "actual": "...",
      "case_type": "boundary|random|adversarial"
    }
  ],
  "mismatch_rate": 0.02,
  "metamorphic_violations": [],
  "golden_test_failures": [],
  "verdict": "PASS|FAIL|WARN"
}
```
