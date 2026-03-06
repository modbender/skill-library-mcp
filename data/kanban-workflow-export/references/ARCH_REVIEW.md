# Kanban Workflow architecture review (current → recommended)

Date: 2026-02-26

This document reviews the current Kanban Workflow codebase architecture and proposes a best-practice structure for a sustainable “ports/adapters + command layer + scheduling/automation + state store” design.

> Scope: TypeScript library + small CLI in this repo (`openclaw-skill-kanban-workflow`).

---

## 1) Current architecture (as implemented)

### High-level shape

- **Domain-ish primitives**
  - `src/stage.ts`: canonical stage keys + `Stage` normalization
  - `src/models.ts`: `WorkItem` schema
  - `src/events.ts`: event schemas

- **Snapshot polling + diff**
  - `src/runner.ts`: `tick(adapter, previousSnapshot?)` → fetch snapshot + diff
  - `src/diff.ts`: snapshot diffing to produce events

- **Adapter layer**
  - `src/adapter.ts`: a single `Adapter` interface that combines multiple responsibilities:
    - snapshot fetching (`fetchSnapshot()`)
    - “workflow verbs” (list by stage, set stage, add comment, create, whoami, etc.)
  - `src/adapters/*`: platform adapters, implemented mostly as thin wrappers around CLIs

- **Verb layer (workflow API)**
  - `src/verbs/verbs.ts`: `show/next/start/update/ask/complete/create`
  - `src/verbs/types.ts`: `VerbAdapter` shape (currently very close to `Adapter`)
  - `src/verbs/next_selection.ts`: deterministic selection logic

- **CLI layer**
  - `src/cli.ts`: flags parsing, config loading, setup orchestration, and verb execution
  - `src/setup.ts`: “write config after validation”
  - `src/config.ts`: config schema + file read/write

- **Automations (early)**
  - `src/automation/progress_updates.ts`: a helper function to post periodic progress comments while `stage:in-progress`

### What’s working well

- **Deterministic tick core**: `tick()` is clean and side-effect-free (good for cron/webhook environments).
- **CLIs as auth boundary**: adapters rely on the platform CLI session (aligned with the “no direct HTTP auth” constraint).
- **Verb helpers are small** and mostly platform-agnostic.
- **Vitest coverage** exists for key pieces (selection, diff, CLI tips, setup).

---

## 2) Key architectural issues / risks

### 2.1 Mixed responsibilities in `Adapter`

`Adapter` currently acts as:
- a snapshot source (`fetchSnapshot()`)
- a workflow actor (add comment, set stage, create, whoami)
- a query API for selection (`listIdsByStage`, backlog ordering)

This makes it harder to:
- test behaviors in isolation
- extend with partial capability adapters (e.g., read-only adapters)
- add new automations with clear boundaries

### 2.2 CLI is doing orchestration + parsing + policy

`src/cli.ts` currently:
- parses flags
- constructs config objects
- loads config
- constructs adapters
- runs setup validations
- invokes verbs

This is fine for an MVP, but becomes brittle as you add:
- multiple commands
- shared validation
- richer error reporting
- scheduling / automation control

### 2.3 No first-class “state store” concept

Kanban Workflow has at least 3 categories of state:
1. **Config** (`config/kanban-workflow.json`) — versioned, user-controlled
2. **Snapshots** (last polled snapshot per adapter) — operational state
3. **Automation cursors/dedupe** (e.g., last auto-comment time per work item)

Only config is formalized.

Without a state store abstraction, every new automation risks inventing its own persistence scheme.

### 2.4 Scheduling is out-of-band

Requirements imply periodic behavior (every 5 minutes while in-progress). The code currently provides a helper, but there is no cohesive “scheduler-friendly” entrypoint that:
- loads state
- runs `tick()`
- applies rules/automations
- persists updated state

### 2.5 Logging / observability isn’t structured

Adapters call CLIs, which can fail for many reasons (not installed, not authenticated, permission errors, rate limits).

Right now errors bubble as exceptions with string messages. There’s no consistent:
- log context (adapter name, command, id)
- classification (setup-required vs transient)
- “user-facing” vs “debug” output

---

## 3) Recommended architecture (ports & adapters + command layer)

### 3.1 Layered layout (suggested)

Keep the public API stable, but internally move toward:

```
src/
  core/
    domain/            # Stage, WorkItem, Comment, enums
    ports/             # interfaces/ports (read/write), small & composable
    usecases/          # verbs + automations (pure orchestration)
  adapters/
    github/
    linear/
    plane/
    planka/
    cli/               # CliRunner wrappers and JSON parsing helpers
  config/
    schema.ts
    load.ts
    write.ts
  state/
    store.ts           # StateStore port
    json_file_store.ts # implementation (fs)
    types.ts           # snapshot + automation state
  cli/
    parse.ts
    commands/
      setup.ts
      show.ts
      next.ts
      start.ts
      update.ts
      ask.ts
      complete.ts
      create.ts
      tick.ts          # optional: scheduler entrypoint
  index.ts             # re-exports
```

