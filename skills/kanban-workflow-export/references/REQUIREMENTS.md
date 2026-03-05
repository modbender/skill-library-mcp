# Kanban Workflow requirements (draft)

This document captures the initial Q&A requirements for Kanban Workflow’s verb-level workflow API.

## Design constraints

- **Canonical state machine:** use existing `stage:*` lifecycle.
- **CLI-first auth:** adapters must use platform CLIs/scripts for auth/session. Kanban Workflow does not run interactive OAuth flows or persist secrets, but adapter CLIs may require environment variables (API keys) and may make HTTPS calls internally.
- **Multi-scope (future):** Kanban Workflow should support monitoring multiple scopes per adapter (e.g. all Plane projects, multiple Linear teams/projects, multiple GitHub repos/projects). Constraint: all monitored scopes must share consistent stage/state names so a single `stageMap` works.
- **Assigned-only autopilot:** autopilot selection should be able to operate on items assigned to the current user only (initial implementation: Plane).
- **Cross-platform:** GitHub, Planka, Plane, Linear.

## Canonical stage names

Kanban Workflow’s canonical stages are (and these are the **only** stages the agent should consider):

- `stage:backlog`
- `stage:blocked`
- `stage:in-progress`
- `stage:in-review`

Notes:
- “Done/closed” is platform-specific and not currently part of the canonical stage set.

## Setup

Kanban Workflow must provide a `setup` command to configure enabled adapters and scope/order mappings.

### Setup command (flags-only)

Setup must be **non-interactive** and configured entirely via flags.

General:
- `--adapter <github|plane|linear|planka>` (exactly one)
- `--force` (required to overwrite an existing `config/kanban-workflow.json`)

Stage mapping (required; all 4 stages):
- `--map-backlog <platform-name>`
- `--map-blocked <platform-name>`
- `--map-in-progress <platform-name>`
- `--map-in-review <platform-name>`

Adapter-specific scope/order flags:

**GitHub**
- `--github-repo <owner/repo>`
- `--github-project-number <number>` (explicit backlog ordering)

**Plane**
- `--plane-workspace-slug <slug>`
- `--plane-project-id <uuid>`
- Optional: `--plane-order-field <field>` (only if manual UI order is not detectable; otherwise fallback to updatedAt)

**Linear**
- Scope (choose exactly one):
  - `--linear-team-id <id>` or
  - `--linear-project-id <id>`
- Ordering:
  - `--linear-view-id <id>` (preferred; if not accessible, fallback to updatedAt)

**Planka**
- `--planka-board-id <id>`
- `--planka-backlog-list-id <id>` (needed for backlog ordering by card position; other stages can be mapped by list name)

### Setup validations

- Setup must test that required CLIs are installed and authenticated and **fail hard** if the selected adapter check fails.
- Setup must validate all **read-only verbs** for the selected adapter: `show` prerequisites (read body/description, list comments, list attachments where supported) and `next` prerequisites (list backlog + ordering inputs).
- Setup validations are **read-only** (no comments/transitions/creates during setup).

### Config

- Config storage: store config in-repo (versionable) under `config/kanban-workflow.json`.
- Only **one** config file/profile is supported (no multiple profiles).

## UX requirement: next-step tips

Every verb execution must output a **"What next"** tip.

- If setup is not completed (no valid `config/kanban-workflow.json`), **all commands** must error and instruct the user to complete setup.
- After successful `setup`: suggest `next`.
- After `next`: suggest `start`.
- After `start`: suggest `ask` or `update`.
  - Additionally, after `start` include a tip to run the actual execution/implementation work in a **subagent**.
- After `ask`: suggest `next`.
- After `update`: suggest `complete`.
- After `complete`: suggest `next`.

## Required verbs (MVP)

### 0) `show`

**Goal:** show the content of a specific ticket/work item on demand (even if it is not the next item).

- Input: platform scope + work item identifier.
- Output: title, current stage, URL, **full body/description**, relevant metadata (assignees/labels/state), **attachments (filename + URL) where supported**, and the **last 10 comments** (most recent first), including **private/internal** comments where supported.
  - Each comment entry includes: **author + timestamp + content**.
- Also include: titles of any linked/related tickets (e.g., blocks/blocked-by/duplicates) where supported.
- Use case: follow linked/blocked tickets during implementation.

### 1) `next`

**Goal:** return the next work item the agent should work on.

