# Execution Guardrails

Use this checklist before any run that can modify files, app state, or large batches of items.

## Operation Classes

| Class | Examples | Confirmation Policy |
|-------|----------|---------------------|
| Read-only | List files, inspect metadata, preview app state | No extra confirmation after scope is clear |
| Reversible write | Tagging, moving, or creating items with easy rollback | One explicit confirmation |
| Destructive | Delete, overwrite, reset, bulk edits without easy rollback | Two-step explicit confirmation |

## Pre-Run Checklist

1. Confirm absolute workflow path and intended target.
2. Confirm operation class and expected side effects.
3. Confirm bounded input set (no unbounded stdin).
4. Confirm rollback plan for reversible or destructive runs.
5. Run with verbose output on first execution.

## Two-Step Confirmation Template

Use this wording for destructive runs:

1. "This run will <action> on <target>. Confirm this exact target."
2. "Final check: proceed with destructive execution now?"

Only continue when both confirmations are explicit.

## Post-Run Verification

1. Read back target state after execution.
2. Compare expected vs actual outcome.
3. If mismatch exists, stop and report before retrying.
