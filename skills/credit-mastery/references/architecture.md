# Swarms API Architecture

## Three-Tier System

### Tier 1: Individual Agents
- Endpoint: `POST /v1/agent/completions`
- Single AI model per agent, focused tasks
- Use cases: content generation, data analysis, Q&A, tool execution
- Config: `agent_config` (AgentSpec) + `task` string
- Optional: `history` (conversation context), `img`/`imgs` (base64 images), `tools_enabled`

### Tier 2: Reasoning Agents (Pro+ only)
- Endpoint: `POST /v1/reasoning-agent/completions`
- 1-2 internal sub-agents for complex reasoning
- Types:
  - `reasoning-duo` — dual perspectives, synthesis
  - `self-consistency` — multiple paths, validation
  - `ire` — iterative refinement
  - `reasoning-agent` — general systematic reasoning
  - `consistency-agent` — contradiction detection
  - `ReflexionAgent` — self-reflection, bias detection
  - `GKPAgent` — cross-domain knowledge synthesis

### Tier 3: Multi-Agent Swarms
- Endpoint: `POST /v1/swarm/completions`
- 3 to 10,000+ agents
- Batch: `POST /v1/swarm/batch/completions` (Pro+ only)
- Config: `SwarmSpec` with `agents` array, `swarm_type`, `task`/`tasks`

## Health Check
```
GET https://api.swarms.world/health
```

## Conversation History
Include `history` parameter with previous messages:
```json
{
  "history": [
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "..."}
  ]
}
```

## Swarm-Specific Parameters
- `rearrange_flow` — for AgentRearrange type
- `rules` — governance constraints
- `messages` — for GroupChat types
- `stream` — real-time SSE output
- `heavy_swarm_loops_per_agent` — loops per agent in HeavySwarm
- `heavy_swarm_question_agent_model_name` — question agent model
- `heavy_swarm_worker_model_name` — worker model

## Choosing Architecture

**Sequential** when: ordered pipeline, each step depends on previous
**Concurrent** when: independent parallel tasks, speed matters
**MixtureOfAgents** when: need multiple specialist domains
**HierarchicalSwarm** when: complex org structure, delegation chains
**MajorityVoting** when: consensus/validation decisions
**GroupChat** when: collaborative brainstorming
**MultiAgentRouter** when: intelligent task routing at scale
**auto** when: unsure, let the system decide
