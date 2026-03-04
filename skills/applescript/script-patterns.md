# Script Patterns

Reference patterns for robust AppleScript execution.

## Quoting User Text Safely

- Escape embedded quotes before interpolation.
- Prefer passing controlled values rather than raw command fragments.
- Reject unsafe input if command boundaries are unclear.

## Read-Only Probe Pattern

```applescript
tell application "System Events"
  return name of every process
end tell
```

Use this first to verify permissions and baseline execution.

## Read-Before-Write Pattern

```applescript
-- 1) Read target state
-- 2) Apply change
-- 3) Read back final state
```

Never skip step 1 or step 3 for write operations.

## Timeout and Wait Strategy

- Add bounded retries for app launch readiness.
- Use short waits with explicit max attempts.
- Stop with diagnostics when retries are exhausted.

## Output Normalization

- Return concise, parse-friendly text.
- Prefer one record per line for lists.
- Include key identifiers that allow verification.
