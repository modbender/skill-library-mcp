---
name: craftwork
description: 9 engineering disciplines for AI agents — TDD, debugging, code review, planning, and multi-agent coordination. Build software like it matters.
version: 1.0.0
metadata:
  openclaw:
    emoji: "🔨"
    homepage: https://github.com/gaurangbhatt/craft
    os:
      - macos
      - linux
      - win32
    always: false
---

# Craft — Engineering Discipline for AI Agents

9 skills that turn AI agents into disciplined software engineers. Battle-tested on a 4-agent team shipping production software.

## Skills

| Skill | What It Enforces |
|-------|-----------------|
| `craftwork:test-driven-development` | No production code without a failing test first |
| `craftwork:systematic-debugging` | No fixes without root cause investigation |
| `craftwork:verification-before-completion` | No "done" claims without fresh evidence |
| `craftwork:brainstorming` | No code without exploring approaches first |
| `craftwork:writing-plans` | No implementation without exact file paths, code, and tests |
| `craftwork:subagent-driven-development` | One subagent per task, structured review between each |
| `craftwork:dispatching-parallel-agents` | Safe parallel execution for independent tasks |
| `craftwork:requesting-code-review` | Structured diff review with security and spec checklist |
| `craftwork:receiving-code-review` | Technical rigor over performative agreement |

## Install

```bash
clawhub install craftwork
```

## Philosophy

Agents are fast but sloppy. They skip tests, guess at fixes, claim "done" without checking, and agree with every review comment. These skills add guardrails — not to slow agents down, but to make their speed count.

Every skill follows the same pattern: **stop, verify, then act.**
