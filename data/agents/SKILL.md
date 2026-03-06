---
name: Agents
description: Design, build, and deploy AI agents with architecture patterns, framework selection, memory systems, and production safety.
---

## When to Use

Use when designing agent systems, choosing frameworks, implementing memory/tools, specifying agent behavior for teams, or reviewing agent security.

## Quick Reference

| Topic | File |
|-------|------|
| Architecture patterns & memory | `architecture.md` |
| Framework comparison | `frameworks.md` |
| Use cases by role | `use-cases.md` |
| Implementation patterns & code | `implementation.md` |
| Security boundaries & risks | `security.md` |
| Evaluation & debugging | `evaluation.md` |

## Before Building — Decision Checklist

- [ ] **Single purpose defined?** If you can't say it in one sentence, split into multiple agents
- [ ] **User identified?** Internal team, end customer, or another system?
- [ ] **Interaction modality?** Chat, voice, API, scheduled tasks?
- [ ] **Single vs multi-agent?** Start simple — only add agents when roles genuinely differ
- [ ] **Memory strategy?** What persists within session vs across sessions vs forever?
- [ ] **Tool access tiers?** Which actions are read-only vs write vs destructive?
- [ ] **Escalation rules?** When MUST a human step in?
- [ ] **Cost ceiling?** Budget per task, per user, per month?

## Critical Rules

1. **Start with one agent** — Multi-agent adds coordination overhead. Prove single-agent insufficient first.
2. **Define escalation triggers** — Angry users, legal mentions, confidence drops, repeated failures → human
3. **Separate read from write tools** — Read tools need less approval than write tools
4. **Log everything** — Tool calls, decisions, user interactions. You'll need the audit trail.
5. **Test adversarially** — Assume users will try to break or manipulate the agent
6. **Budget by task type** — Use cheaper models for simple tasks, expensive for complex

## The Agent Loop (Mental Model)

```
OBSERVE → THINK → ACT → OBSERVE → ...
```

Every agent is this loop. The differences are:
- What it observes (context window, memory, tool results)
- How it thinks (direct, chain-of-thought, planning)
- What it can act on (tools, APIs, communication channels)
