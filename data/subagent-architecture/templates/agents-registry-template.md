# Agent Registry

> **What this file is:** A human reference doc, not a config file. The spawning system does not read it.
> Copy this template to your workspace root as `AGENTS.md` when you're ready to track recurring agent configurations.

---

## How to use this file

When you spawn the same type of subagent repeatedly, document what worked here. Before your next spawn of that type, read this file to recall the personality, model, and task structure that produced good results.

**The workflow:**
1. Spawn an agent with whatever parameters seem right
2. If it works well, record the configuration below
3. Next time you need that agent type, read this file first, then construct your spawn call

---

## Example Entry Format

### AgentName — One-line description

**Purpose:** What tasks this agent handles well  
**Model:** sonnet / haiku / opus  
**Cost range:** $X.XX – $X.XX per spawn  
**Last used:** YYYY-MM-DD  

**Personality snippet:**
```
Precise, direct, no padding. [Domain] expert. Fix what's broken, document what you changed.
Skeptical of unverified claims. Calls out weak evidence. No sycophancy.
```

**Typical task structure:**
```
## TASK
[What you want the agent to do]

## CONTEXT
[Relevant background — include only what the agent needs]

## OUTPUT
[What format/deliverables you expect]
```

**Notes:**
- What this agent does well
- Known limitations or failure modes
- Cost patterns observed

---

## Your Agents

*(Add entries below as you develop recurring agent configurations)*

---

## When to split this file

Split into domain files (e.g., `AGENTS_WRITING.md`, `AGENTS_INFRA.md`) once you have more than ~10 agents and this file becomes hard to scan. The split is purely for your readability — it has zero effect on how spawning works.

**Suggested domain splits:**
- `AGENTS_WRITING.md` — content creation, editing, worldbuilding
- `AGENTS_INFRA.md` — coding, DevOps, system administration
- `AGENTS_RESEARCH.md` — research, analysis, fact-checking
- `AGENTS_PUBLISHING.md` — packaging, distribution, marketplace

Update your master `AGENTS.md` to contain a table of contents pointing to domain files when you make the split.
