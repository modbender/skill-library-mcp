# Kanban Workflow Core Skill — Technical Plan

**Scope**: Define the platform-agnostic “Kanban Workflow core” plus a pluggable adapter layer for PM systems (GitHub/Planka/OpenProject/etc.) that uses **CLI-managed auth** (no direct HTTP auth handling in core).

**Primary entrypoint**: `kanban-workflow tick` (deterministic worker pass). Optional: `kanban-workflow webhook` only where inbound events are available without managing auth.

---

## 1) Design goals / non-goals

### Goals
- **Canonical stage lifecycle** as the shared state machine:
  - `stage:backlog`, `stage:queued`, `stage:needs-clarification`, `stage:ready-to-implement`, `stage:in-progress`, `stage:in-review`, `stage:blocked`, plus platform-specific done/closed.
- **Ports & adapters** architecture: core holds rules and state; adapters translate between core model and platform specifics.
- **Deterministic tick**: same inputs + same config/state ⇒ same decisions.
- **Idempotent actions**: safe re-runs; dedupe on action keys.
- **Polling + snapshot diff** support for platforms without robust event feeds.

### Non-goals
- A full multi-tenant PM product.
- OAuth/token handling in Kanban Workflow core.
- Perfect real-time sync (tick cadence is acceptable).

---

## 2) Canonical domain model

### Identifiers
Use stable, adapter-scoped IDs.
- `AdapterId`: string (e.g. `github`, `planka`)
- `WorkItemId`: `{adapter}:{native_id}` (e.g. `github:repo#123`, `planka:card:abcd`)
- `ProjectId`: `{adapter}:{native_id}`

### Entities
Keep these as the *core* schema; adapters map into/out of them.

```text
Stage
- BACKLOG | QUEUED | NEEDS_CLARIFICATION | READY_TO_IMPLEMENT
- IN_PROGRESS | IN_REVIEW | BLOCKED | DONE (normalized)

WorkItem
- id: WorkItemId
- project_id: ProjectId
- title: str
- body: str | None
- stage: Stage
- labels: set[str]                # includes canonical stage labels where relevant
- assignees: set[str]             # platform usernames
- priority: str | None            # optional normalized priority (P0..P3 or similar)
- url: str | None
- updated_at: datetime | None
- etag/version: str | None        # adapter-provided version cursor if available

Comment
- id: str (adapter-native)
- work_item_id: WorkItemId
- author: str
- body: str
- created_at: datetime

Snapshot
- work_item_id: WorkItemId
- captured_at: datetime
- payload_hash: str               # hash of normalized snapshot for diffing
- payload_json: dict              # minimal normalized snapshot used by core
```

### Canonical events
Events are produced by adapters (webhook/poll/diff) and consumed by core.

```text
Event (base)
- id: str                         # globally unique; used for dedupe
- adapter: AdapterId
- occurred_at: datetime
- work_item_id: WorkItemId | None
- kind: str
- payload: dict

Kinds
- WorkItemCreated
- WorkItemUpdated
- StageChanged
- CommentAdded
- CommentEdited (optional)
- WorkItemClosed / WorkItemReopened (optional)
```

**Normalization rule**: core only relies on canonical fields + `payload` for adapter-specific extras.

---

## 3) Ports (internal adapter interface)

Adapters are responsible for:
1) **Reading** platform state (list items, fetch details, list comments).
2) **Writing** platform changes (add comment, set stage/labels, assign, close/reopen).
3) Providing an **event stream** via either:
   - webhooks → `ingest_webhook(...) → list[Event]`, or
   - polling → `poll(...) → list[Event]` (often implemented with snapshot diff).

### Python interface (Protocol / ABC)

```python
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from typing import Iterable, Optional, Protocol

@dataclass(frozen=True)
class PollCursor:
    value: str

@dataclass(frozen=True)
class ActionResult:
    action_id: str
    ok: bool
    message: str | None = None

class Kanban WorkflowAdapter(Protocol):
    adapter_id: str

    # --- read
    def list_projects(self) -> list[Project]: ...
    def list_work_items(self, project_id: ProjectId, *, cursor: Optional[PollCursor]) -> tuple[list[WorkItem], Optional[PollCursor]]: ...
    def get_work_item(self, work_item_id: WorkItemId) -> WorkItem: ...
    def list_comments(self, work_item_id: WorkItemId, *, since: Optional[datetime] = None) -> list[Comment]: ...

    # --- event ingestion
    def poll_events(self, project_id: ProjectId, *, cursor: Optional[PollCursor]) -> tuple[list[Event], Optional[PollCursor]]: ...
    def ingest_webhook(self, *, headers: dict[str, str], body: bytes) -> list[Event]: ...

    # --- writes (idempotent where possible)
    def ensure_stage(self, work_item_id: WorkItemId, stage: Stage) -> ActionResult: ...
    def add_comment(self, work_item_id: WorkItemId, body: str, *, dedupe_key: str) -> ActionResult: ...
    def set_labels(self, work_item_id: WorkItemId, labels: set[str]) -> ActionResult: ...
    def set_assignees(self, work_item_id: WorkItemId, assignees: set[str]) -> ActionResult: ...
    def close_work_item(self, work_item_id: WorkItemId) -> ActionResult: ...
```

### Adapter implementation constraints
- **CLI-only auth**: adapters call CLIs (`gh`, `planka-cli`, `openproject-cli`, etc.) and parse outputs.
- Outputs should be requested as **JSON** when CLIs support it.
- Adapters should return *normalized* entities and events.
- Adapters must provide **stable cursors** when possible, otherwise rely on snapshots + timestamps.

