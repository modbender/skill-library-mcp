# Queue Traps

- Model property serializes as ID — re-fetched on process, may be deleted
- Closure can't serialize — use invocable job class, not anonymous function
- `$tries` exceeded — job goes to `failed_jobs` table silently
- `$timeout` kills process — no exception, no retry, job lost without `$tries`
- `release()` without delay — infinite retry loop, CPU spike
- `dispatchAfterResponse()` — runs in same process, blocks shutdown
- Job constructor runs at dispatch — not at process time, stale data
- Database queue + transactions — job may process before commit
