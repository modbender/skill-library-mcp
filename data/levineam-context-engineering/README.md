# context-engineering

> **Comprehensive context engineering guidance for AI agent systems.**

An OpenClaw skill that routes to 13 specialized sub-skills for production agent work — covering context optimization, memory systems, multi-agent coordination, evaluation, and more.

---

## Attribution

This skill is an OpenClaw wrapper for [Agent Skills for Context Engineering](https://github.com/muratcankoylan/Agent-Skills-for-Context-Engineering), created by [Muratcan Koylan](https://x.com/koylanai). All credit for the underlying context engineering principles, skills, and documentation belongs to Muratcan and the original contributors.

---

## What It Does

When you ask about context windows, token costs, memory systems, multi-agent design, or production LLM architecture, this skill routes your request to the most relevant specialized sub-skill and loads its guidance before responding.

Sub-skill documentation is fetched directly from GitHub — **no local setup required**.

---

## Trigger Phrases

- "optimize context", "reduce token costs", "KV-cache", "context budgeting"
- "context compression", "summarize history", "compaction", "long sessions"
- "design multi-agent system", "supervisor pattern", "swarm architecture", "agent handoffs"
- "implement memory", "memory frameworks", "Mem0", "Zep", "Letta", "vector RAG"
- "offload context to files", "filesystem memory", "scratch pads", "dynamic discovery"
- "debug agent failure", "lost-in-middle", "context poisoning", "context degradation"
- "build agent tools", "tool descriptions", "MCP tools", "tool consolidation"
- "evaluate agent", "LLM-as-judge", "test framework", "quality gates"
- "understand context", "context windows", "attention mechanics", "fundamentals"
- "build background agent", "sandboxed execution", "hosted coding agent"
- "implement BDI", "belief-desire-intention", "mental state modeling"
- "start an LLM project", "batch pipeline", "task-model fit"
- Any discussion of context degradation, attention patterns, multi-agent coordination, or production agent architecture

---

## 13 Sub-Skills

| Sub-skill | What it covers |
|---|---|
| `context-optimization` | Token budgeting, KV-cache, reduce costs |
| `context-compression` | Summarizing history, compaction for long sessions |
| `multi-agent-patterns` | Supervisor pattern, swarm architecture, agent handoffs |
| `memory-systems` | Memory frameworks, Mem0, Zep, Letta, vector RAG |
| `filesystem-context` | Filesystem memory, scratch pads, dynamic discovery |
| `context-degradation` | Lost-in-middle, context poisoning, debugging agent failures |
| `tool-design` | Tool descriptions, MCP tools, tool consolidation |
| `evaluation` | LLM-as-judge, test frameworks, quality gates |
| `advanced-evaluation` | Rubrics, pairwise comparison, position bias |
| `context-fundamentals` | Context windows, attention mechanics, core concepts |
| `hosted-agents` | Background agents, sandboxed execution, hosted coding agents |
| `bdi-mental-states` | Belief-desire-intention architecture, mental state modeling |
| `project-development` | Starting LLM projects, batch pipelines, task-model fit |

---

## Setup

**No local setup required.** Sub-skill documentation is loaded directly from GitHub raw URLs:

```
https://raw.githubusercontent.com/muratcankoylan/Agent-Skills-for-Context-Engineering/main/skills/<sub-skill>/SKILL.md
```

### Optional: Offline / Faster Local Access

If you want offline access or faster reads, initialize the git submodule (from your OpenClaw workspace root):

```bash
git submodule update --init
```

This populates `references/context-engineering-skills/` locally. When local files are present, the skill prefers them over GitHub fetches.

---

## How Sub-Skill Routing Works

1. Your request is matched to the closest row in the routing table.
2. The sub-skill's `SKILL.md` is loaded (local if available, GitHub otherwise).
3. Deep reference files within each sub-skill are loaded progressively — only the patterns relevant to your current task.
4. If your task spans two sub-skills (e.g., memory + multi-agent), both `SKILL.md` files are loaded before responding.

---

## License

MIT — same as the [source repository](https://github.com/muratcankoylan/Agent-Skills-for-Context-Engineering).
