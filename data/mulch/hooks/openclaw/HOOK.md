---
name: self-improvement
description: "Mulch Self Improver 🌱 — Injects reminder at bootstrap: mulch prime, mulch record, promote. Better coding, less hallucination."
metadata: {"openclaw":{"emoji":"🌱","events":["agent:bootstrap"]}}
---

# Mulch Self Improver 🌱

Injects a short reminder on `agent:bootstrap` (main sessions only): run `mulch prime`, record with `mulch record`, promote to SOUL/AGENTS/TOOLS. Benefits: better and more consistent coding, improved experience, less hallucination.

## Behavior

- **Event:** `agent:bootstrap`
- **Skips:** sub-agent sessions (`sessionKey` containing `:subagent:`)
- **Adds:** virtual file `SELF_IMPROVEMENT_REMINDER.md` with Mulch workflow

## Enable

```bash
openclaw hooks enable self-improvement
```
