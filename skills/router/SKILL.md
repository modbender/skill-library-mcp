---
name: switchboard
description: >
  Cost-optimize AI agent operations by routing tasks to appropriate models based on complexity.
  Use this skill when: (1) deciding which model to use for a task, (2) spawning sub-agents,
  (3) considering cost efficiency, (4) the current model feels like overkill for the task.
  Triggers: "model routing", "cost optimization", "which model", "too expensive", "spawn agent",
  "cheap model", "expensive", "tier 1", "tier 2", "tier 3".
---

# SwitchBoard

Route tasks to the cheapest model that can handle them. Most agent work is routine.

## Prerequisites

This skill requires an [OpenRouter](https://openrouter.ai/) API key for model routing. Add it to your OpenClaw user config:

```jsonc
// ~/.openclaw/openclaw.json
{
  "openrouter_api_key": "sk-or-v1-..."
}
```

Without this key, `/model` switching and `sessions_spawn` with non-default models will fail. Get a key at [openrouter.ai/keys](https://openrouter.ai/keys).

> **Privacy Note:** Some models listed in this skill (e.g., Aurora Alpha, Free Router) may log prompts and completions for provider training. **Do not route sensitive data** (API keys, passwords, private PII) through free or unmoderated models. Review model privacy policies at [openrouter.ai/docs](https://openrouter.ai/docs) before use.

## Core Principle

80% of agent tasks are janitorial. File reads, status checks, formatting, simple Q&A. These don't need expensive models. Reserve premium models for problems that actually require deep reasoning.

## Model Tiers

For OpenRouter-specific pricing and models, see [references/openrouter-models.md](references/openrouter-models.md).

### Tier 0: Free

| Model | Context | Tools | Best For |
|-------|---------|-------|----------|
| Aurora Alpha | 128K | ✅ | Zero-cost reasoning, cloaked community model |
| Free Router | 200K | ✅ | Auto-routes to best available free model |
| Step 3.5 Flash (free) | 256K | ✅ | Long-context reasoning at zero cost |

*Free models have rate limits and variable availability. Good for non-critical background tasks.*

### Tier 1: Cheap ($0.02-0.50/M tokens)

| Model | Input | Output | Context | Tools | Best For |
|-------|-------|--------|---------|-------|----------|
| Qwen3 Coder Next | $0.07 | $0.30 | 262K | ✅ | Agentic coding, MoE 80B/3B active |
| Gemini 2.0 Flash Lite | $0.07 | $0.30 | 1M | ✅ | High volume, massive context |
| Gemini 2.0 Flash | $0.10 | $0.40 | 1M | ✅ | General routine with long context |
| GPT-4o-mini | $0.15 | $0.60 | 128K | ✅ | Quick responses, reliable tool use |
| DeepSeek Chat | $0.30 | $1.20 | 164K | ✅ | General routine work |
| Claude 3 Haiku | $0.25 | $1.25 | 200K | ✅ | Fast tool use, structured output |
| Kimi K2.5 | $0.45 | $2.20 | 262K | ✅ | Multimodal, visual coding, agentic |

### Tier 2: Mid ($1-5/M tokens)

| Model | Input | Output | Context | Tools | Best For |
|-------|-------|--------|---------|-------|----------|
| o3-mini | $1.10 | $4.40 | 200K | ✅ | Reasoning on a budget |
| Gemini 2.5 Pro | $1.25 | $10.00 | 1M | ✅ | Long context, large codebase work |
| GPT-4o | $2.50 | $10.00 | 128K | ✅ | Multimodal tasks |
| Claude Sonnet | $3.00 | $15.00 | 1M | ✅ | Balanced performance, agentic |

### Tier 3: Premium ($5+/M tokens)

| Model | Input | Output | Context | Tools | Best For |
|-------|-------|--------|---------|-------|----------|
| Claude Opus 4.6 | $5.00 | $25.00 | 1M | ✅ | Complex reasoning, deep context |
| o1 | $15.00 | $60.00 | 200K | ✅ | Multi-step reasoning |
| GPT-4.5 | $75.00 | $150.00 | 128K | ✅ | Frontier tasks |

*Prices as of Feb 2026. Check provider docs for current rates. Context = max context window. Tools = function calling support.*

## Task Classification

Before executing any task, classify it:

### ROUTINE → Use Tier 1

**Characteristics:**
- Single-step operations
- Clear, unambiguous instructions
- No judgment required
- Deterministic output expected

**Examples:**
- File read/write operations
- Status checks and health monitoring
- Simple lookups (time, weather, definitions)
- Formatting and restructuring text
- List operations (filter, sort, transform)
- API calls with known parameters
- Heartbeat and cron tasks
- URL fetching and basic parsing

### MODERATE → Use Tier 2

**Characteristics:**
- Multi-step but well-defined
- Some synthesis required
- Standard patterns apply
- Quality matters but isn't critical

**Examples:**
- Code generation (standard patterns)
- Summarization and synthesis
- Draft writing (emails, docs, messages)
- Data analysis and transformation
- Multi-file operations
- Tool orchestration
- Code review (non-security)
- Search and research tasks

### COMPLEX → Use Tier 3

**Characteristics:**
- Novel problem solving required
- Multiple valid approaches
- Nuanced judgment calls
- High stakes or irreversible
- Previous attempts failed

**Examples:**
- Multi-step debugging
- Architecture and design decisions
- Security-sensitive code review
- Tasks where cheaper model already failed
- Ambiguous requirements needing interpretation
- Long-context reasoning (>50K tokens)
- Creative work requiring originality
- Adversarial or edge-case handling

## Decision Algorithm

```
function selectModel(task):
  # Rule 1: Escalation override
  if task.previousAttemptFailed:
    return nextTierUp(task.previousModel)

  # Rule 2: Hard constraints (filter before cost)
  candidates = ALL_MODELS
  if task.requiresToolUse:
    candidates = candidates.filter(m => m.supportsTools)
  if task.estimatedTokens > 128_000:
    candidates = candidates.filter(m => m.contextWindow >= task.estimatedTokens)
  if task.requiresMultimodal:
    candidates = candidates.filter(m => m.supportsImages)

  # Rule 3: Latency constraint
  if task.isRealTime or task.inAgentLoop:
    candidates = candidates.filter(m => m.latencyTier <= "fast")

  # Rule 4: Complexity classification
  if task.hasSignal("debug", "architect", "design", "security"):
    return cheapestIn(candidates, TIER_3)
  if task.hasSignal("summarize", "analyze", "refactor"):
    return cheapestIn(candidates, TIER_2)

  complexity = classifyTask(task)
  if complexity == ROUTINE:
    return cheapestIn(candidates, TIER_1)
  elif complexity == MODERATE:
    return cheapestIn(candidates, TIER_2)
  else:
    return cheapestIn(candidates, TIER_3)
```

> **Note:** "write", "read", "code" alone are poor routing signals — `"write a file"` is Tier 1: work, not Tier 2. Classify based on the *task structure*, not individual keywords.

## Latency Considerations

Cost isn't the only axis. For real-time agent loops, latency matters:

| Tier | Typical TTFT | Throughput | Use When |
|------|-------------|------------|----------|
| Free | 1-5s | Variable | Background tasks, not time-sensitive |
| Tier 1 | 200-800ms | 50-100 tok/s | Agent loops, real-time pipelines |
| Tier 2 | 500ms-2s | 30-80 tok/s | Interactive sessions, async work |
| Tier 3 | 1-10s | 10-40 tok/s | One-shot complex tasks, async only |

*TTFT = Time To First Token. Reasoning models (o1, o3-mini) have high TTFT due to thinking time but are worth it for hard problems.*

**Rule of thumb:** If the agent is waiting in a loop for a response before the next action, use Tier 1. If the task is fire-and-forget, cost matters more than speed.

## Behavioral Rules

### For Main Session

1. Default to Tier 2 for interactive work
2. Suggest downgrade when doing routine work: "This is routine - I can handle this on a cheaper model or spawn a sub-agent."
3. Request upgrade when stuck: "This needs more reasoning power. Switching to [premium model]."

### For Sub-Agents

1. Default to Tier 1 unless task is clearly moderate+
2. Batch similar tasks to amortize overhead
3. Report failures back to parent for escalation
4. Check context window limits before dispatching — don't send 200K tokens to a 32K model

### For Automated Tasks

1. Heartbeats/monitoring → Always Tier 1 (or Free if available)
2. Scheduled reports → Tier 1 or 2 based on complexity
3. Alert responses → Start Tier 2, escalate if needed
4. Background data fetching → Free tier when non-critical

## Communication Patterns

When suggesting model changes, use clear language:

**Downgrade suggestion:**
> "This looks like routine file work. Want me to spawn a sub-agent on DeepSeek for this? Same result, fraction of the cost."

**Upgrade request:**
> "I'm hitting the limits of what I can figure out here. This needs Opus-level reasoning. Switching up."

**Explaining hierarchy:**
> "I'm running the heavy analysis on Sonnet while sub-agents fetch the data on DeepSeek. Keeps costs down without sacrificing quality where it matters."

## Cost Impact

Assuming 100K tokens/day average usage:

| Strategy | Monthly Cost | Notes |
|----------|--------------|-------|
| Pure Opus 4.6 | ~$75 | Maximum capability, lower than old Opus |
| Pure Sonnet | ~$45 | Good default for most work |
| Pure DeepSeek | ~$9 | Cheap but limited on hard problems |
| Pure Qwen3 Coder | ~$2 | Cheapest viable for coding agents |
| Hierarchy (80/15/5) | ~$12 | Best of all worlds |
| With Free tier (85/10/4/1) | ~$8 | Aggressive optimization |

The 80/15/5 split:
- 80% routine tasks on Tier 1 (~$4)
- 15% moderate tasks on Tier 2 (~$5)
- 5% complex tasks on Tier 3 (~$3)

Result: 6-10x cost reduction vs pure premium, with equivalent quality on complex tasks.

## OpenClaw Integration

### Session Model Switching

```yaml
# config.yml - set your default session model
model: anthropic/claude-sonnet-4

# Mid-session, switch down for routine work
/model deepseek/deepseek-chat

# Switch up when you hit a wall
/model anthropic/claude-opus-4
```

### Spawning Sub-Agents

```yaml
# Batch routine tasks on cheap models
sessions_spawn:
  task: "Fetch and parse these 50 URLs"
  model: deepseek/deepseek-chat

# Use Qwen3 Coder for file-heavy agent work
sessions_spawn:
  task: "Refactor these test files to use the new helper"
  model: qwen/qwen3-coder-next

# Free tier for non-critical background jobs
sessions_spawn:
  task: "Check health of all endpoints and log status"
  model: openrouter/free
```

### Recommended OpenClaw Defaults

| Task Type | Model | Why |
|-----------|-------|-----|
| Main interactive session | `claude-sonnet-4` | Best balance of quality and cost |
| File ops, fetches, formatting | `deepseek/deepseek-chat` | Cheap, reliable |
| Agentic coding sub-tasks | `qwen/qwen3-coder-next` | $0.07/M, 262K context, tool use |
| Background monitoring | `openrouter/free` | Zero cost |
| Stuck / complex debugging | `anthropic/claude-opus-4` | Escalate only when needed |

## Anti-Patterns

**DON'T:**
- Leave your session on Opus when the task is clearly routine — `/model deepseek` exists for a reason
- Spawn sub-agents without specifying a model — they inherit the session model, which is usually Tier 2
- Use Tier 3 for `sessions_spawn` tasks like file parsing, URL fetching, or status checks
- Forget context window limits — spawning a 200K-token task on a 32K model will silently truncate
- Run recurring or scheduled tasks on anything above Tier 1

**DO:**
- Set `model: anthropic/claude-sonnet-4` as your `config.yml` default — good baseline
- Always set an explicit `model` field in `sessions_spawn` — default to `deepseek/deepseek-chat` or `qwen/qwen3-coder-next`
- `/model` switch down the moment you realize the current task is janitorial
- `/model` switch up the moment you're stuck — don't waste tokens retrying on a weak model
- Use `openrouter/free` for fire-and-forget background checks

## Extending This Skill

Optimize your switchboard over time:

1. **Track your actual spend** — review your OpenRouter dashboard weekly to see which models are burning tokens
2. **Add your own routing signals** — if your workflow has domain terms (e.g., "settlement", "pricing", "vault"), map them to tiers
3. **Tune the 80/15/5 split** — if you find yourself escalating more than 5% of tasks, your classification may be too aggressive
4. **Pin model versions** — when a cheap model works well for you, pin the version (e.g., `deepseek/deepseek-chat-v3.1`) so provider updates don't break your flow
5. **Set OpenRouter budget alerts** — catch runaway premium usage before it compounds
