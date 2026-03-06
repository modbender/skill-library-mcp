# Troubleshooting - Automator

Use this matrix when a workflow run fails.

## Failure Matrix

| Symptom | Likely Cause | Next Action |
|---------|--------------|-------------|
| `No se ha podido abrir` / file not found | Relative or wrong workflow path | Resolve absolute path and re-run preflight checks |
| `command not found: automator` | PATH or environment mismatch | Use `/usr/bin/automator` directly and re-check shell context |
| AppleScript `Can't get Automator action` | Action name mismatch | Enumerate actions first, then retry with exact name |
| Permission dialogs block execution | macOS automation/privacy permissions missing | Ask user to grant permission, then run a small read-only probe |
| Workflow runs but output is empty | Input mismatch or wrong variable binding | Validate `-i` input format and verify each `-D` variable name |

## Fast Triage Sequence

```bash
command -v automator
command -v osascript
test -f "/absolute/path/to/flow.workflow"
automator -v "/absolute/path/to/flow.workflow"
```

If the failure persists, capture:
- Exact command used.
- Full stderr output.
- Whether a permission prompt appeared.

## Recovery Rules

1. Never retry destructive workflows without re-confirmation.
2. Reduce to a minimal reproducible run.
3. Reintroduce inputs and variables one by one.
4. Persist only fixes that worked at least twice.
