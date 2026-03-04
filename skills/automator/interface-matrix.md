# Interface Matrix - Automator

Use this order to select the execution interface.

## Preferred Path by Task

| Task | Interface | Why |
|------|-----------|-----|
| Run existing `.workflow` | `automator` CLI | Official runner with stable `-i`, `-D`, and `-v` options |
| Inspect and compose workflow internals | `osascript` + Automator app dictionary | Official scripting terms: `workflow`, `Automator action`, `add`, `execute` |
| Shortcuts-only automation request | `shortcuts run` | Explicit fallback when user asks for Shortcuts |

## Preflight Checks

```bash
command -v automator
command -v osascript
test -d /System/Applications/Automator.app
```

For workflow execution:

```bash
WORKFLOW="/absolute/path/to/flow.workflow"
test -f "$WORKFLOW"
```

## CLI Execution Patterns

Run with verbose output:

```bash
automator -v "/absolute/path/to/flow.workflow"
```

Run with text input:

```bash
printf '%s\n' "line 1" "line 2" | automator -i - "/absolute/path/to/flow.workflow"
```

Run with one workflow variable:

```bash
automator -D TargetFolder="/Users/name/Desktop" "/absolute/path/to/flow.workflow"
```

## Interface Selection Rules

1. If a valid `.workflow` already exists, run via `automator` first.
2. If the user asks to edit actions, switch to AppleScript composition flow.
3. If task scope is unclear, ask for expected side effects before selecting interface.