### 3.2 Ports (interfaces) that stay small

Instead of one big `Adapter`, define composable ports:

- **IdentityPort**
  - `whoami(): Promise<{ id?: string; username?: string; name?: string }>`

- **WorkItemReadPort**
  - `getWorkItem(id)`
  - `listIdsByStage(stage)`
  - `listBacklogIdsInOrder()`
  - `listLinkedWorkItems(id)`
  - `listAttachments(id)`
  - `listComments(id, ...)`

- **WorkItemWritePort**
  - `addComment(id, markdown)`
  - `setStage(id, stageKey)`
  - `createInBacklogAndAssignToSelf({title, body})`

- **SnapshotPort**
  - `fetchSnapshot(): Promise<Map<string, WorkItem>>`

Adapters can implement all ports, but tests/use-cases can depend on only what they need.

### 3.3 Use-cases (command/verb layer)

Make “verbs” and “automations” be use-cases that accept ports:

- Verbs:
  - `show(WorkItemReadPort, id)`
  - `next(WorkItemReadPort, selectionPolicy)`
  - `start(WorkItemWritePort, id)`
  - etc.

- Automations:
  - `runProgressAutoUpdates(WorkItemReadPort + WorkItemWritePort, StateStore, Clock)`
  - `runAutoReopenOnHumanComment(...)` (event-driven once comment events exist)

### 3.4 Scheduling / “tick runner” composition

Keep `tick()` pure, and add a *separate* orchestration entrypoint:

- `runScheduledPass({ adapter, stateStore, clock })`:
  1. load previous snapshot + automation cursors
  2. `tick()` to compute events
  3. apply automations based on snapshot/events
  4. persist updated snapshot/state
  5. emit a summary

This becomes the cron-friendly entrypoint.

### 3.5 Config + validation

- Keep `config/kanban-workflow.json` for the *selected adapter + mapping*.
- Implement setup validation as a reusable use-case:
  - `validateAdapterReadiness(adapter, config)`
  - returns typed errors: `CliMissing`, `NotAuthenticated`, `PermissionDenied`, etc.

### 3.6 Logging

- Add a `Logger` port with levels: `debug/info/warn/error`.
- In CLI mode, log user-facing summaries to stdout/stderr.
- In library mode, allow a structured logger (pino/winston-like) but don’t require a dependency; keep a small port.

---

## 4) Step-by-step refactor plan (milestones)

The goal is to improve structure without breaking current behavior.

### Milestone 0 — Baseline safety (now)

- Ensure `npm test` is green.
- Keep existing exports working via `src/index.ts`.

### Milestone 1 — Introduce ports without moving code

- Create `src/core/ports/*` interfaces.
- Update verbs to depend on ports (types-only change).
- Keep adapters implementing the existing `Adapter` interface, but make it extend the smaller ports internally.

Deliverable:
- No runtime changes; only types and imports.

### Milestone 2 — Create a real state store abstraction

- Add `StateStore` port:
  - `loadAutomationState()` / `saveAutomationState()`
  - `loadSnapshot()` / `saveSnapshot()`
- Provide `JsonFileStateStore` implementation writing under `data/`.

Deliverable:
- A single place to manage persistence.

### Milestone 3 — Add a scheduler-friendly orchestration entrypoint

- Add `runScheduledPass()` use-case that composes:
  - state store
  - `tick()`
  - progress updates automation

Deliverable:
- A single function usable by cron.

### Milestone 4 — CLI modularization

- Move `src/cli.ts` into `src/cli/*` modules:
  - parsing
  - commands
  - shared error formatting

Deliverable:
- CLI behavior unchanged; improved maintainability.

### Milestone 5 — Adapter module boundaries

- Ensure each adapter has:
  - `cli/*` wrappers (command execution + JSON parsing)
  - mapping helpers (stage mapping)
  - a small facade implementing ports

Deliverable:
- Adapters are easier to test and reason about.

### Milestone 6 — Add remaining automations (optional)

- Auto-reopen when human comments on `stage:blocked` or `stage:in-review`.
  - Requires comment event modeling (either via polling/diff of comments, or platform event APIs).

---

## 5) Notes on constraints ("no direct HTTP auth")

The recommended architecture keeps auth concerns in platform CLIs:
- adapters never manage OAuth tokens directly
- any HTTP calls (if needed) must use the CLI (`gh api`, `linear-cli`, `plane-cli`, `planka-cli`) as the execution/auth boundary

---

## 6) Suggested next actions

1. Implement Milestone 1 (ports) — low risk, mostly types.
2. Implement a JSON file `StateStore` and a `runScheduledPass()` orchestration function.
3. Decide whether Kanban Workflow should ship a first-class `kanban-workflow tick` CLI command or remain library-first.
