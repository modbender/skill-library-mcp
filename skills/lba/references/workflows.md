# Linear Browser Workflows

## Create issue workflow

1. In `profile="openclaw"`, check existing tabs and reuse an already-open Linear tab if available.
2. If no Linear tab exists, navigate to `https://linear.app/`.
3. Snapshot and detect whether user is authenticated.
4. If unauthenticated/public landing:
   - navigate to `https://linear.app/login`
   - show browser alert: "Please log in to Linear so I can continue this task."
   - wait until dashboard/workspace UI appears
5. Ensure required chat inputs exist (team/project context, title).
6. If required fields missing in chat, prompt for missing inputs.
7. Fill issue form fields.
8. Present final summary in chat.
9. Ask: `Proceed? (yes/no)`.
10. If yes, submit issue.
11. Snapshot and verify success (identifier/link/banner).

## Bulk triage workflow

1. Apply filters (team/state/assignee/label).
2. Snapshot and verify list matches requested scope.
3. Announce planned bulk action and ask for confirmation.
4. Execute updates in small batches.
5. Re-snapshot and report changed items.

## Comment workflow

1. Open target issue.
2. Snapshot and locate comment input.
3. Fill comment text.
4. Optional confirmation for sensitive content.
5. Submit and verify comment appears in timeline.
