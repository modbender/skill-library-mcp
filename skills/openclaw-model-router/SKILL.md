---
name: model-router
description: Intelligent cost-aware model routing that classifies task complexity and selects the optimal AI model. Automatically routes simple tasks to cheap models and complex tasks to premium models. Use when you need "which model should I use", "route this task", "optimize cost", "switch model", "cheapest model for this", "use the right model", or to balance quality vs cost across AI providers. Supports progressive escalation, 5-tier routing, and current model pricing.
version: 2.0.0
---

# Smart Model Router

**Intelligent cost-aware model routing for OpenClaw agents.**

Before executing any task via `sessions_spawn` or delegating to a sub-agent, classify the task complexity using the rules below and route to the optimal model. This saves 60-90% on LLM costs by using cheap models for simple work and reserving premium models for tasks that genuinely need them.

## Core Principle

**Route every request to the cheapest model that can handle it well.**

## Step 1: Classify Task Complexity

Score the task on these dimensions. Count how many COMPLEX/REASONING indicators are present:

### SIMPLE indicators (route to Tier 1)
- Greetings, small talk, status checks, heartbeats
- Single factual questions ("What is X?", "Define Y")
- Simple translations, format conversions
- File lookups, directory listings, basic shell commands
- Calendar checks, weather queries
- Tasks under 50 tokens with no technical depth
- Keywords: "what is", "define", "translate", "list", "check", "hello", "status"

### MODERATE indicators (route to Tier 2)
- Summarization of documents or conversations
- Single-file code edits, bug fixes, simple refactors
- Writing emails, messages, short-form content
- Data extraction, parsing, formatting
- Explaining concepts, answering "how to" questions
- Research requiring synthesis of a few sources
- Keywords: "summarize", "explain", "write", "fix this", "how to", "extract"

### COMPLEX indicators (route to Tier 3)
- Multi-file code generation or refactoring
- Architecture design, system design
- Creative writing (stories, long-form, nuanced tone)
- Debugging complex issues across multiple systems
- Analysis requiring multiple perspectives
- Tasks with constraints ("optimize for X while maintaining Y")
- Keywords: "build", "design", "architect", "refactor", "create", "implement", "analyze"

### REASONING indicators (route to Tier 4)
- Mathematical proofs, formal logic
- Multi-step reasoning chains ("first X, then Y, therefore Z")
- Security vulnerability analysis
- Performance optimization with tradeoffs
- Scientific analysis, hypothesis testing
- Any task with 2+ of: "prove", "derive", "why does", "compare and contrast", "evaluate tradeoffs", "step by step"
- Keywords: "prove", "derive", "reason", "why does", "evaluate", "theorem"

### Special Rules
- **2+ reasoning keywords → always Tier 4** (high confidence)
- **Code blocks or multi-file references → minimum Tier 2**
- **"Debug" + stack traces → Tier 3**
- **Heartbeats and /status → always Tier 1**
- **When uncertain, default to Tier 2** (fast, cheap, good enough)

## Step 2: Select Model from Tier

### Tier 0 — FREE (OpenRouter free tier)
| Model | Cost | Best For |
|-------|------|----------|
| Gemini 2.5 Flash (free) | $0.00 | High-volume simple tasks, translation |
| Gemini 2.5 Flash-Lite (free) | $0.00 | Translation, marketing |
| Gemini 3 Flash Preview (free) | $0.00 | Technology, health, science |
| DeepSeek V3.2 (free) | $0.00 | Roleplay, creative writing |
| Moonshot Kimi K2.5 (free) | $0.00 | Technology, programming |
| Arcee Trinity Large Preview (free) | $0.00 | Creative writing, storytelling, agents |

**Default Tier 0 model:** `openrouter/free` (auto-selects from available free models)

Access via OpenRouter with model IDs like `google/gemini-2.5-flash`, `deepseek/deepseek-v3.2-20251201`, `moonshotai/kimi-k2.5-0127`. Or use `openrouter/free` to auto-route across all free models.

**Note:** Free models have rate limits and may have variable availability. Use for non-critical tasks only.

### Tier 1 — SIMPLE (near-zero cost)
| Model | Input $/MTok | Output $/MTok | Best For |
|-------|-------------|--------------|----------|
| Gemini 2.0 Flash | $0.10 | $0.40 | Default simple tier — fast, multimodal, 1M context |
| GPT-4o-mini | $0.15 | $0.60 | Simple tasks, multimodal |
| GPT-5 Nano | $0.05 | $0.40 | Cheapest OpenAI option |
| DeepSeek V3 | $0.27 | $1.10 | Budget general-purpose |
| Gemini 2.5 Flash-Lite | $0.10 | $0.40 | Most economical Google model |

**Default Tier 1 model:** `gemini-2.0-flash` (best cost/reliability balance)

