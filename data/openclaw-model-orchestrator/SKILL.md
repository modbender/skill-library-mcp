---
name: openclaw-model-orchestrator
description: Multi-LLM orchestration for OpenClaw with fan-out, pipeline, and consensus patterns. Dispatches tasks across 40+ models using AAHP v3 inspired handoffs.
---

# OpenClaw Model Orchestrator

Dispatch tasks across multiple LLMs from chat. Uses AAHP v3 structured handoffs for minimal token overhead.

## Orchestration Modes

### Fan-Out
Split a task into parallel subtasks, each executed by a different model.
A planner model decomposes the task, workers execute in parallel, a reviewer merges results.

```
/orchestrate --mode fan-out --task "Build a REST API with auth" --planner copilot-opus --workers copilot52c,grokfast --reviewer copilot-sonnet46
```

### Pipeline
Chain models sequentially. Each model refines the previous model's output.
Ideal for plan -> implement -> review -> polish workflows.

```
/orchestrate --mode pipeline --task "Design and implement a caching layer" --planner copilot-opus --workers copilot52c,copilot-sonnet46 --reviewer copilot-opus
```

### Consensus
Send the same question to multiple models, then synthesize the best answer.
Identifies agreement, disagreement, and unique insights across models.

```
/orchestrate --mode consensus --task "What are the security risks of this API design?" --workers copilot-opus,gemini25,sonnet --reviewer copilot-opus
```

## Smart Recommendations

The orchestrator auto-classifies tasks and recommends optimal model combinations:

```
/orchestrate recommend "Build a REST API with JWT auth"
```

Returns: task classification, recommended planner/workers/reviewer, reasoning, and a ready-to-run command.

Use `help` as any flag value for context-aware recommendations:
```
/orchestrate --task "Audit security" --planner help
```

## Task Profiles

Pre-configured model combinations optimized for common task types:

| Profile | Planner | Workers | Reviewer | Use Case |
|---------|---------|---------|----------|----------|
| coding | copilot-opus | copilot52c, grokfast | copilot-sonnet46 | Feature development |
| research | gemini25 | gemini-flash, copilot-flash | copilot-opus | Analysis, investigation |
| security | copilot-opus | copilot-sonnet46, gemini25 | sonnet | Security audits |
| review | copilot-opus | copilot-sonnet46, copilot-sonnet | copilot-opus | Code/design review |
| bulk | haiku | copilot-flash, gemini25-flash, gpt5mini | haiku | Mass operations |

## AAHP v3 Integration

All model-to-model communication uses structured AAHP v3 handoff objects instead of raw chat history. This achieves up to 98% token reduction compared to naive context passing. Each handoff contains:

- Task context (only relevant information)
- Routing metadata (source/target model, mode)
- Differential state (only what changed)
- Constraints (output format, scope limits)

## Commands

| Command | Description |
|---------|-------------|
| `/orchestrate help` | Show help and available modes |
| `/orchestrate models` | List all available models with aliases |
| `/orchestrate recommend "task"` | Get model recommendations for a task |
| `/orchestrate --task "..." [flags]` | Execute orchestration |

## Configuration

In `openclaw.plugin.json`:

```json
{
  "config": {
    "defaultPlanner": "copilot-opus",
    "defaultReviewer": "copilot-sonnet46",
    "defaultWorkers": ["copilot52c", "grokfast", "copilot51"],
    "maxConcurrent": 4,
    "taskProfiles": { ... }
  }
}
```
