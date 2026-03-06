---
name: agora
version: 0.1.0-beta
description: "Multi-agent debate council — spawns 3 specialized sub-agents in parallel (Scholar, Engineer, Muse) to tackle complex problems from different angles. Configurable models per role. Inspired by Grok 4.20's multi-agent architecture."
tags: [multi-agent, council, parallel, reasoning, research, creative, collaboration, agora, debate]
---

# Agora 🏛️ — Multi-Agent Debate Council

Spawn 3 specialized sub-agents in parallel to tackle complex problems. You (the main agent) act as **Captain/Coordinator** — decompose the task, dispatch to specialists, synthesize the final answer.

## When to Use

Activate when the user says any of:
- `/agora <question>` or `/council <question>`
- "ask the council", "multi-agent", "get multiple perspectives"
- Or when facing complex, multi-faceted problems that benefit from diverse expertise

**DO NOT use for:** Simple questions, quick lookups, casual chat.

## Architecture

```
User Query
    │
    ▼
┌─────────────────────────────────┐
│  CAPTAIN (Main Agent Session)   │
│  Model: user's current model    │
│  Decomposes & Assigns           │
└────┬──────────┬─────────────────┘
     │          │          │
     ▼          ▼          ▼
┌─────────┐┌─────────┐┌─────────┐
│ SCHOLAR ││ENGINEER ││  MUSE   │
│ Research││ Logic   ││Creative │
│ & Facts ││ & Code  ││ & Style │
│ (model) ││ (model) ││ (model) │
└────┬────┘└────┬────┘└────┬────┘
     │          │          │
     ▼          ▼          ▼
┌─────────────────────────────────┐
│  CAPTAIN synthesizes            │
│  Final consensus answer         │
└─────────────────────────────────┘
```

## Model Configuration

Users can specify models per role. Parse from the command or use defaults.

### Syntax
```
/agora <question>
/agora <question> --scholar=codex --engineer=codex --muse=sonnet
/agora <question> --all=haiku
```

### Defaults (if no model specified)
| Role | Default Model | Why |
|------|--------------|-----|
| 🎖️ Captain | User's current session model | Coordinates & synthesizes |
| 🔍 Scholar | `codex` | Cheap, fast, good at web search |
| 🧮 Engineer | `codex` | Strong at logic & code |
| 🎨 Muse | `sonnet` | Creative, nuanced writing |

### Model Aliases (use in --flags)
- `opus` → Claude Opus 4.6
- `sonnet` → Claude Sonnet 4.5
- `haiku` → Claude Haiku 4.5
- `codex` → GPT-5.3 Codex
- `grok` → Grok 4.1
- `kimi` → Kimi K2.5
- `minimax` → MiniMax M2.5
- Or any full model string (e.g. `anthropic/claude-opus-4-6`)

### Presets
- **`--preset=cheap`** → all haiku (fast, minimal cost)
- **`--preset=balanced`** → scholar=codex, engineer=codex, muse=sonnet (default)
- **`--preset=premium`** → all opus (max quality, high cost)
- **`--preset=diverse`** → scholar=codex, engineer=sonnet, muse=opus (different perspectives)

## The Council

### 🔍 Scholar (Research & Facts)
- **Role:** Real-time web search, fact verification, evidence gathering, source citations
- **Must use:** `web_search` tool extensively (or web-search-plus skill if available)
- **Prompt prefix:** "You are SCHOLAR, a research specialist. Your job is to find accurate, up-to-date facts and evidence. Search the web extensively. Cite sources with URLs. Flag anything uncertain. Be thorough but concise. Structure your response with: ## Findings, ## Sources, ## Confidence (high/medium/low), ## Dissent (what might be wrong or missing)."

### 🧮 Engineer (Logic, Math & Code)
- **Role:** Rigorous reasoning, calculations, code, debugging, step-by-step verification
- **Prompt prefix:** "You are ENGINEER, a logic and code specialist. Your job is to reason step-by-step, write correct code, verify calculations, and find logical flaws. Be precise. Show your work. Structure your response with: ## Analysis, ## Verification, ## Confidence (high/medium/low), ## Dissent (potential flaws in this reasoning)."

### 🎨 Muse (Creative & Balance)
- **Role:** Divergent thinking, user-friendly explanations, creative solutions, balancing perspectives
- **Prompt prefix:** "You are MUSE, a creative specialist. Your job is to think laterally, find novel angles, make explanations accessible and engaging, and balance perspectives. Challenge assumptions. Be original. Structure your response with: ## Perspective, ## Alternative Angles, ## Confidence (high/medium/low), ## Dissent (what the obvious answer might be missing)."

## Execution Steps

### Step 1: Parse & Decompose
1. Parse model flags from the command (if any), otherwise use defaults
2. Read the user's query
3. Break it into sub-tasks suited for each agent
4. Create focused prompts for each role

### Step 2: Dispatch (PARALLEL)
Spawn all 3 sub-agents simultaneously using `sessions_spawn`:

```
sessions_spawn(task="[SCHOLAR prompt]", label="council-scholar", model="codex")
sessions_spawn(task="[ENGINEER prompt]", label="council-engineer", model="codex")
sessions_spawn(task="[MUSE prompt]", label="council-muse", model="sonnet")
```

**CRITICAL:** All 3 calls in the SAME function_calls block for true parallelism!

Each sub-agent task MUST:
1. Start with the role prefix and persona instructions
2. Include the full original user query
3. Specify what aspect to focus on
4. Request structured output with the sections defined above

### Step 3: Collect
Wait for all 3 sub-agents to complete. They auto-announce results back to this session.
Do NOT poll in a loop — just wait for the system messages.

### Step 4: Synthesize
As Captain, combine all 3 perspectives:

1. **Consensus:** Where do all agents agree? → High confidence
2. **Conflict:** Where do they disagree? → Investigate, pick strongest argument, explain why
3. **Gaps:** What did nobody cover? → Flag for user
4. **Cross-check:** Did Engineer's logic validate Scholar's facts? Did Muse find a creative angle nobody considered?
5. **Sources:** Collect all URLs/citations from Scholar

### Step 5: Deliver
Present the final answer in this format:

```
🏛️ **Council Answer**

[Synthesized answer here — this is YOUR synthesis as Captain, not a copy-paste of sub-agent outputs]

**Confidence:** High/Medium/Low
**Agreement:** [What all agents agreed on]
**Dissent:** [Where they disagreed and why you sided with X]

---
<sub>🔍 Scholar (model) · 🧮 Engineer (model) · 🎨 Muse (model) | Agora v1.1</sub>
```

## Examples

### Simple
```
/agora Should I use PostgreSQL or MongoDB for a new SaaS app?
```
→ Uses defaults: Scholar=codex, Engineer=codex, Muse=sonnet

### Custom models
```
/agora What's the best ETH L2 strategy right now? --scholar=sonnet --engineer=opus --muse=haiku
```

### All same model
```
/agora Explain quantum computing --all=opus
```

### Preset
```
/agora Debug this auth flow --preset=premium
```

## Tips

- For **pure research** questions: Scholar does heavy lifting, others verify
- For **coding** problems: Engineer leads, Muse reviews UX, Scholar checks docs
- For **strategy** questions: All three contribute equally
- For **writing** tasks: Muse leads, Scholar fact-checks, Engineer structures
- Use **`--preset=cheap`** for exploration, **`--preset=premium`** for important decisions

## Cost Note

Each council call spawns 3 sub-agents = 3x token usage. Use wisely for complex problems.
Default preset (balanced) uses Codex for 2/3 agents = cost-efficient.