- `next` returns **exactly one** ticket (no "up next" list).
- `next` must return the same payload shape as `show` (i.e., it should reuse the `show` implementation to display the selected ticket: full body/description, last 10 comments incl. private, and titles of linked/related tickets where supported).

- Primary need: *only* `next` for discovery/selection.
- Selection policy TBD (see open questions), but should be deterministic.

### 2) `update`

- Post a progress update comment on a task.
- **No enforced template**; post the provided text as-is.
- No stage change.

### 3) `complete`

- Requires a short completion **summary** string.
- Post a **Completed** comment including that summary.
- Move the task to `stage:in-review`.

### 4) `ask`

- Requires clarification request **text**.
- Post a clarification request comment including that text.
- Move the task to `stage:blocked`.

### 5) `start`

- Required stage change verb: `start`.
- Behavior: transition task into `stage:in-progress`.
- No comment is posted on `start`.

### 6) `create`

**Goal:** create a new task in `stage:backlog` and automatically assign it to the agent itself.

- Must create work item in the target platform.
- Must apply/encode `stage:backlog`.
- Must assign to the agent identity.
- Keep `create` minimal for now (no linked-ticket relationships created at creation time).
- `create` does **not** auto-start; it leaves the task in `stage:backlog`.

## Not required (explicitly)

- Assignment verbs (`assign`, `unassign`) are **not** needed beyond `create` auto-assign.
- Explicit `transition` to `stage:in-review` is **not** needed (happens automatically on `complete`).
- `sync-stages` is **not** needed.

## Continuous status updates (5-minute cadence)

While a task is in `stage:in-progress`, Kanban Workflow must post an **automatic progress update comment every 5 minutes** describing:

- what is currently being worked on
- what the next step is

This should stop when the task leaves `stage:in-progress`.

## Automation rules

### Auto-reopen

Reopening should happen automatically when a human comments on a task that is:

- `stage:blocked`, or
- `stage:in-review`

Reopen target stage:
- On human comment, automatically move the task to `stage:backlog`.
- Auto-reopen is silent (no automatic comment is posted).

## CLI identity discovery (“self”) requirement

For `create` (auto-assign to self) and any future ownership logic, Kanban Workflow must be able to discover the current authenticated user from the platform CLI.

- **GitHub:** use `gh api user` → `login`
- **Linear:** use `scripts/linear_json.sh whoami` (JSON; requires `LINEAR_API_KEY`)
- **Plane:** use ClawHub skill `plane` (owner: `vaguilera-jinko`): `plane me` (JSON)
- **Planka:** `planka-cli status` shows the current user, but output is human-formatted.
  - **Recommended approach:** ship a small **wrapper script** (CLI-auth compliant) that returns `whoami` as **JSON** for Planka, rather than parsing formatted output.

## Clarified implementation rules

### `next`

- Guard:
  - If **exactly 1** task is in `stage:in-progress`: `next` returns an error (don’t assign a second task).
  - If **more than 1** task is in `stage:in-progress`: `next` returns an error (inconsistent state).
- Ignore `stage:in-review` for selection.
- Eligible pool: select from `stage:backlog`.
- Empty backlog: return an **info** response (“no work to do”).
- Ordering:
  - Prefer explicit human ordering when available (configured during setup; see adapter-specific flags).
  - Otherwise fallback to `updatedAt` descending.

### `create` stage + assignment

- Input: title + Markdown body.
- Stage on create: do **not** override platform defaults at runtime; rely on the platform configuration done during onboarding/setup.
  - (I.e., the platform’s “new item” default should correspond to the mapped canonical `stage:backlog`.)
- Assignment: must assign to self as discovered via the CLI `whoami` mechanism; **fail hard** if self cannot be resolved or assignment cannot be performed.

### Auto-reopen

- Trigger: human comment on a task in `stage:blocked` or `stage:in-review`.
- Action: silently move the task to `stage:backlog`.

### Message formats

- All user-provided text for `update/ask/complete` is **Markdown**.
- Adapters may convert Markdown to platform-native formats if required, but Markdown is the canonical input.

## Documentation requirements

- When implementing or changing behavior, keep **README.md** and **SKILL.md** in sync with the current requirements and available commands.

## Implementation notes (for later)

- These verbs imply the adapter port must support idempotent writes:
  - post comment
  - create work item
  - set stage (platform state/labels/lists)
  - set assignee (create only)
- `next` + auto-reopen require polling/diffing event detection unless the platform webhook/CLI provides events.
