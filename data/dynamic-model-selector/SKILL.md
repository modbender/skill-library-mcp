---
name: dynamic-model-selector
description: Dynamically select the best AI model for a task based on complexity, cost, and availability in GitHub Copilot. Use when deciding between free/paid models, or when you want automatic model routing based on query analysis.
---

# Dynamic Model Selector

## Overview

This skill analyzes user queries to recommend the optimal AI model from available GitHub Copilot options, balancing performance, cost, and task requirements.

## How to Use

1. Provide the user query or task description.
2. Run the classification script to analyze complexity.
3. Choose the suggested model or adjust based on preferences.

## Classification Criteria

- **Simple tasks** (short responses, basic chat): Use faster, free models like grok-code-fast-1.
- **Complex reasoning** (analysis, multi-step): Use advanced models like gpt-4o or claude-3.5-sonnet.
- **Code generation**: Prefer code-optimized models.
- **Cost sensitivity**: Favor free models when possible.

## Example Usage

For a query like "Explain quantum computing": Classify as medium complexity -> Recommend gpt-4o.

For "Write a Python function to sort a list": Classify as code task -> Recommend grok-code-fast-1.

## Resources

### scripts/
- `classify_task.py`: Analyzes the query and outputs model recommendation.

### references/
- `models.md`: Detailed list of available models, pros/cons, costs.