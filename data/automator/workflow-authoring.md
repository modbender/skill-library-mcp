# Workflow Authoring With AppleScript

Use this file when the task is to inspect, compose, or mutate Automator workflows.

## 1. Verify Automator Dictionary Access

```bash
sdef /System/Applications/Automator.app | rg "Automator Suite|command name=\"add\"|command name=\"execute\""
```

This confirms expected scripting terms are available.

## 2. Enumerate Installed Automator Actions

```bash
osascript <<'APPLESCRIPT'
tell application "Automator"
  return name of every Automator action
end tell
APPLESCRIPT
```

Use this before selecting action names for composition.

## 3. Build a Minimal Workflow Programmatically

```bash
osascript <<'APPLESCRIPT'
tell application "Automator"
  set wf to make new workflow
  set candidate to first Automator action whose name is "Get Selected Finder Items"
  add candidate to wf
  execute wf
  return execution result of wf
end tell
APPLESCRIPT
```

Notes:
- Add one action at a time.
- Verify each action exists before adding.
- Read `execution error message` if `execute` fails.

## 4. Edit Existing Workflow Safely

```bash
osascript <<'APPLESCRIPT'
tell application "Automator"
  open POSIX file "/absolute/path/to/flow.workflow"
  set wf to first workflow
  set actionNames to name of every Automator action of wf
  return actionNames
end tell
APPLESCRIPT
```

After each mutation, re-read action names or settings to confirm state.

## 5. Capture Deterministic Run Records

Record after every meaningful run:
- Interface used (`automator` or `osascript`).
- Input source (`-i`, `-D`, or none).
- Workflow path and result summary.
- Any permission prompt or runtime error text.
