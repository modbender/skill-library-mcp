# Performance Traps

## Event Loop Blocking
- `fs.readFileSync` blocks entire server — use `fs.promises.readFile`
- CPU-intensive code blocks — no I/O processed, use worker_threads
- Large `JSON.parse` blocks — consider streaming parser for big files
- RegEx catastrophic backtracking — `/(a+)+$/` hangs on "aaaaaaaaaaaaaaX"

## Memory Leaks
- Event listeners accumulate — `removeListener` or use `once()`
- `setInterval` without `clearInterval` — keeps running forever
- Closures hold references — large objects stay in memory
- Global caches grow unbounded — use LRU with max size

## Worker Threads
- Thread creation has overhead — don't spawn per-request, use pool
- `postMessage` copies data — use SharedArrayBuffer for large data
