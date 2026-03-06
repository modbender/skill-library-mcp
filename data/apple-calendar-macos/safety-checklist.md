# Safety Checklist - Apple Calendar

Apply this checklist before any create, update, or delete operation.

## Pre-Write Checks

1. Confirm target calendar name exactly.
2. Confirm event identity using at least two fields (title plus start time, or ID).
3. Confirm timezone interpretation and all-day behavior.
4. For recurrence, confirm rule and effective date range.
5. For cross-calendar move, confirm source and destination calendar names.
6. For destructive actions, collect explicit user confirmation in clear text.

## Post-Write Checks

1. Re-read the exact target window.
2. Verify title, start/end, calendar, and recurrence fields.
3. Report success only after read-back matches requested change.
4. If mismatch occurs, stop and present rollback options.

## Bulk Operation Guardrails

- Show count of impacted events before execution.
- Require a second explicit confirmation for edits affecting more than one event.
- Keep a minimal snapshot of impacted events for rollback discussion.
