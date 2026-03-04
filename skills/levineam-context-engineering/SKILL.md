---
name: context-engineering
description: >
  Comprehensive context engineering guidance for AI agent systems. Routes to
  specialized sub-skills for production agent work. Use when the user asks to:
  "optimize context", "reduce token costs", "context compression", "summarize
  conversation history", "design multi-agent system", "implement supervisor
  pattern", "create swarm architecture", "implement memory", "build memory
  system", "offload context to files", "use filesystem for agent memory",
  "debug agent failure", "diagnose context problems", "fix lost-in-middle",
  "build agent tools", "design agent tools", "evaluate agent performance",
  "build test framework", "implement LLM-as-judge", "understand context",
  "explain context windows", "build background agent", "implement BDI
  architecture", "start an LLM project", or any discussion of context
  degradation, attention patterns, multi-agent coordination, or production
  agent architecture.
version: "1.0.0"
---

# Context Engineering Skill

Routes to the appropriate sub-skill from Koylan's
[Agent-Skills-for-Context-Engineering](https://github.com/muratcankoylan/Agent-Skills-for-Context-Engineering)
collection, located at:

```
references/context-engineering-skills/skills/<sub-skill>/SKILL.md
```

## Setup

**No setup required.** This skill uses GitHub raw URLs as the primary method to fetch sub-skill documentation.

Sub-skill SKILL.md files are loaded directly from GitHub:

```
https://raw.githubusercontent.com/muratcankoylan/Agent-Skills-for-Context-Engineering/main/skills/<sub-skill>/SKILL.md
```

Example: For `context-optimization`, use:
```
https://raw.githubusercontent.com/muratcankoylan/Agent-Skills-for-Context-Engineering/main/skills/context-optimization/SKILL.md
```

**Optional Enhancement (Offline Use):**
For offline access or faster local reads, you can optionally initialize the git submodule:

```bash
git submodule update --init
```

This will populate the `references/context-engineering-skills/` directory locally. When the local directory exists, the skill loader will prefer local files over GitHub fetches.

## Sub-Skill Routing Table

Match the user's task to one sub-skill and **read its SKILL.md before
proceeding**. Load additional sub-skills only if the task spans multiple
domains.

| Task / trigger phrase | Sub-skill directory |
|---|---|
| "optimize context", reduce token costs, KV-cache, context budgeting | `context-optimization` |
| "context compression", summarize history, compaction, long sessions | `context-compression` |
| "design multi-agent", supervisor pattern, swarm architecture, agent handoffs | `multi-agent-patterns` |
| "implement memory", memory frameworks, Mem0, Zep, Letta, vector RAG | `memory-systems` |
| "offload context to files", filesystem memory, scratch pads, dynamic discovery | `filesystem-context` |
| "debug agent failure", lost-in-middle, context poisoning, degradation patterns | `context-degradation` |
| "build agent tools", tool descriptions, MCP tools, tool consolidation | `tool-design` |
| "evaluate agent", LLM-as-judge, test framework, quality gates | `evaluation` |
| Advanced evaluation: rubrics, pairwise comparison, position bias | `advanced-evaluation` |
| "understand context", context windows, attention mechanics, fundamentals | `context-fundamentals` |
| "build background agent", sandboxed execution, hosted coding agent | `hosted-agents` |
| "implement BDI", mental state modeling, belief-desire-intention | `bdi-mental-states` |
| "start an LLM project", batch pipeline, task-model fit, project structure | `project-development` |

## How to Load a Sub-Skill

1. Identify the best-matching row above.
2. Check if the local sub-skill SKILL.md exists:
   ```
   references/context-engineering-skills/skills/<sub-skill>/SKILL.md
   ```
   - **If the file exists locally:** Read it directly.
   - **If the file does NOT exist** (e.g., submodule not initialized): Fetch from GitHub:
     ```
     https://raw.githubusercontent.com/muratcankoylan/Agent-Skills-for-Context-Engineering/main/skills/<sub-skill>/SKILL.md
     ```
3. Follow the instructions in that file. Most sub-skills have a `references/`
   directory with detailed patterns — read those files only when the relevant
   pattern is needed (progressive disclosure).
4. If the user's task spans two sub-skills (e.g., memory + multi-agent), read
   both SKILL.md files before responding.

## Progressive Disclosure

Sub-skill SKILL.md files are compact routing documents. The deep content lives
in each sub-skill's `references/` folder. Load reference files only when the
specific topic is active — do not bulk-load all references upfront.

Example:
```
references/context-engineering-skills/skills/context-optimization/references/
```
Read individual reference files from that directory only when the matching
pattern is needed.
