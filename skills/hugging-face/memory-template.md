# Memory Template - Hugging Face

Create `~/hugging-face/memory.md` with this structure:

```markdown
# Hugging Face Memory

## Status
status: ongoing
version: 1.0.0
last: YYYY-MM-DD
integration: pending | complete | paused | never_ask

## Environment Context
- Project:
- Preferred runtime:
- Latency budget:
- Cost ceiling:
- License posture:

## Active Objectives
- Objective | Success metric | Deadline

## Preferred Sources
- Models:
- Datasets:
- Spaces:

## Model Shortlist
- model_id | task | license | hosting option | current rank

## Evaluation Log
- date | model_id | benchmark set | score | decision

## Endpoint Notes
- endpoint | auth mode | limits | last check

## Notes
- Short observations safe to persist.

---
*Updated: YYYY-MM-DD*
```

## Status Values

| Value | Meaning | Behavior |
|-------|---------|----------|
| `ongoing` | context still evolving | keep refining defaults from real tasks |
| `complete` | stable context available | run faster with stored defaults |
| `paused` | memory updates paused | read-only memory behavior |
| `never_ask` | no setup prompts | avoid setup follow-up prompts |

## Key Principles

- Store durable decisions, not full conversation transcripts.
- Record license and access constraints next to each shortlisted artifact.
- Keep benchmark logs minimal but reproducible.
- Never store tokens, secrets, or private keys in memory files.
