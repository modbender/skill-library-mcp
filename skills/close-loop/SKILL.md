---
name: close-loop
description: End-of-session workflow for shipping changes, consolidating memory, applying self-improvements, and preparing publishable outputs with safety gates.
license: MIT
metadata:
  version: 2.1.1
  category: session-memory
---

# Close Loop

Use this skill when the user says "wrap up", "close session", "end session", "close out this task", or invokes `/wrap-up`.

Run four phases in order and return one consolidated inline report.

## Modular structure

This skill is split into components for maintainability:

1. `components/01-design-principles.md`
2. `components/02-phase-1-ship-state.md`
3. `components/03-phase-2-memory.md`
4. `components/04-phase-3-4-and-output.md`

Follow these components in order.

## Quick run order

1. Apply execution policy and action gates (`01-design-principles.md`)
2. Execute Ship State (`02-phase-1-ship-state.md`)
3. Consolidate Memory (`03-phase-2-memory.md`)
4. Run improvements + publish queue + output contract (`04-phase-3-4-and-output.md`)

## Required output

Return:
- Artifact A: human-readable report sections exactly as defined in component 04
- Artifact B: machine-readable JSON block exactly as defined in component 04

## Resources

- `references/memory-frameworks.md`
- `assets/templates/wrap-report-template.md`
