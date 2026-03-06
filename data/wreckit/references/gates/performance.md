# Gate: Performance Benchmarks

**Question:** Is the code fast enough, and did it get slower?

AI code often works on toy inputs but tanks at scale. This gate catches:
- O(n²) algorithms hiding in "working" code
- Functions that take 10ms at 100 items but 60 seconds at 10,000
- Memory blowups that look fine until production load hits
- Regressions: code that worked fast last week is now 3x slower

Run `scripts/perf-benchmark.sh [path]` first.

---

## Step-by-Step Process

### 1. Find or Create Benchmarks

Look for:
- **Vitest bench** — `bench()` calls in test files
- **pytest-benchmark** — `benchmark.pedantic()` or `benchmark()` in pytest
- **cargo bench** — `#[bench]` functions
- **go test -bench** — `func BenchmarkX(b *testing.B)` functions
- **k6** — `k6.js` or `script.js` load test files

If none exist: write benchmarks for the 3 most critical/expensive functions.

### 2. Run Benchmarks

Run benchmarks with enough iterations to be statistically meaningful:
- Vitest bench: `vitest bench`
- pytest-benchmark: `pytest --benchmark-only`
- cargo bench: `cargo bench`
- go bench: `go test -bench=. -benchmem -count=3`
- k6: `k6 run script.js`

### 3. Compare vs Baseline

If `.wreckit/perf-baseline.json` exists from a previous run:
- Compare each benchmark's mean time to baseline
- Flag regressions > 20% slower
- Flag improvements > 20% faster (document, may want to update baseline)

If no baseline exists: write current results as the new baseline.

### 4. Complexity Analysis

For core algorithmic functions, estimate time complexity:
- Run at N=10, 100, 1000, 10000 inputs
- Calculate growth ratio: T(10N)/T(N)
  - ~1.0x → O(1) or O(log n) — excellent
  - ~2-3x → O(n) — expected
  - ~10x → O(n log n) — acceptable for sort operations
  - ~100x → O(n²) — likely too slow for production at scale
  - ~1000x → O(n³) or worse — almost certainly broken

### 5. Memory Scaling

Run at increasing input sizes and track peak memory:
- Watch for linear memory growth (normal)
- Flag superlinear memory growth (possible bug)

---

## Pass/Fail Criteria

| Condition | Verdict |
|-----------|---------|
| All benchmarks within 20% of baseline | Pass ✅ |
| No baseline — first run | Pass ✅ (baseline created) |
| Any benchmark >20% slower than baseline | Caution ⚠️ |
| Any benchmark >50% slower than baseline | Blocked 🚫 |
| O(n²) or worse detected for N>1000 operation | Blocked 🚫 |
| Memory grows superlinearly | Caution ⚠️ |
| No benchmarks and no benchmark framework | Warn ⚠️ |

---

## Script Output

`scripts/perf-benchmark.sh [path]` outputs:
```json
{
  "framework": "vitest-bench|pytest-benchmark|cargo-bench|go-bench|none",
  "benchmarks": [
    {
      "name": "sort 1000 items",
      "mean_ms": 1.2,
      "baseline_ms": 1.0,
      "delta_pct": 20.0,
      "regression": false
    }
  ],
  "regressions": [],
  "baseline_created": true,
  "baseline_path": ".wreckit/perf-baseline.json",
  "verdict": "PASS|WARN|FAIL"
}
```
