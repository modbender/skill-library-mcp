---
name: swarms-ai
description: Build and orchestrate multi-agent AI systems using the Swarms API. Use when creating single agents, multi-agent swarms (sequential, concurrent, hierarchical, mixture-of-agents, majority voting, graph workflows), launching agent tokens on Solana, integrating ATP payment protocol, publishing to Swarms Marketplace, using sub-agent delegation, streaming responses, or building any multi-agent orchestration pipeline. Covers Python, TypeScript, and cURL.
---

# Swarms AI — Multi-Agent Orchestration

Build production-grade multi-agent systems using the Swarms API platform. Supports single agents, reasoning agents, and swarms of 3–10,000+ agents with 20+ architecture patterns.

## Quick Reference

- **Base URL:** `https://api.swarms.world`
- **Auth:** `x-api-key` header with API key from [swarms.world/platform/api-keys](https://swarms.world/platform/api-keys)
- **Docs index:** `https://docs.swarms.ai/llms.txt`
- **Python SDK:** `pip install swarms-client`
- **Marketplace:** [swarms.world](https://swarms.world)

## Architecture Tiers

| Tier | Name | Agents | Endpoint |
|------|------|--------|----------|
| 1 | Individual Agent | 1 | `/v1/agent/completions` |
| 2 | Reasoning Agent | 1-2 internal | `/v1/reasoning-agent/completions` |
| 3 | Multi-Agent Swarm | 3–10,000+ | `/v1/swarm/completions` |

## Workflow

### 1. Single Agent

```python
import requests

payload = {
    "agent_config": {
        "agent_name": "MyAgent",
        "description": "Purpose of the agent",
        "system_prompt": "You are...",
        "model_name": "gpt-4o",  # or claude-sonnet-4-20250514, etc.
        "role": "worker",
        "max_loops": 1,
        "max_tokens": 8192,
        "temperature": 0.5,
        "auto_generate_prompt": False,
        "tools_list_dictionary": None
    },
    "task": "Your task here"
}

response = requests.post(
    "https://api.swarms.world/v1/agent/completions",
    headers={"x-api-key": API_KEY, "Content-Type": "application/json"},
    json=payload
)
```

### 2. Multi-Agent Swarm

```python
payload = {
    "name": "My Swarm",
    "description": "What this swarm does",
    "agents": [
        {
            "agent_name": "Agent1",
            "description": "Role 1",
            "system_prompt": "You are...",
            "model_name": "gpt-4o",
            "role": "worker",
            "max_loops": 1,
            "max_tokens": 8192,
            "temperature": 0.5
        },
        {
            "agent_name": "Agent2",
            "description": "Role 2",
            "system_prompt": "You are...",
            "model_name": "claude-sonnet-4-20250514",
            "role": "worker",
            "max_loops": 1,
            "max_tokens": 8192,
            "temperature": 0.5
        }
    ],
    "max_loops": 1,
    "swarm_type": "SequentialWorkflow",  # See architecture table
    "task": "Your task here"
}

response = requests.post(
    "https://api.swarms.world/v1/swarm/completions",
    headers={"x-api-key": API_KEY, "Content-Type": "application/json"},
    json=payload
)
```

### 3. Token Launch (Solana)

```python
payload = {
    "name": "My Agent Token",
    "description": "Agent description",
    "ticker": "MAG",
    "private_key": "[1,2,3,...]"  # Solana wallet private key
}

response = requests.post(
    "https://swarms.world/api/token/launch",
    headers={"Authorization": "Bearer API_KEY", "Content-Type": "application/json"},
    json=payload
)
# Returns: token_address, pool_address, listing_url
# Cost: ~0.04 SOL
```

## Available Swarm Architectures

Use the `swarm_type` parameter:

| Type | Description | Best For |
|------|-------------|----------|
| `SequentialWorkflow` | Linear pipeline, each agent builds on previous | Step-by-step processing |
| `ConcurrentWorkflow` | Parallel execution | Independent tasks, speed |
| `AgentRearrange` | Dynamic agent reordering | Adaptive workflows |
| `MixtureOfAgents` | Specialist agent selection | Multi-domain tasks |
| `MultiAgentRouter` | Intelligent task routing | Large-scale distribution |
| `HierarchicalSwarm` | Nested hierarchies with delegation | Complex org structures |
| `MajorityVoting` | Consensus across agents | Decision making |
| `BatchedGridWorkflow` | Grid pattern execution | Multi-task × multi-agent |
| `GraphWorkflow` | Directed graph of agent nodes | Complex dependencies |
| `GroupChat` | Agent discussion | Collaborative brainstorming |
| `InteractiveGroupChat` | Real-time agent interaction | Dynamic collaboration |
| `AutoSwarmBuilder` | Auto-generate optimal swarm | When unsure of architecture |
| `HeavySwarm` | High-capacity processing | Large workloads |
| `DebateWithJudge` | Structured debate | Adversarial evaluation |
| `RoundRobin` | Round-robin distribution | Even load distribution |
| `MALT` | Multi-agent learning | Training systems |
| `CouncilAsAJudge` | Expert panel evaluation | Quality assessment |
| `LLMCouncil` | LM council for decisions | Group decision making |
| `AdvancedResearch` | Research workflows | Deep research |
| `auto` | Auto-select best type | Default/unknown |

## Agent Config Parameters

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `agent_name` | string | — | Unique agent identifier |
| `description` | string | — | Agent purpose |
| `system_prompt` | string | — | Behavior instructions |
| `model_name` | string | `gpt-4.1` | AI model (gpt-4o, claude-sonnet-4-20250514, etc.) |
| `role` | string | `worker` | Agent role in swarm |
| `max_loops` | int/string | `1` | Iterations (`"auto"` for autonomous) |
| `max_tokens` | int | `8192` | Max response length |
| `temperature` | float | `0.5` | Creativity (0.0–2.0) |
| `auto_generate_prompt` | bool | `false` | Auto-enhance system prompt |
| `tools_list_dictionary` | list | — | OpenAPI-style tool definitions |
| `streaming_on` | bool | `false` | Enable SSE streaming |
| `mcp_url` | string | — | MCP server URL |
| `selected_tools` | list | all safe | Restrict available tools |

## Rules

- Always use environment variables for API keys — never hardcode.
- Set appropriate `max_loops` — use `"auto"` only when sub-agent delegation is needed.
- Match `swarm_type` to use case (see architecture table).
- For streaming, set `streaming_on: true` and parse SSE events (metadata → chunks → usage → done).
- Token launches cost ~0.04 SOL from the provided wallet.
- Batch endpoint (`/v1/swarm/batch/completions`) requires Pro/Ultra/Premium tier.
- Reasoning agents (`/v1/reasoning-agent/completions`) require Pro+ tier.

## Resource Map

| Topic | Reference |
|-------|-----------|
| Full API architecture & tiers | `references/architecture.md` |
| Sub-agent delegation patterns | `references/sub-agents.md` |
| ATP payment protocol (Solana) | `references/atp-protocol.md` |
| Marketplace publishing | `references/marketplace.md` |
| Streaming implementation | `references/streaming.md` |
| Tools integration | `references/tools.md` |
| All docs pages | https://docs.swarms.ai/llms.txt |

Read references only when the task requires that specific depth.
