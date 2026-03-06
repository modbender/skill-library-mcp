# Command Paths - Apple Maps (MacOS)

Use this order for deterministic command selection.

## Priority Order

1. `open` with Apple Maps URLs (primary and preferred)
2. `shortcuts run` for user-owned shortcut automations
3. `osascript` as last-mile fallback (activate app and assist UI workflows)

## Probe Pattern

Run lightweight checks before first operation:

```bash
command -v open
command -v shortcuts
command -v osascript
```

## URL Launch Pattern

Use `open -a Maps` with explicit URLs:

```bash
open -a Maps "https://maps.apple.com/?q=coffee+near+me"
open -a Maps "https://maps.apple.com/?q=restaurants&near=Madrid"
open -a Maps "https://maps.apple.com/?saddr=Cupertino&daddr=San+Francisco&dirflg=d"
```

## URL Parameter Rules

- `q` for search terms or place names.
- `near` to bias search near a specific area.
- `saddr` and `daddr` for routing origin and destination.
- `dirflg` for route mode (`d` driving, `w` walking, `r` transit).
- `ll` and `z` for map center and zoom when explicit map framing is needed.

## Selection Rules

- Use the first available path in priority order.
- If `open` is available, prefer URL workflows over UI scripting.
- If using `shortcuts run`, require an existing shortcut name and confirm expected output.
- If only `osascript` is usable, clearly state reduced reliability and request confirmation before proceeding.

## Notes on Scriptability

- Apple Maps has limited direct AppleScript command coverage for deterministic search actions.
- Use URL-based invocation as the stable default and keep UI scripting as a fallback only.
