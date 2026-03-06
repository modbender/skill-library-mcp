---
name: agent-router
description: Route prompts to the optimal AI model based on task type,
  complexity, and cost constraints.
---


# Agent Router

Route prompts to the optimal AI model based on task characteristics.

## What This Does

Analyzes a task/prompt and recommends the best model, considering task type, complexity, cost, speed, and context length.

## Model Routing Table

| Task Type | Complexity | Recommended | Fallback |
|-----------|-----------|-------------|----------|
| Coding (generation) | High | claude-opus / gpt-5 | claude-sonnet |
| Coding (simple edits) | Low | claude-sonnet / gpt-4.1 | claude-haiku |
| Creative writing | High | claude-opus | gpt-5 |
| Summarization | Low | claude-haiku / gpt-4.1-mini | gemini-flash |
| Data analysis | Medium | claude-sonnet | gpt-4.1 |
| Vision/Image | Any | claude-sonnet / gpt-4.1 | gemini-pro |
| Translation | Low | gpt-4.1-mini | claude-haiku |
| Long context (>100k) | Any | gemini-pro | claude-sonnet |
| Real-time/fast | Any | claude-haiku / gpt-4.1-mini | gemini-flash |
| Math/reasoning | High | claude-opus / o3 | deepseek-r1 |

## Instructions

1. **Analyze the task**: Classify by type, complexity (low/medium/high), and constraints (cost, speed, context length).
2. **Check user preferences**: Factor in model preferences, cost limits, or subscription tiers.
3. **Route decision**: Using the table above, recommend primary + fallback model.
4. **For Codex CLI routing** (local dev):
   - Heavy coding → `codex exec` (GPT-5.3-Codex, free via subscription)
   - Quick questions → current model
   - Cost-sensitive batch work → claude-haiku or gpt-4.1-mini
5. **Output format**:
   ```
   🔀 Route: <task_type> | Complexity: <level>
   ✅ Recommended: <model>
   🔄 Fallback: <model>
   💰 Est. cost: <low/medium/high>
   💡 Reason: <why>
   ```
6. **Batch routing**: For multiple tasks, create a routing plan table showing which model handles each task.

## Edge Cases

- **Ambiguous tasks**: Default to claude-sonnet as the best general-purpose choice
- **Multi-modal tasks** (text + image): Ensure the chosen model supports vision
- **Context overflow**: If input exceeds model's context window, suggest chunking or switching to a larger-context model
- **Rate limits**: If primary model is rate-limited, auto-route to fallback

## Requirements

- No API keys or dependencies — this is a decision framework, not an API
- Update routing table as model pricing/capabilities change