---

## 4) State storage & dedupe

We need persistent state for:
- per-project polling cursors
- last-seen snapshots for diffing
- processed event IDs (dedupe)
- emitted action IDs (idempotency)

### Recommended: SQLite (default)
Use a small SQLite DB under skill-local `data/`:
- Pros: robust, queryable, good for dedupe, safe concurrency with simple locking.
- Cons: slightly more setup than JSON.

Schema sketch:
```sql
-- Cursors per adapter+project
CREATE TABLE cursors (
  adapter TEXT NOT NULL,
  project_id TEXT NOT NULL,
  cursor TEXT,
  updated_at TEXT NOT NULL,
  PRIMARY KEY (adapter, project_id)
);

-- Latest normalized snapshot hash to generate synthetic events
CREATE TABLE snapshots (
  work_item_id TEXT PRIMARY KEY,
  payload_hash TEXT NOT NULL,
  payload_json TEXT NOT NULL,
  captured_at TEXT NOT NULL
);

-- Dedupe incoming events
CREATE TABLE processed_events (
  event_id TEXT PRIMARY KEY,
  occurred_at TEXT NOT NULL,
  adapter TEXT NOT NULL,
  kind TEXT NOT NULL
);

-- Dedupe outgoing actions (comment/stage changes)
CREATE TABLE emitted_actions (
  action_id TEXT PRIMARY KEY,
  work_item_id TEXT,
  kind TEXT NOT NULL,
  dedupe_key TEXT,
  created_at TEXT NOT NULL
);
```

### JSON (optional, fallback)
Support a `--state-backend json` for quick demos:
- `state/cursors.json`, `state/snapshots.json`, `state/processed_events.json`.
- Must implement compaction/TTL to avoid unbounded growth.

### TTL / compaction rules
- `processed_events`: keep N days (e.g. 30) or last N entries per adapter.
- `snapshots`: keep only latest per work item.
- `emitted_actions`: keep N days (e.g. 90) for idempotency.

---

## 5) Tick loop algorithm (deterministic)

`kanban-workflow tick` performs one pass:

1) **Load config**
   - adapters enabled, projects to watch, tick options (max items/events), stage rules.

2) **For each (adapter, project)**
   - load `cursor` from state.
   - call `adapter.poll_events(project_id, cursor)`.
   - store updated cursor.

3) **Normalize + dedupe**
   - drop events whose `event_id` already exists in `processed_events`.
   - store new `event_id`s.

4) **Materialize current item state (as needed)**
   - for events referencing items, fetch `WorkItem` details if event payload is insufficient.
   - maintain/update latest `Snapshot` (store `payload_hash`).

5) **Rules engine (core decisions)**
   - input: events + current WorkItem.
   - output: ordered `PlannedAction[]`.

   Examples of core rules:
   - If `stage:queued` and missing required fields → move to `stage:needs-clarification` and comment with questions.
   - If clarified (answers present) → move to `stage:ready-to-implement`.
   - If blocked keyword detected → move to `stage:blocked` and request dependency.

6) **Action execution (idempotent)**
   - for each planned action, compute `action_id = hash(adapter + work_item_id + kind + dedupe_key)`.
   - if `action_id` exists in `emitted_actions`, skip.
   - otherwise call adapter write method; record result.

7) **Report**
   - print a compact summary: events ingested, actions executed/skipped, errors.

**Error strategy**:
- Fail-soft per project; continue other projects.
- Persist cursors only after successful poll parse; never advance cursor past unprocessed events.

---

## 6) Snapshot-diff event synthesis (poll mode)

When platforms don’t provide a usable event feed, implement:

- Poll list of work items (possibly since `updated_at >= last_tick` when supported).
- For each work item, compute a **normalized snapshot** (stable field ordering).
- Compare `payload_hash` to stored `snapshots.payload_hash`.
- If changed, emit `WorkItemUpdated` and (if stage differs) also `StageChanged`.
- Store new snapshot.

Normalization should exclude noisy fields (view counts, sync tokens) to avoid churn.

---

## 7) Repo layout proposal

This skill repo currently is documentation/scripts only. Plan for eventual implementation:

```text
openclaw-skill-kanban-workflow/
  SKILL.md
  references/
    TECH_PLAN.md
    schemas/
      domain.schema.json
      events.schema.json
  assets/
    runbooks/
    templates/
  scripts/
    github/
      gh_list_items.sh
      gh_get_item.sh
  src/ (when code is introduced)
    kanban-workflow/
      core/
        engine.py        # tick loop + rule evaluation
        rules.py
        domain.py        # entities + event types
        state/
          sqlite.py
          json.py
      adapters/
        github/
          adapter.py
        planka/
          adapter.py
        openproject/
          adapter.py
      cli/
        main.py          # `kanban-workflow tick`, `kanban-workflow webhook`
  tests/
    core/
    adapters/
```

---

## 8) Milestones checklist (short)

- [ ] Define canonical domain types (Stage, WorkItem, Event) + JSON schema in `references/schemas/`.
- [ ] Implement `Kanban WorkflowAdapter` port and `PlannedAction` contract in core.
- [ ] Implement state backends: SQLite (default) + JSON (fallback).
- [ ] Implement `tick` engine with dedupe + idempotent action execution.
- [ ] Implement GitHub adapter using `gh` (poll + snapshot diff) and basic write ops (comment, labels/stage mapping).
- [ ] Add minimal end-to-end harness: `kanban-workflow tick --adapter github --project <repo>`.
- [ ] Add regression tests for: stage mapping, snapshot diff → events, action dedupe.
