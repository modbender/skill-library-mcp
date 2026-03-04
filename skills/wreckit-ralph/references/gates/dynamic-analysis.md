# Gate: Dynamic Analysis

**Question:** Does the code misbehave at runtime — leaks memory, races on shared state, hits undefined behavior?

Static analysis finds what code LOOKS like. Dynamic analysis finds what it DOES — at runtime,
under real execution. These are entirely different failure classes.

Run `scripts/dynamic-analysis.sh [path]` first.

---

## What Dynamic Analysis Catches

Things NO amount of reading the code or running tests will catch:

- **Memory leaks** — objects created, never garbage collected
- **Race conditions** — concurrent writes to shared state producing corrupt results
- **Use-after-free** — accessing memory after it's been freed (C/C++)
- **Undefined behavior** — signed overflow, null dereference, invalid casts
- **Async leaks** — event listeners added, never removed; timers that don't clear
- **File descriptor leaks** — files opened in error paths without being closed
- **Handle leaks** — database connections, network sockets not returned to pool

---

## Tools by Language

### C / C++
- **Valgrind** — memory errors, leaks, undefined behavior: `valgrind --leak-check=full ./binary`
- **AddressSanitizer (ASAN)** — compile with `-fsanitize=address`
- **UndefinedBehaviorSanitizer (UBSan)** — compile with `-fsanitize=undefined`
- **ThreadSanitizer (TSan)** — compile with `-fsanitize=thread`

### Python
- **tracemalloc** — built-in memory tracing
- **memory_profiler** — `pip install memory_profiler`, run `@profile` decorator
- **objgraph** — `pip install objgraph`, finds reference cycles
- **pytest-memray** — memory profiling in tests

### JavaScript / TypeScript (Node.js)
- **--expose-gc + heapUsed** — track V8 heap growth
- **clinic.js** — `npx clinic doctor -- node app.js`
- **node --inspect** — Chrome DevTools memory profiling
- **leakage** — `npm install leakage`, automatic leak detection in tests

### Go
- **go test -race** — built-in race detector (always use this)
- **pprof** — built-in profiling: `go test -memprofile=mem.out`
- **go test -count=N** — run tests multiple times to expose flakiness

### Rust
- **Miri** — interpreter that detects undefined behavior: `cargo miri test`
- **cargo test -- --nocapture** — run tests with full output
- Memory safety is largely guaranteed by the borrow checker (less concern here)

---

## Step-by-Step Process

### 1. Run Language-Appropriate Sanitizers

Run the test suite with sanitizers enabled. ANY sanitizer finding = Blocked.

### 2. Memory Leak Check

Run tests, then check for heap growth:
- Before test: record heap size
- Run tests
- After test: record heap size
- Growth > 10MB unexplained = warning

### 3. Race Condition Check

For concurrent code:
- Go: always `go test -race`
- Python async: run with `asyncio.set_debug(True)` and check for warnings
- JS async: look for unhandled promise rejections, unhandled event emitter errors

### 4. File/Handle Leak Check

After running tests, check:
- Open file descriptors (compare before/after)
- Open database connections
- Active event listeners (Node.js: `process.listenerCount('exit')`)

---

## Pass/Fail Criteria

| Finding | Severity | Verdict |
|---------|----------|---------|
| Memory leak > 1MB sustained | BLOCKER | Blocked 🚫 |
| Race condition detected | BLOCKER | Blocked 🚫 |
| Use-after-free / ASAN finding | BLOCKER | Blocked 🚫 |
| Undefined behavior (UBSan) | BLOCKER | Blocked 🚫 |
| Memory growth < 10MB (tolerable) | INFO | Pass ✅ |
| Async resource leak | WARNING | Caution ⚠️ |
| FD leak detected | WARNING | Caution ⚠️ |
| No dynamic analysis tooling available | INFO | Warn ⚠️ (note only) |
