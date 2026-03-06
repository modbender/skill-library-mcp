# Code Review: openclaw-monitor

## Summary
3 issues found (0 critical, 1 high, 2 medium, 0 low)

## Strengths
- All database interactions use prepared statements, preventing SQL injection vulnerabilities.
- Idempotent inserts with `INSERT OR IGNORE` and unique `event_id` ensure data integrity and prevent duplicates.
- WAL mode enabled for better concurrency and crash recovery.
- Migrations are versioned, checksummed, and run transactionally.
- Comprehensive test suite covering ingestion, reporting, aggregation, interchange generation, and backup/restore.
- Clear separation of concerns: collector for ingestion, reports for queries, aggregator for summaries.
- Interchange files distinguish between ops (no sensitive data) and state (detailed metrics), enhancing security.
- Edge cases like zero events are handled gracefully with `COALESCE`.
- Good use of indexes in schema for performance.

## Issues

### 1. [HIGH] Missing Error Handling in CLI Actions
**File:** `src/cli.js` lines 15-200 (all command actions)
**Problem:** CLI commands open a database connection but do not wrap operations in try-catch blocks. If a database error occurs (e.g., corruption, permission issues), the process will crash without graceful error reporting, and the DB might not be closed properly (though process exit mitigates this). No user-friendly error messages for common failures like invalid options or DB access issues.
**Fix:** Wrap each action in try { ... } catch (err) { console.error(`Error: ${err.message}`); closeDb(); process.exit(1); }. Use commander's built-in error handling where possible, and validate options early.

### 2. [MEDIUM] Lack of Input Validation in Event Ingestion
**File:** `src/collector.js` lines 20-50 (addTokenEvent, addTaskEvent, addCronRun)
**Problem:** Functions accept inputs without validation, allowing invalid data like negative tokens, invalid statuses (e.g., 'invalid' for tasks), or non-numeric durations. While schema CHECK constraints exist for statuses, numeric fields could be corrupted. CLI options parse to numbers but don't check ranges.
**Fix:** Add validation before insertion: e.g., if (event.tokens_in < 0 || event.tokens_out < 0) throw new Error('Tokens must be non-negative'); For statuses, use a Set of allowed values. Consider adding CHECK constraints to schema for tokens >=0 and duration_ms >0.

### 3. [MEDIUM] Recent Errors in Status Not Time-Bounded
**File:** `src/reports.js` line 45 (getStatus)
**Problem:** `recent_errors` query fetches the last 5 failures all-time, not limited to recent periods (e.g., last 7 days). This could show outdated errors in daily status reports, reducing relevance.
**Fix:** Add a time filter to the query, e.g., WHERE timestamp > datetime('now', '-7 days') ORDER BY timestamp DESC LIMIT 5. Make the window configurable if needed.