### Tier 2 — MODERATE (balanced)
| Model | Input $/MTok | Output $/MTok | Best For |
|-------|-------------|--------------|----------|
| Claude Haiku 4.5 | $1.00 | $5.00 | Near-frontier, fast, great coding |
| GPT-4o | $2.50 | $10.00 | Multimodal, tool use, solid all-rounder |
| Gemini 2.5 Flash | $0.15 | $0.60 | Thinking-enabled, fast reasoning |
| GPT-5 Mini | $0.25 | $2.00 | Balanced performance, 400K context |
| Mistral Medium 3 | $0.40 | $2.00 | European languages, balanced |

**Default Tier 2 model:** `claude-haiku-4-5` (best quality-to-price at this tier)

### Tier 3 — COMPLEX (premium)
| Model | Input $/MTok | Output $/MTok | Best For |
|-------|-------------|--------------|----------|
| Claude Sonnet 4.5 | $3.00 | $15.00 | Best coding-to-cost ratio, most popular |
| GPT-5 | $1.25 | $10.00 | Flagship coding and agentic tasks |
| GPT-5.3 Codex | $1.75* | $14.00* | Most capable agentic coding model |
| Gemini 2.5 Pro | $1.25 | $10.00 | Coding, reasoning, up to 2M context |
| Claude Opus 4.5 | $5.00 | $25.00 | Maximum intelligence, agentic tasks |
| Grok 4 | $3.00 | $15.00 | Frontier reasoning, real-time data |

*GPT-5.3 Codex API pricing not yet officially released; estimated from GPT-5.2 Codex rates.

**Default Tier 3 model:** `claude-sonnet-4-5` (best balance of quality, coding, and cost)

### Tier 4 — REASONING (maximum capability)
| Model | Input $/MTok | Output $/MTok | Best For |
|-------|-------------|--------------|----------|
| Claude Opus 4.6 | $5.00 | $25.00 | Latest frontier reasoning, extended thinking, 1M context (beta) |
| Claude Opus 4.5 | $5.00 | $25.00 | Extended thinking, frontier reasoning |
| o3 | $2.00 | $8.00 | Deep STEM reasoning |
| DeepSeek R1 | $0.55 | $2.19 | Budget reasoning (20-50x cheaper than o1) |
| o4-mini | $1.10 | $4.40 | Efficient reasoning |

**Default Tier 4 model:** `claude-opus-4-6` with extended thinking enabled

## Step 3: Apply Optimization Mode

### 🟢 Balanced Mode (DEFAULT)
Use the default model for each tier as listed above. Escalate to next tier if the model produces low-quality output or fails.

### 🔵 Aggressive Mode (Maximum Savings)
Override tier defaults to cheapest option:
- Tier 0-1: `openrouter/free` ($0.00) for simple tasks, fall back to `gemini-2.0-flash` ($0.10/$0.40)
- Tier 2: `gemini-2.5-flash` ($0.15/$0.60)
- Tier 3: `gemini-2.5-pro` ($1.25/$10.00)
- Tier 4: `deepseek-r1` ($0.55/$2.19)

**Savings: 70-99% vs always using Opus**

### 🟡 Quality Mode (Maximum Quality)
Override tier defaults to best-in-class:
- Tier 1: `claude-haiku-4-5` ($1.00/$5.00)
- Tier 2: `claude-sonnet-4-5` ($3.00/$15.00)
- Tier 3: `claude-opus-4-6` ($5.00/$25.00) or `gpt-5.3-codex` for coding
- Tier 4: `claude-opus-4-6` ($5.00/$25.00) with extended thinking

## Step 4: Execute with sessions_spawn

```bash
# Simple task — Tier 1
sessions_spawn --task "What's on my calendar today?" --model gemini-2.0-flash

# Moderate task — Tier 2
sessions_spawn --task "Summarize this document" --model claude-haiku-4-5

# Complex task — Tier 3
sessions_spawn --task "Build a React auth component with tests" --model claude-sonnet-4-5

# Reasoning task — Tier 4
sessions_spawn --task "Prove this algorithm is O(n log n)" --model claude-opus-4-6
```

## Progressive Escalation Pattern

When uncertain about complexity, start cheap and escalate:

```bash
# 1. Try Tier 1 with timeout
sessions_spawn --task "Fix this bug" --model gemini-2.0-flash --runTimeoutSeconds 60

# 2. If output is poor or times out, escalate to Tier 2
sessions_spawn --task "Fix this bug" --model claude-haiku-4-5

# 3. If still failing, escalate to Tier 3
sessions_spawn --task "Fix this complex bug" --model claude-sonnet-4-5
```

Maximum escalation chain: 3 attempts. If Tier 3 fails, surface the error to the user rather than burning tokens.

## Parallel Processing for Batch Tasks

Route batch/parallel tasks to Tier 1 models for massive savings:

