# Hiring AI Agents

When your AI agent hires other AI agents for specialized subtasks.

## When to Hire Agents vs Humans

| Task Type | Hire Agent | Hire Human |
|-----------|------------|------------|
| Data extraction at scale | ✅ | |
| Code generation | ✅ | Review |
| Image generation | ✅ | Direction |
| Physical presence required | | ✅ |
| Legal/regulated tasks | | ✅ |
| Judgment under uncertainty | Triage | ✅ Final |

## Model Tier Routing

Route subtasks to cheapest capable model:

| Task | Model Tier | Examples |
|------|------------|----------|
| Extraction, formatting | Haiku/GPT-4o-mini | Parse JSON, extract fields |
| Synthesis, analysis | Sonnet/GPT-4o | Summarize, compare, draft |
| Judgment, complex reasoning | Opus/o1 | Architecture decisions, edge cases |

## Agent Discovery

- **OpenRouter** — Single API, multiple models, automatic routing
- **LangChain Hub** — Pre-built chains and agents
- **Direct APIs** — OpenAI, Anthropic, Google, Mistral
- **Self-hosted** — Ollama, vLLM for privacy-sensitive work

## Integration Pattern

```
1. Define task schema (input/output types)
2. Select agent based on capability + cost
3. Format input to agent's expected schema
4. Execute with timeout and retry logic
5. Validate output against schema
6. Handle errors gracefully (fallback agent, human escalation)
7. Log everything for audit trail
```

## Cost Control

- **Set hard budget limits** per task, per day, per project
- **Alert before hitting limits** — don't just fail silently
- **Track cost per agent** — identify expensive inefficiencies
- **Cache repeated queries** — don't pay twice for same question
- **Batch when possible** — reduce API call overhead

## Quality Verification

- **Schema validation** — Does output match expected structure?
- **Fact-check sampling** — Spot-check claims against sources
- **Consistency checks** — Multiple agents should agree on facts
- **Human spot-checks** — Randomly escalate for QA

## Orchestration Patterns

**Sequential**: Agent A → Agent B → Agent C  
**Parallel**: Agent A, B, C simultaneously → merge results  
**Hierarchical**: Coordinator agent delegates to specialist agents  
**Competitive**: Multiple agents attempt same task, pick best result

## Audit Trail

For every agent interaction, log:
- Timestamp, agent ID, model version
- Input (or hash if sensitive)
- Output (or hash if sensitive)
- Latency, token count, cost
- Success/failure status
- Human reviewer (if applicable)
