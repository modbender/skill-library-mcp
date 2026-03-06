## Design principles

- Treat memory as a system, not a dump: working, episodic, semantic, procedural.
- Write memory only with evidence and confidence.
- Prefer idempotent actions and deterministic outputs.
- Keep high-impact side effects gated.
- Keep memory auditable, reversible, and minimally invasive.

## Execution policy

- Default is execution mode: perform actions directly.
- Ask exactly one minimal question only when blocked by unclear irreversible operations.
- Only push, deploy, or publish externally when explicitly requested in this session or preapproved by project policy.
- Support `dry-run` mode to compute all actions and memory writes without side effects.

## Action gate matrix

| Action | Allowed | Ask | Blocked |
|---|---|---|---|
| Commit | Local repo changed and message is clear | Unclear scope for staged files | Repo locked or no write permission |
| Push | Explicit user request or explicit project policy | Ambiguous policy status | User says no push |
| Deploy | Explicit user request or explicit deploy policy | Deployment target unclear | No deploy script/skill or user says no deploy |
| Publish | Explicit user request | Platform/schedule ambiguous | No user approval |
