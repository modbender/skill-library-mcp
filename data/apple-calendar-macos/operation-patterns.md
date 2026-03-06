# Operation Patterns - Apple Calendar

Use these patterns to keep behavior deterministic and auditable.

## Lookup Pattern

1. Normalize time range (timezone plus explicit start and end).
2. Query only the target window.
3. If duplicates exist, disambiguate before any write.

## Create Pattern

1. Validate required fields: title, start, end (or all-day flag), calendar.
2. Run a pre-read in the same window.
3. Execute create using active command path.
4. Run read-back and return concise confirmation.

## Update Pattern

1. Resolve a unique target event first.
2. Confirm changed fields only.
3. Execute update with explicit before/after summary.
4. Verify with read-back and report final state.

## Delete Pattern

1. Resolve a unique event and show snapshot.
2. Require explicit confirmation.
3. Execute delete.
4. Verify absence in the same window and report outcome.

## Multi-Calendar Pattern

1. Confirm which Calendar.app account owns the target event.
2. If moving events across calendars, show source and destination before execution.
3. Re-read both calendars in the target window after write.

## Failure Pattern

- On permission or command errors, keep context and switch to next valid path.
- If no safe fallback exists, stop and provide exact blocker with one actionable fix.
