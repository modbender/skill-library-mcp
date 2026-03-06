# Troubleshooting - Apple Calendar

## Terminal Cannot Access Calendar

Symptoms:
- Command fails with permission errors.

Actions:
1. Ask user to grant Calendar permission to terminal app in macOS Privacy settings.
2. Re-run a read-only command first.
3. Retry write only after read succeeds.

## Calendar Not Visible in CLI Results

Symptoms:
- User sees a calendar in Calendar.app, but command output omits it.

Actions:
1. Confirm the calendar account is enabled for Calendar sync in macOS settings.
2. Run a broad read on a short date window to force index refresh.
3. Switch command path and compare output.

## Duplicate Event Matches

Symptoms:
- Multiple events share the same title.

Actions:
1. Narrow search window.
2. Match with additional fields (start time, calendar, notes snippet).
3. Ask a short disambiguation question before write.

## Timezone Drift on Recurrence

Symptoms:
- Recurring meetings shift after DST transitions.

Actions:
1. Confirm timezone explicitly.
2. Verify recurrence rule and first occurrence.
3. Re-read events around transition dates.

## Path-Specific Failures

Symptoms:
- Primary command path breaks after OS update.

Actions:
1. Probe all paths in priority order.
2. Switch to a confirmed fallback path.
3. Log the failure and communicate new active path.
