# Troubleshooting - Apple Maps (MacOS)

## Maps Opens in Browser Instead of Maps.app

Symptoms:
- URL opens in browser tab instead of Apple Maps app.

Actions:
1. Use `open -a Maps "https://maps.apple.com/?q=..."`.
2. Retry with a simple query to verify app routing.
3. Keep using explicit `-a Maps` for future operations.

## No Results or Wrong Area Bias

Symptoms:
- Search returns irrelevant places.

Actions:
1. Add explicit `near` context (city or neighborhood).
2. Use a more specific query term.
3. Relaunch with corrected URL and confirm result alignment.

## Route Mode Not Matching Intent

Symptoms:
- Directions open in wrong transport mode.

Actions:
1. Confirm requested mode (driving, walking, transit).
2. Set `dirflg` explicitly in URL.
3. Relaunch and verify visible mode in Maps.

## Shortcuts Path Fails

Symptoms:
- `shortcuts run` fails or shortcut not found.

Actions:
1. Verify shortcut exists with `shortcuts list`.
2. Confirm exact shortcut name or identifier.
3. Fall back to `open -a Maps` URL workflow.

## osascript Fallback Is Unreliable

Symptoms:
- AppleScript command runs but cannot perform deterministic search action.

Actions:
1. Treat `osascript` as UI-assist fallback only.
2. Switch back to URL workflow for deterministic behavior.
3. Document the limitation in local command reliability notes.
