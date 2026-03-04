# Jobs Traps

- Pass IDs not objects — ActiveJob serializes, stale data if object changed
- Jobs must be idempotent — retries on failure will re-run entire job
- `perform_later` in transaction — job may execute before commit, see stale DB
- Sidekiq `retry: 0` doesn't disable — use `sidekiq_options retry: false`
- `ActiveJob::DeserializationError` — record deleted between queue and execute
- Long-running job holds Redis connection — Sidekiq starves on connection pool
