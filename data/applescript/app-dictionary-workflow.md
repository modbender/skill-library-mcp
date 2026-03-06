# App Dictionary Workflow

Use this process before writing app-specific AppleScript commands.

## 1. Confirm Target App and Intent

- Confirm exact app name and requested action.
- Classify action as read-only, write, or destructive.

## 2. Inspect the App Dictionary

- Open Script Editor dictionary viewer when available.
- Identify real classes, properties, and commands for the target app.
- Record exact casing and object hierarchy.

## 3. Build a Minimal Probe Script

Start with a small read-only probe that confirms dictionary understanding:

```applescript
tell application "TargetApp"
  -- read one known property
end tell
```

## 4. Expand in Small Steps

- Add one operation at a time.
- Validate output after each change.
- Keep each step reversible where possible.

## 5. Persist Reusable Notes

Store successful object names and command patterns in local memory.
Document failed patterns and why they failed.

## Red Flags

- Unknown class or property names guessed from memory.
- Multiple app versions with different dictionaries.
- UI-only actions attempted as direct dictionary commands.