```bash
# Batch summaries in parallel with cheap model
sessions_spawn --task "Summarize doc A" --model gemini-2.0-flash &
sessions_spawn --task "Summarize doc B" --model gemini-2.0-flash &
sessions_spawn --task "Summarize doc C" --model gemini-2.0-flash &
wait

# Then analyze results with premium model
sessions_spawn --task "Synthesize findings from all summaries" --model claude-sonnet-4-5
```

## Special Routing Rules

| Scenario | Route To | Why |
|----------|----------|-----|
| Heartbeat / status check | Tier 0 (`openrouter/free`) or Tier 1 | Zero intelligence needed, save every cent |
| Vision / image analysis | `gemini-2.5-pro` | Best multimodal + huge context |
| Long context (>100K tokens) | `gemini-2.5-pro` or `gpt-5` | 1M-2M context windows |
| Chinese language tasks | `deepseek-v3` or `glm-4.7` | Optimized for Chinese |
| Real-time web data needed | `grok-4.1-fast` | Built-in X/web search, 2M context |
| Agentic coding tasks | `gpt-5.3-codex` or `claude-sonnet-4-5` | Purpose-built for agentic code workflows |
| Code generation | `claude-sonnet-4-5` minimum | Best code quality per dollar |
| Math / formal proofs | `o3` or `claude-opus-4-6` with thinking | Specialized reasoning |

## Cost Comparison (Typical Workload)

For a typical OpenClaw day (24 heartbeats + 20 sub-agent tasks + 10 user queries):

| Strategy | Monthly Cost | Savings |
|----------|-------------|---------|
| All Opus 4.6 | ~$200 | baseline |
| Smart routing (balanced) | ~$45 | **78%** |
| Smart routing (aggressive) | ~$15 | **92%** |
| Smart routing (aggressive + free tier) | ~$5 | **97%** |
| All free models (OpenRouter) | ~$0 | 100% (but rate-limited & unreliable) |

## When NOT to Route Down

Always use Tier 3+ for:
- Security-sensitive code review
- Financial calculations where errors are costly
- Architecture decisions that affect the whole codebase
- Anything the user explicitly asks for premium quality
- Tasks where the user says "be thorough" or "take your time"

## Mode Switching

Users can switch modes mid-conversation:
- "Use aggressive routing" → Switch to cheapest models per tier
- "Use quality mode" → Switch to best models per tier
- "Use balanced routing" → Return to defaults
- "Use [specific model] for this" → Override routing for one task

## Pricing Reference (February 2026)

All prices per million tokens. Models are listed from cheapest to most expensive output:

| Model | Input | Output | Context | Provider |
|-------|-------|--------|---------|----------|
| OpenRouter Free Models | $0.00 | $0.00 | Varies | OpenRouter |
| GPT-5 Nano | $0.05 | $0.40 | 400K | OpenAI |
| Gemini 2.0 Flash | $0.10 | $0.40 | 1M | Google |
| Gemini 2.5 Flash-Lite | $0.10 | $0.40 | 1M | Google |
| GPT-4o-mini | $0.15 | $0.60 | 128K | OpenAI |
| Gemini 2.5 Flash | $0.15 | $0.60 | 1M | Google |
| Grok 4.1 Fast | $0.20 | $0.50 | 2M | xAI |
| GPT-5 Mini | $0.25 | $2.00 | 400K | OpenAI |
| DeepSeek V3 | $0.27 | $1.10 | 64K | DeepSeek |
| DeepSeek R1 | $0.55 | $2.19 | 64K | DeepSeek |
| Claude Haiku 4.5 | $1.00 | $5.00 | 200K | Anthropic |
| o4-mini | $1.10 | $4.40 | 200K | OpenAI |
| Gemini 2.5 Pro | $1.25 | $10.00 | 1M | Google |
| GPT-5 | $1.25 | $10.00 | 400K | OpenAI |
| GPT-5.3 Codex | $1.75* | $14.00* | 400K | OpenAI |
| o3 | $2.00 | $8.00 | 200K | OpenAI |
| GPT-4o | $2.50 | $10.00 | 128K | OpenAI |
| Claude Sonnet 4.5 | $3.00 | $15.00 | 200K | Anthropic |
| Grok 4 | $3.00 | $15.00 | 256K | xAI |
| Claude Opus 4.5 | $5.00 | $25.00 | 200K | Anthropic |
| Claude Opus 4.6 | $5.00 | $25.00 | 200K (1M beta) | Anthropic |

*GPT-5.3 Codex pricing estimated from GPT-5.2 Codex; official API pricing pending.

**Note:** Prices change. Check provider pricing pages for current rates. Batch API discounts (50% off) and prompt caching (50-90% off) can reduce costs further. OpenRouter free models have rate limits — see openrouter.ai/collections/free-models for current availability.
