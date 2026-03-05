# Organization Root (Org Root)

> This is the single entrypoint for the whole multi-agent organization. Every new agent, department, or project starts here.

---

## 1) Why This Exists
- **Unified entrypoint**: All agents know where global memory, tasks, and reusable assets live.
- **Single source of truth**: Project progress is never scattered across chat sessions.
- **Department collaboration**: Minimal-cost cross-department reuse and communication via Markdown + cron.

---

## 2) Boot Sequence (mandatory, every session)
Every agent, before doing any work, reads in order:
1. `TASKBOARD.md` — Today's priorities + most important tasks
2. `DEPARTMENTS/<dept>/HANDOFF.md` — Your department's current state / blockers / next steps
3. `ASSET_REGISTRY.md` — Check for reusable assets (reuse first, build second)
4. `MEMORY_POLICY.md` — Where to write what

---

## 3) Directory Navigation
- Task board: `TASKBOARD.md`
- Memory & persistence rules: `MEMORY_POLICY.md`
- Pipeline framework (project lifecycle): `PIPELINE_GUIDE.md`
- Pipeline design doc: `PROJECTS/pipeline-framework/DESIGN.md`
- Reusable asset registry: `ASSET_REGISTRY.md`
- Reuse requests: `REUSE_REQUESTS.md`
- Departments: `DEPARTMENTS/`
- Projects: `PROJECTS/`
- Announcements: `ANNOUNCEMENTS/`

---

## 4) Hard Rules
- Any important conclusion must be persisted to: department `HANDOFF.md` or project `STATUS.md` / `DECISIONS.md`.
- Never just say "done" in chat without a file link.
- System-level config changes (gateway/channels/infra): only the reliability/SRE department may execute. Others submit change requests.
- Projects with clear goals and deliverables must use the Pipeline framework. Maintenance/patrol crons are exempt. See `PIPELINE_GUIDE.md`.
- Pipeline artifacts must be written to `PROJECTS/<project>/pipeline/`, archived to `pipeline_archive/` after each run.

---

## 5) Organization Structure (example)
- **CEO / Controller**: You (the human)
- **Departments**:
  - Research — domain-specific research projects
  - Engineering — implementation and coding
  - Reliability / SRE — system stability, healthchecks, auto-repair
  - Infrastructure — shared tooling, crawlers, platform services

(See `DEPARTMENTS/` for each department's `CHARTER.md`)
