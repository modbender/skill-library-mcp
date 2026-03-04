---
name: workflow-orchestrator
description: Structural parity skeleton for queue-driven orchestration in a workflow context.
user-invocable: true
version: "0.1"
allowed-tools: Read, Write, Edit, Grep, Glob, Bash
argument-hint: "[target] [--handoff] [--batch <id>] [--type <extract|create|reflect|reweave|verify>]"
---

## Contract

This skill is intentionally skeleton-only. It provides structure parity with canonical queue orchestration without plugin hooks.

Wave 2 execution parity includes:
- Setup derivation phase ordering: `detection -> understanding -> derivation -> proposal -> generation -> validation`
- Required persisted setup artifacts: `ops/derivation.md`, `ops/derivation-manifest.md`, `ops/config.yaml`
- In-skill lifecycle emulation routines (not real hook execution):
  - session orient
  - write-time validation checklist
  - stop/session capture persistence

## Argument Parsing

Parse arguments in this order:
1. positional `target` (optional)
2. `--handoff` (boolean)
3. `--batch <id>` (optional)
4. `--type <phase>` (optional)
5. unknown flags are non-fatal; report and ignore

If no `target` is supplied, list candidate inbox files and request explicit selection.

## Runtime Loader Requirements

Before doing queue work, load runtime context from:
- `ops/derivation-manifest.md` (if present)
- `ops/config.yaml` (if present)
- queue file with fallback precedence:
  1. `ops/queue/queue.yaml`
  2. `ops/queue/queue.yml`
  3. `ops/queue/queue.json`

If no queue file exists, fail safely with actionable remediation.

## Safety Constraints

Never:
- execute arbitrary shell from user-provided strings
- continue processing after parse/load failures
- mutate tasks outside declared queue schema fields
- call external plugins/hooks (explicitly out of scope)

Always:
- validate queue structure before state transitions
- make state transitions explicit (`extract -> create -> reflect -> reweave -> verify -> done`)
- produce deterministic handoff text when `--handoff` is set
- preserve resumability by reading persisted queue state first

## Scope Boundary

No plugin hooks are implemented in this skeleton.
Lifecycle behavior is emulated in-skill to preserve deterministic execution semantics only.

## Installation

To install the workflow-engine and enable its hooks:

```bash
# Clone or navigate to the workflow-engine directory
cd workflow-engine

# Run the install script to set up hooks
./install-hooks.sh

# Or manually enable hooks via openclaw
openclaw hooks enable session-orient
openclaw hooks enable write-validate
openclaw hooks enable session-capture
```
