# Safety Checklist

Apply this before any destructive or broad AppleScript action.

## Pre-Execution

- Confirm exact target app and object identity.
- Confirm scope: one item, filtered set, or full set.
- Confirm reversibility and rollback option.
- Confirm user intent in explicit language.

## Confirmation Gate

Use two-step confirmation for destructive actions:
1. Summarize the action and impact in one sentence.
2. Request explicit confirmation before execution.

If user confirmation is ambiguous, do not execute.

## Execution Guardrails

- Run pre-read snapshot when feasible.
- Execute smallest possible scope first.
- Avoid chained destructive commands in one script.

## Post-Execution

- Run read-back verification.
- Report what changed and what did not change.
- Log failure details if expected state was not reached.

## Hard Stops

Stop immediately if any of these apply:
- Target identity is ambiguous.
- Dictionary commands differ from expected shape.
- Script attempts irreversible bulk change without confirmation.
