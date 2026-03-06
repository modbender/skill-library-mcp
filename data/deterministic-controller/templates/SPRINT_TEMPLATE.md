### Sprint Plan Template (single project)

**Project:** `<PROJECT NAME> (vX.Y)`  
**Sprint state:** `PAUSED`  
**Spec authority:**  
- `<path/to/spec.md>` (canonical)  
- `<path/to/contracts-or-schema.md>` (optional)

**Goal (one sentence):**  
- `<What “done” means in plain English>`

**Non-goals:**  
- `<Explicitly excluded work #1>`  
- `<Explicitly excluded work #2>`

**Assumptions / Constraints:**  
- `<e.g., research-only / no external actions / requires no credentials / time horizon>`  
- `<e.g., platform/OS constraints>`

#### Definition of Done (project-level; evidence-gated)
- [ ] `<DoD item>` — Evidence: `<path/to/artifact>`  
- [ ] `<DoD item>` — Evidence: `<path/to/artifact>`  
- [ ] `<DoD item>` — Evidence: `<path/to/artifact>`

---

#### Step table (deterministic execution queue)

| # | Step (action + completion condition) | Status | Evidence/Output |
|---|---|---|---|
| 1 | Create/update `<spec path>` with required sections: `<Section A, B, C…>`. Completion: file exists and contains all sections. | TODO | `<path/to/spec.md>` |
| 2 | Create repository skeleton under `<project dir>`: `<list of dirs/files>`. Completion: all paths exist. | TODO | `<project dir>/` |
| 3 | Define data contracts / schemas for `<objects>` (format: JSON Schema/YAML). Completion: schema files exist and validate (if applicable). | TODO | `<project dir>/docs/contracts/*.json` |
| 4 | Implement `<component A>` (scope: `<tight scope>`). Completion: command `<exact command>` produces `<artifact>`. | TODO | `<project dir>/runs/<run_id>/artifact_A.json` |
| 5 | Implement `<component B>` (scope: `<tight scope>`). Completion: command `<exact command>` produces `<artifact>`. | TODO | `<project dir>/runs/<run_id>/artifact_B.json` |
| 6 | Integration run: execute end-to-end command sequence. Completion: run folder contains `<list of required artifacts>` with non-empty outputs. | TODO | `<project dir>/runs/<run_id>/*` |
| 7 | Generate final deliverable/report. Completion: output file exists and matches required template sections. | TODO | `<project dir>/reports/<id>.md` |
| 8 | Write closure note (what was built, how to run it, known limitations, next backlog). Completion: file exists. | TODO | `<project dir>/docs/closure.md` |

---

#### BLOCKED (only if human action is required)

| Item | Blocker | Unblock Condition | Owner |
|------|---------|-------------------|-------|
| None | No active blockers. | N/A | manager |
