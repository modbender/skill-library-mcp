# Agent Architecture Patterns

## Core Patterns

### ReAct (Reasoning + Acting)
```
Thought: I need to find the weather in Madrid
Action: weather_api(location="Madrid")
Observation: 22°C, sunny
Thought: Now I can answer the user
Answer: It's 22°C and sunny in Madrid
```
**Best for:** General-purpose agents, research tasks, debugging visibility

### Plan-and-Execute
```
1. Create plan: [Step1, Step2, Step3]
2. Execute each step
3. Replan if needed
```
**Best for:** Complex multi-step tasks, coding projects, long-running workflows

### Tool-Use Agent
- LLM decides which tool to call each turn
- Simpler than ReAct, no explicit reasoning trace
- Works well for bounded, well-defined tasks

### Multi-Agent Orchestration
```
Orchestrator Agent
    ├── Research Agent
    ├── Writing Agent  
    └── Review Agent
```
**Best for:** Tasks requiring specialized expertise, parallel execution, role separation

## Memory Architecture

| Type | Scope | What to Store | Implementation |
|------|-------|---------------|----------------|
| **Working** | Current task | Conversation, tool results | Context window |
| **Episodic** | Per session | What happened, decisions made | Session log, summarization |
| **Semantic** | Long-term | Facts, learnings, preferences | Vector DB, embeddings |
| **Procedural** | Permanent | How to do things | Prompts, skills, code |

### Memory Strategy by Use Case

| Use Case | Working | Episodic | Semantic | Procedural |
|----------|---------|----------|----------|------------|
| Customer support | Full conversation | Last 5 interactions | FAQ, product catalog | Response templates |
| Coding assistant | Current file + errors | Project context | Codebase embeddings | Language patterns |
| Personal assistant | Today's tasks | User history | Preferences, contacts | Workflows, automations |

## Single vs Multi-Agent Decision

### Use Single Agent When:
- Task has clear linear flow
- Same context needed throughout
- No genuine role separation
- Latency matters (multi-agent adds overhead)

### Use Multi-Agent When:
- Distinct expertise needed (researcher vs writer vs reviewer)
- Different tool access per role (analyst reads, executor writes)
- Parallel execution beneficial
- Clear handoff points exist

### Multi-Agent Patterns

**Sequential Pipeline:**
```
Input → Agent A → Agent B → Agent C → Output
```

**Hierarchical:**
```
Manager Agent
  ├── delegates to Worker A
  ├── delegates to Worker B
  └── aggregates results
```

**Debate/Consensus:**
```
Agent A proposes → Agent B critiques → Agent A revises → Output
```

## Context Window Strategy

| Context Type | Priority | Max Tokens | Refresh |
|--------------|----------|------------|---------|
| System prompt | Highest | 2000 | Deploy |
| User profile | High | 500 | Session start |
| Recent messages | High | 4000 | Every turn |
| Retrieved docs (RAG) | Medium | 2000 | On-demand |
| Tool results | Medium | Variable | Per-call |
| Long-term memory | Low | 1000 | Summarized |

### Context Management Rules

1. **System prompt is sacred** — Never let user content modify it
2. **Summarize aggressively** — Old context → compressed summary
3. **Retrieve on-demand** — Don't preload everything, fetch what's needed
4. **Drop stale context** — Tool results from 10 turns ago rarely matter
