---
name: Semantic Model Orchestrator
description: A powerful model routing skill that analyzes query intent and cost-efficiency to select the optimal LLM (Elite/Balanced/Basic) before execution.
version: 1.0.0
author: Ray
tags: [llm-ops, routing, efficiency, selection]
---

# Semantic Model Orchestrator

This skill provides an intelligent middle layer for AI agents to decide which model tier should handle a specific task. By using semantic analysis, it categorized queries into **Elite**, **Balanced**, or **Basic** levels.

## Features
- **Semantic Intent Recognition**: Uses vector embeddings to detect query complexity.
- **Cost-Efficiency Orchestration**: Routes queries to **Elite**, **Balanced**, or **Basic** models.
- **ClawHub Optimized**: Default tiers for Claude 3.5 Sonnet, GPT-4o-mini, and DeepSeek.
- **Rolling Adjustment**: Built-in logic to refine intent keywords from user history.
- **Multi-Provider Support**: Supports OpenAI, Anthropic, Gemini, and DeepSeek.

## Model Tiers
- **Elite**: `anthropic/claude-3-5-sonnet-latest`
- **Balanced**: `openai/gpt-4o-mini`
- **Basic**: `deepseek/deepseek-chat`

## Usage
Add this skill to your agent's capability list. The agent will call the `get_optimal_model` tool before making main LLM calls to optimize performance and budget.

### Example Tool Call
```python
result = router.analyze_and_route("Design a high-scalable microservices architecture for a fintech app.")
# Returns: {"tier": "ELITE", "suggested_model": "anthropic/claude-3-5-sonnet-latest"}
```
