---
name: council-of-wisdom
description: A multi-agent deliberation hub with 3 core agents and extensible extended agents. Can call user workspace skills when needed.
version: 1.3.0
tags: [agents, routing, multi-agent, council, wisdom, orchestration, decision-making, hub]
---

# Council of Wisdom

A multi-agent deliberation hub with 3 core agents and extensible extended agents.

## When to Activate

### Auto-Trigger
- Decision words: should I, should we, better to, which option
- Risk signals: dangerous, risk, worried, concerned, scared
- Complex words: analyze, compare, think, help me
- Explicit: council:, ask the council

### Auto-Skip
```
hello, hi, hey, thanks, thank you
what time, weather, temperature
yes, no, ok, sure
define, what is
```

## Architecture

```
Query → Check Skip List
           │
           ▼ (if not skipped)
    ┌──────────────────┐
    │  CORE AGENTS    │ (always run)
    │ - Intent Decoder│
    │ - Risk Checker  │
    │ - Tone Designer │
    └──────────────────┘
           │
           ▼ (if extended triggered)
    ┌──────────────────┐
    │ EXTENDED AGENTS │ (included)
    └──────────────────┘
           │
           ▼
    ┌──────────────────┐
    │ WORKSPACE SKILLS │ (if needed)
    └──────────────────┘
           │
           ▼
    Enriched Response
```

## Core Agents (Always Run)

### Intent Decoder
What does the user actually want?

### Risk Checker
What could go wrong?

### Tone Designer
How should this feel?

## Extended Agents (Included)

| Agent | Trigger Keywords |
|-------|-----------------|
| System Designer | api, database, architecture, system |
| Complexity Assessor | complex, analyze, compare |
| Values Guardian | ethical, moral, values, fair |

## Calling Workspace Skills

The council can call skills from your workspace when specialized knowledge is needed.

**Example:**
- Query about Quran → call quran-search-engine-mcp
- Query about GitHub → call github-mcp
- Query about security → call penetration-tester agent

**To add workspace skills:**
1. Skills go in `workspace/skills/`
2. Agents go in `workspace/agents/`
3. The council detects keywords and calls them when needed

## Adding Custom Extended Agents

Create a new `.md` file in `agents/` folder:

```markdown
# Your Agent Name

Trigger: keyword1, keyword2

Your analysis...
```

## Output

### Implicit Mode (Default)
Skill runs silently. Apply analysis to shape response.

### Explicit Mode (When Asked)
Use `council:` prefix to see full analysis.

## Simple Rules (80% of Value)

```
IF query contains: dangerous, risk, worried, scared
THEN: Risk Checker flag = high

IF query contains: frustrated, angry, upset
THEN: Tone = empathetic
```

## SEO

**Keywords:** multi-agent, AI router, agent council, decision support, AI deliberation, extensible hub, workspace skills

**Use cases:** personal AI assistant, decision making, risk assessment
