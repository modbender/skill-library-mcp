---
name: geepers-orchestrate
description: Run multi-agent Dream Cascade (hierarchical 3-tier synthesis) or Dream Swarm (parallel multi-domain search) workflows via the dr.eamer.dev orchestration API. Use when a task benefits from multiple specialized agents working in parallel or hierarchically.
---

# Dreamer Orchestrate

Run multi-agent workflows through `https://api.dr.eamer.dev`.

## Authentication

```bash
export DREAMER_API_KEY=your_key_here
```

## Endpoints

### Dream Swarm — Parallel Search
```
POST https://api.dr.eamer.dev/v1/orchestrate/swarm
Body:
{
  "query": "What are the most effective treatments for Type 2 diabetes?",
  "sources": ["pubmed", "semantic_scholar", "wikipedia"],
  "num_agents": 5
}
```
Runs multiple agents simultaneously across data sources and synthesizes results.

### Dream Cascade — Hierarchical Synthesis
```
POST https://api.dr.eamer.dev/v1/orchestrate/cascade
Body:
{
  "task": "Analyze the current state of quantum computing hardware",
  "num_agents": 8,
  "provider": "anthropic"
}
```
Three-tier workflow: Belter agents gather raw data → Drummer agents synthesize domains → Camina produces executive summary.

## Response Format

Both endpoints return:
```json
{
  "result": "Synthesized answer...",
  "sources": [...],
  "agent_count": 5,
  "duration_ms": 12450
}
```

## When to Use
- Complex research questions requiring multiple perspectives
- Cross-domain synthesis that would take multiple sequential queries
- Long-horizon analysis where parallelism saves time

## Don't Use When
- Simple single-source queries (use dreamer-data instead)
- You need fine-grained control over individual agent behavior
- Latency is critical (orchestration takes 10-60 seconds)
