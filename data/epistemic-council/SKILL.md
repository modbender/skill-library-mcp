---
name: Epistemic Council Skill
description: Use this skill for all Epistemic Council pipeline operations.
---

# Epistemic Council Skill

Use this skill for all Epistemic Council pipeline operations.

## Triggers
"run council", "run pipeline", "substrate status", "council status",
"health check", "validate claims", "check boundaries", "find gaps", "rechallenge"

## How to invoke

Use the `exec` tool with the epistemic_council working directory:

```
exec: cd /root/.openclaw/workspace-epistemic-council-bot/epistemic_council && python epistemic_skill.py "run council"
```

Available commands (replace argument as needed):
- `"run council"` — full pipeline run
- `"substrate status"` — event counts + last run summary
- `"health check"` — risk / integrity scan
- `"validate claims"` — re-evaluate challenged-zone claims
- `"check boundaries"` — domain boundary audit
- `"find gaps"` — orphan + sparse coverage scan
- `"rechallenge"` — adversarial re-challenge of top insight

## Workspace
`/root/.openclaw/workspace-epistemic-council-bot/`

## Working directory for exec
`/root/.openclaw/workspace-epistemic-council-bot/epistemic_council/`
