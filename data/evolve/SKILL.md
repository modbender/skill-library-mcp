---
name: evolve
description: Local DevOps/autonomy skill for OpenClaw (safe evolution loop with guardrails).
metadata: { "openclaw": { "emoji": "🧬" } }
---

# evolve

Local DevOps/autonomy skill for OpenClaw.

This skill provides a safe "evolution loop" controller (barandales) that:
- snapshots current status
- generates candidates
- tests candidates
- promotes candidates into active skills
- supports rollback

## Commands

- `evolve plan`
- `evolve generate <slug>`
- `evolve test <slug>`
- `evolve promote <slug>`
- `evolve rollback <slug>`

## Notes

This skill delegates to a local controller script (`evolvectl.sh`).
You can override its location with `EVOLVECTL`.
