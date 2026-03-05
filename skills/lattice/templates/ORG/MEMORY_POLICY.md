# Memory & Persistence Policy

Goal: Agents don't rely on "remembering" — the process automatically persists knowledge to inheritable locations.

---

## 1) Memory Layering (Single Source of Truth)

### A. Org Level — cross-project facts only
Location: `ORG/`
- Org policies: Boot/Closeout, reuse policy, change control
- Agent roster, asset registry, reuse requests, announcements

Does NOT store:
- Project-internal TODOs
- Secrets / tokens / passwords

### B. Department Level — single source of truth per team
Location: `ORG/DEPARTMENTS/<dept>/`
Required files:
- `CHARTER.md` — mission, scope, inputs/outputs
- `RUNBOOK.md` — operational playbook + checklists
- `HANDOFF.md` — current state / next steps / blockers / recent output links
- `STATE.json` — machine-readable state (lastRun, cursor, seenIds, etc.)

### C. Project Level — single source of truth per project
Location: `ORG/PROJECTS/<project>/`
Minimum:
- `STATUS.md` — current progress and next steps
- `DECISIONS.md` — key decisions with rationale
- `RUNBOOK.md` — how to run / reproduce / deliver

Pipeline projects additionally require:
- `PIPELINE_STATE.json` — phase state machine (machine read/write, includes runNumber)
- `PIPELINE_LOG.jsonl` — phase transition log (append-only, spans all runs)
- `pipeline/` directory — current run artifacts
- `pipeline_archive/` directory — historical run archives (auto-archived after each Review PASS)

### D. Agent Workspace — personal only
- Temporary drafts, personal preferences (not a global source of truth)
- Should have a `GLOBAL_POINTER.md` pointing to Org Root

---

## 2) Mandatory Processes

### Boot Sequence (before any work)
1. Read `ORG/TASKBOARD.md`
2. Read your department's `HANDOFF.md`
3. Check `ASSET_REGISTRY.md` (reuse first, build second)
4. If reuse/integration needed: add entry to `REUSE_REQUESTS.md` and @owner

### Closeout Sequence (after work)
1. Update your department's `HANDOFF.md` (Done / Next / Blockers + links)
2. If output is reusable: register in `ASSET_REGISTRY.md` + write `ANNOUNCEMENTS/<date>-<asset>.md`
3. If project was advanced: update `PROJECTS/<project>/STATUS.md`
4. If project uses Pipeline: Orchestrator auto-updates PIPELINE_STATE.json + PIPELINE_LOG.jsonl (sub-agents just write artifacts to `pipeline/`)

---

## 3) Reuse Levels (L0 / L1 / L2)
- **L0 (ready to use)**: Has owner, stable I/O, minimal runbook, minimal tests
- **L1 (usable with coordination)**: Needs access/env/interface negotiation, must go through `REUSE_REQUESTS.md`
- **L2 (one-off delivery)**: No reuse guarantee; must be "upgraded" (add docs, tests, maintainer) to become L1/L0

---

## 4) Change Control
- **System-level config / networking / gateway / channels**: Only the reliability/SRE department may execute. Others submit change requests (in their HANDOFF blockers or a dedicated change entry).
- **Shared asset mainline**: Only the asset's maintainer may merge/release. Others submit PRs/requests.

---

## 5) External Communication Rules
- Designated spokesperson only.
- Default: read-only. Posting/replying requires explicit approval from the human controller.
- Other agents produce internal materials only, never publish directly.
