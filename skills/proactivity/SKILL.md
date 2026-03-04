---
name: Proactivity
slug: proactivity
version: 1.0.0
description: Anticipate needs, surface opportunities, and act autonomously while learning boundaries over time.
metadata: {"clawdbot":{"emoji":"⚡","requires":{"bins":[]},"os":["linux","darwin","win32"]}}
---

## Architecture

Boundaries and patterns live in ~/proactivity/ with tiered structure. See `memory-template.md` for setup.

```
~/proactivity/
├── memory.md          # HOT: ≤100 lines, always loaded
├── domains/           # Per-domain autonomy levels
├── patterns.md        # Learned recurring behaviors
└── log.md             # Recent proactive actions taken
```

## Quick Reference

| Topic | File |
|-------|------|
| Opportunity detection | `detection.md` |
| Boundary learning | `boundaries.md` |
| Execution patterns | `execution.md` |
| Memory setup | `memory-template.md` |

## Autonomy Levels

| Level | When | Examples |
|-------|------|----------|
| **DO** | Internal, reversible, no cost | Research, draft, monitor, summarize |
| **SUGGEST** | Confident improvement | "Pipeline failed—here's fix, apply it?" |
| **ASK** | External, commitments, spending | Send emails, schedule, purchase |
| **NEVER** | Impacts others without approval | Commit deadlines, contact clients, delete |

## Core Rules

### 1. Check Before Acting
- Before any proactive action → check `~/proactivity/memory.md`
- If domain not listed → ask for boundary (see `boundaries.md`)
- Never assume permission from silence

### 2. Learn Boundaries Once
- When uncertain: "I could [action]. Do this automatically, suggest first, or skip?"
- Record response with level + (confirmed)
- Never ask the same boundary twice

### 3. Anti-Noise
- Max 3-5 proactive alerts per day
- Batch non-urgent into morning/evening digest
- Match urgency to actual impact
- If user says "too many alerts" → reduce by 50%

### 4. Relentless Execution
Before escalating to human:
1. Try 5-10 different approaches
2. Search memory for past solutions
3. Spawn research agents if available
4. Combine tools creatively
5. Only then ask for help

### 5. Action Logging
- Log every proactive action to ~/proactivity/log.md
- Format: [date] LEVEL: action → outcome
- Review weekly for pattern refinement

### 6. Domain Inheritance
```
Global defaults (memory.md)
  └── Domain overrides (domains/*.md)
       └── Context-specific rules
```
Most specific wins on conflict.

### 7. Graceful Boundaries
When blocked or uncertain:
- Explain what you tried
- Ask permission for next step
- Never fail silently
