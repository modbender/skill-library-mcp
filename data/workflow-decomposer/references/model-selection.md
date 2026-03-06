# Model Selection Guide

## Reasoning Models (Priority Order)

### Tier 1: Strong Reasoning (Latest + Alibaba Preferred)

| Model | Provider | Strengths | Best For |
|-------|----------|-----------|----------|
| `bailian/qwen3.5-plus` | Alibaba | Strong reasoning, latest Qwen | Complex analysis, task decomposition |
| `bailian/qwen3-plus` | Alibaba | Strong reasoning | Multi-step reasoning |
| `bailian/qwen-max` | Alibaba | Maximum capability | Hardest problems |

### Tier 2: Strong Reasoning (Other Providers)

| Model | Provider | Strengths | Best For |
|-------|----------|-----------|----------|
| `claude-sonnet-4-20250514` | Anthropic | Balanced reasoning | General complex tasks |
| `gpt-4o` | OpenAI | Strong all-rounder | Mixed workloads |

## Task-Type Model Selection

### Coding Tasks
- **New features/apps** → Coding-specialized models
- **Debugging** → Strong reasoning + code understanding
- **Refactoring** → Models with large context windows
- **Code review** → Models with strong analysis

### Research Tasks
- **Web search needed** → Models with web access
- **Document analysis** → Models with large context
- **Fact checking** → Fast models with web access

### Creative Tasks
- **Writing** → Models with strong generation
- **Brainstorming** → Creative models
- **Design** → Models with visual understanding (if available)

### Simple Tasks
- **Lookups** → Fast, lightweight models
- **Calculations** → Any model
- **Formatting** → Fast models

## Selection Algorithm

```
1. Is reasoning required?
   YES → Use Tier 1 (prefer latest Alibaba)
   NO → Continue

2. Is coding required?
   YES → Use coding-specialized model
   NO → Continue

3. Is web access required?
   YES → Use model with web_fetch capability
   NO → Continue

4. Is it a simple task?
   YES → Use fastest available model
   NO → Use default reasoning model
```

## Current Environment Models

Check runtime info for available models:
- `model` - Currently active model
- `default_model` - Default model for sessions

Current defaults (from runtime):
- Active: `bailian/qwen3.5-plus`
- Default: `bailian/qwen3.5-plus`
