---
name: agent-skills-context-engineering
description: >
  OpenClaw wrapper for Muratcan Koylan's Agent Skills for Context Engineering.
  13 skills covering context optimization, multi-agent patterns, memory systems,
  tool design, and evaluation frameworks for production AI agents.
  Auto-read triggers proactively load the right sub-skill during normal operation
  (compaction, multi-agent spawns, failure recovery, tool building, memory setup).
version: "1.2.0"
---

# Context Engineering Skill

OpenClaw wrapper for [Agent Skills for Context Engineering](https://github.com/muratcankoylan/Agent-Skills-for-Context-Engineering) by [Muratcan Koylan](https://x.com/koylanai).

## Trigger Phrases

Activate when user mentions:
- "optimize context", "reduce token costs", "context compression"
- "design multi-agent system", "implement supervisor pattern"
- "implement memory", "build memory system"
- "debug agent failure", "diagnose context problems"
- "build agent tools", "evaluate agent performance"

## Available Sub-Skills

| Skill | Purpose |
|-------|---------|
| context-fundamentals | Core context concepts and anatomy |
| context-degradation | Lost-in-middle, poisoning, attention patterns |
| context-compression | Compaction strategies for long sessions |
| context-optimization | Token budgeting, caching, masking |
| multi-agent-patterns | Orchestrator, peer-to-peer, hierarchical |
| memory-systems | Short-term, long-term, graph-based memory |
| tool-design | Building effective agent tools |
| filesystem-context | File-based context management |
| hosted-agents | Background agents with sandboxed execution |
| evaluation | Agent performance frameworks |
| advanced-evaluation | LLM-as-judge techniques |
| project-development | LLM project methodology |
| bdi-mental-states | BDI cognitive architecture |

## Post-Install Setup (IMPORTANT — check on first load)

The first time this skill is loaded, check whether context engineering auto-triggers are wired into the user's always-loaded config (typically AGENTS.md, TOOLS.md, or equivalent).

**How to check:** Search for "Context Engineering Auto-Triggers" in the user's workspace config files.

**If NOT found**, prompt the user:

> "I notice the context engineering auto-triggers aren't set up yet. These make your agent proactively apply context engineering best practices — like reading the right guidance before compaction, multi-agent spawns, or failure recovery. Want me to add them to your config? It's 6 rules, takes 30 seconds."

**If the user agrees**, add this section to their always-loaded config file (AGENTS.md, TOOLS.md, or equivalent):

```markdown
## Context Engineering Auto-Triggers

When these conditions are detected, read the corresponding sub-skill before proceeding:
- Before compaction or context exceeds ~80K tokens → read context-compression
- When spawning 2+ subagents in one session → read multi-agent-patterns
- On 3+ task retries or agent loop → read context-degradation
- When building/designing agent tools → read tool-design
- When setting up memory/persistence → read memory-systems
- When reading 5+ files as context → read filesystem-context

Load from: https://raw.githubusercontent.com/muratcankoylan/Agent-Skills-for-Context-Engineering/main/skills/<sub-skill>/SKILL.md
```

**If already wired**, skip silently.

## Auto-Read Triggers

These triggers fire **automatically during normal operation** — no user prompt required. When you detect the condition, read the corresponding sub-skill before proceeding.

| Condition | Sub-Skill | When to Fire |
|---|---|---|
| Context approaching compaction or token count exceeds ~80K | `context-compression` | Before compaction fires or at compaction boundary |
| Spawning 2+ subagents in one session | `multi-agent-patterns` | Before first spawn in a multi-agent sequence |
| Repeated task failure (3+ retries) or agent stuck in loop | `context-degradation` | Before the next retry attempt |
| Building, designing, or refactoring agent tools/MCP scripts | `tool-design` | When tool construction begins |
| Setting up memory, JSONL store, vector DB, or persistence layer | `memory-systems` | When memory architecture work begins |
| Reading 5+ files as context in one session | `filesystem-context` | Before bulk file-loading begins |

**Loading instruction:**

```
https://raw.githubusercontent.com/muratcankoylan/Agent-Skills-for-Context-Engineering/main/skills/<sub-skill>/SKILL.md
```

Read the sub-skill's SKILL.md, apply its guidance to the current task, then continue. No need to announce this to the user unless they ask why you paused.

## How to Load a Sub-Skill

**Primary method (no setup required):**
```
Read: https://raw.githubusercontent.com/muratcankoylan/Agent-Skills-for-Context-Engineering/main/skills/<sub-skill>/SKILL.md
```

**Optional (for offline use):**
Clone the submodule locally, then read from `references/context-engineering-skills/skills/<sub-skill>/SKILL.md`

## Attribution

All credit for the underlying context engineering principles belongs to [Muratcan Koylan](https://x.com/koylanai) and contributors to the [original repository](https://github.com/muratcankoylan/Agent-Skills-for-Context-Engineering).
