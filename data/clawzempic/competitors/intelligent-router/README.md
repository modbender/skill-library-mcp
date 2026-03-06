# Intelligent Router

**Version:** 2.0.0  
**License:** MIT

An intelligent model routing system for AI agent task delegation. Optimize costs by routing simple tasks to cheaper models while preserving quality for complex work.

## Overview

The Intelligent Router helps AI agents make smart decisions about which LLM model to use for different tasks. By classifying tasks into four tiers (SIMPLE, MEDIUM, COMPLEX, CRITICAL) and routing them to appropriate models, you can reduce costs by 80-95% without sacrificing quality on important work.

**Key benefits:**
- 📉 **Massive cost savings** — Route simple tasks to cheap models
- 🎯 **Quality where it matters** — Use premium models for critical work
- 🚀 **Simple to use** — Clear tier system and CLI tools
- 🔧 **Fully customizable** — Bring your own models and pricing
- 📊 **Cost estimation** — Know before you spend

## Quick Start

### 1. Installation

```bash
# Via ClawHub (recommended)
clawhub install intelligent-router

# Or manually
cd skills/
git clone <this-repo> intelligent-router
```

### 2. Configuration

Edit `config.json` to define your available models:

```json
{
  "models": [
    {
      "id": "openai/gpt-4o-mini",
      "alias": "GPT-4o Mini",
      "tier": "MEDIUM",
      "provider": "openai",
      "input_cost_per_m": 0.15,
      "output_cost_per_m": 0.60,
      "context_window": 128000,
      "capabilities": ["text", "code", "vision"],
      "notes": "Great balance of cost and capability"
    }
  ]
}
```

**Required fields:**
- `id` — Model identifier (e.g., "provider/model-name")
- `alias` — Human-friendly name
- `tier` — One of: SIMPLE, MEDIUM, COMPLEX, CRITICAL
- `input_cost_per_m` — Cost per million input tokens (USD)
- `output_cost_per_m` — Cost per million output tokens (USD)

**Recommended:** Include at least one model per tier for full coverage.

### 3. Classify Tasks

Use the CLI to classify tasks and get model recommendations:

```bash
# Classify a task
python scripts/router.py classify "fix authentication bug"
# Output:
#   Classification: MEDIUM
#   Recommended Model: GPT-4o Mini
#   Cost: $0.15/$0.60 per M tokens

# Estimate cost
python scripts/router.py cost-estimate "build payment processing system"
# Output:
#   Tier: COMPLEX
#   Estimated cost: $0.060 USD

# List your models
python scripts/router.py models
# Output: All configured models grouped by tier

# Check configuration health
python scripts/router.py health
# Output: Validates config.json structure
```

### 4. Use in Your Agent

When spawning sub-agents, reference models from your config:

```python
# Simple task — use cheap model
sessions_spawn(
    task="Check server status and report",
    model="openai/gpt-4o-mini",  # Your SIMPLE tier model
    label="health-check"
)

# Complex task — use premium model
sessions_spawn(
    task="Build authentication system with JWT",
    model="anthropic/claude-sonnet-4",  # Your COMPLEX tier model
    label="auth-build"
)
```

## The Four-Tier System

| Tier | Use For | Model Characteristics | Example Cost |
|------|---------|----------------------|--------------|
| **🟢 SIMPLE** | Monitoring, checks, summaries | Fast, cheap, reliable | $0.10-$0.50/M |
| **🟡 MEDIUM** | Code fixes, research, analysis | Balanced cost/quality | $0.50-$3.00/M |
| **🟠 COMPLEX** | Multi-file builds, debugging | High-quality reasoning | $3.00-$5.00/M |
| **🔴 CRITICAL** | Security, production, financial | Best available | $5.00+/M |

### Tier Selection Heuristics

**Keywords that trigger each tier:**

- **SIMPLE**: check, monitor, fetch, status, list, summarize
- **MEDIUM**: fix, patch, research, analyze, review, test
- **COMPLEX**: build, create, debug, architect, design, integrate
- **CRITICAL**: security, production, deploy, financial, audit

**Examples:**

```
"Check GitHub notifications" → SIMPLE
"Fix bug in login.py" → MEDIUM
"Build authentication system" → COMPLEX
"Security audit of auth code" → CRITICAL
```

## Configuration Guide

### Model Selection Criteria

**SIMPLE Tier:**
- Cost under $0.50/M input tokens
- Good for repetitive, well-defined tasks
- Examples: GPT-4o Mini, Gemini Flash, local Ollama models

**MEDIUM Tier:**
- Cost $0.50-$3.00/M input tokens
- Good at code and general reasoning
- Examples: GPT-4o Mini, Claude Haiku, Llama 3.3 70B

**COMPLEX Tier:**
- Cost $3.00-$5.00/M input tokens
- Excellent code generation and reasoning
- Examples: Claude Sonnet, GPT-4o, Gemini Pro

**CRITICAL Tier:**
- Best available quality
- For high-stakes operations only
- Examples: Claude Opus, GPT-4, Gemini Ultra, o1/o3

### Example Configurations

**Budget-conscious setup:**
```json
{
  "models": [
    {"id": "local/ollama-qwen", "tier": "SIMPLE", "input_cost_per_m": 0.00, ...},
    {"id": "openai/gpt-4o-mini", "tier": "MEDIUM", "input_cost_per_m": 0.15, ...},
    {"id": "anthropic/claude-sonnet", "tier": "COMPLEX", "input_cost_per_m": 3.00, ...}
  ]
}
```

**Performance-focused setup:**
```json
{
  "models": [
    {"id": "openai/gpt-4o-mini", "tier": "SIMPLE", "input_cost_per_m": 0.15, ...},
    {"id": "anthropic/claude-sonnet", "tier": "MEDIUM", "input_cost_per_m": 3.00, ...},
    {"id": "anthropic/claude-opus", "tier": "CRITICAL", "input_cost_per_m": 15.00, ...}
  ]
}
```

## CLI Reference

### `router.py classify <task>`

Classify a task and recommend a model.

```bash
python scripts/router.py classify "debug race condition in worker threads"
```

**Output:**
```
Task: debug race condition in worker threads

Classification: COMPLEX
Reasoning: Multi-file development, debugging, or architectural work

Recommended Model:
  ID: anthropic/claude-sonnet-4
  Alias: Claude Sonnet
  Provider: anthropic
  Cost: $3.00/$15.00 per M tokens
  Notes: High-quality model for complex multi-file development
```

---

### `router.py models`

List all configured models grouped by tier.

```bash
python scripts/router.py models
```

**Output:**
```
Configured Models by Tier:

SIMPLE:
  • GPT-4o Mini (openai/gpt-4o-mini) - $0.15/$0.60/M

MEDIUM:
  • Claude Haiku (anthropic/claude-haiku) - $0.80/$4.00/M

COMPLEX:
  • Claude Sonnet (anthropic/claude-sonnet-4) - $3.00/$15.00/M

CRITICAL:
  • Claude Opus (anthropic/claude-opus-4) - $15.00/$75.00/M
```

---

### `router.py health`

Validate configuration file.

```bash
python scripts/router.py health
```

**Output:**
```
Configuration Health Check
Config: /path/to/config.json
Status: HEALTHY
Models: 4

✅ Configuration is valid
```

---

### `router.py cost-estimate <task>`

Estimate the cost of running a task.

```bash
python scripts/router.py cost-estimate "build payment processing system"
```

**Output:**
```
Task: build payment processing system

Cost Estimate:
  Tier: COMPLEX
  Model: Claude Sonnet
  Estimated Tokens: 5000 in / 3000 out
  Input Cost: $0.015000
  Output Cost: $0.045000
  Total Cost: $0.060000 USD
```

## Usage Patterns

### Pattern 1: Simple Routing

For straightforward tasks, just spawn with the appropriate model:

```python
# Classify task (mentally or via CLI)
# "Check server health" → SIMPLE tier

sessions_spawn(
    task="Check server health and report status",
    model="openai/gpt-4o-mini",  # Your SIMPLE tier model
    label="health-check"
)
```

### Pattern 2: Two-Phase Processing

For large tasks, use a cheap model for bulk work, then refine with a better model:

```python
# Phase 1: Extract with SIMPLE model
sessions_spawn(
    task="Extract key sections from research paper at /tmp/paper.pdf",
    model="{simple_model}",
    label="extract"
)

# Phase 2: Analyze with MEDIUM model (after extraction completes)
sessions_spawn(
    task="Analyze extracted sections at /tmp/sections.txt",
    model="{medium_model}",
    label="analyze"
)
```

**Savings:** ~80% cost reduction by processing bulk content with cheap model.

### Pattern 3: Tiered Escalation

Start with MEDIUM tier, escalate to COMPLEX if needed:

```python
# Try MEDIUM first
result = sessions_spawn(
    task="Debug authentication issue",
    model="{medium_model}",
    label="debug-attempt-1"
)

# If unsuccessful, escalate
if not result.successful:
    sessions_spawn(
        task="Deep debug of authentication (previous attempt incomplete)",
        model="{complex_model}",
        label="debug-attempt-2"
    )
```

### Pattern 4: Batch Processing

Group similar simple tasks together:

```python
checks = ["server1", "server2", "server3", "database", "cache"]

sessions_spawn(
    task=f"Health check these services: {', '.join(checks)}. Report any issues.",
    model="{simple_model}",
    label="batch-checks"
)
```

## Cost Optimization Tips

### 1. Profile Your Workload

Track which tasks are most frequent:
- High-frequency tasks → optimize aggressively (use SIMPLE tier)
- Low-frequency tasks → quality over cost (use COMPLEX/CRITICAL tier)

### 2. Measure Success Rates

If a cheaper model requires frequent retries, it's not actually cheaper:
- Track: `(cost per attempt) / (success rate)` = true cost
- If SIMPLE tier has <80% success rate, use MEDIUM tier instead

### 3. Use Local Models for SIMPLE Tier

If you have GPU access, run local models (Ollama, vLLM) for high-frequency simple tasks:
- Zero API costs
- Unlimited usage
- Privacy benefits

### 4. Enable Thinking Mode Selectively

Extended thinking can 2-5x the cost but dramatically improves quality:
- **Use for:** Architecture decisions, complex debugging, critical analysis
- **Avoid for:** Routine tasks, simple code fixes, monitoring

```python
# Thinking mode for hard problem
sessions_spawn(
    task="Design scalable architecture for real-time system",
    model="{complex_model}",
    thinking="on",  # Worth the extra cost
    label="architecture"
)
```

### 5. Batch When Possible

Instead of spawning 10 agents for 10 health checks, spawn 1 agent to do all 10.

**Savings example:**
- 10 separate calls: 10× overhead
- 1 batched call: 1× overhead = ~40% reduction in actual costs

## Real-World Savings

**Example daily workload:**

| Task | Frequency | Tier | Cost/day | If All COMPLEX |
|------|-----------|------|----------|----------------|
| Health checks | 48/day | SIMPLE | $0.005 | $2.40 |
| Monitoring | 12/day | SIMPLE | $0.002 | $0.60 |
| Code reviews | 5/day | MEDIUM | $0.01 | $0.25 |
| Bug fixes | 2/day | MEDIUM | $0.01 | $0.10 |
| Features | 1/day | COMPLEX | $0.05 | $0.05 |
| Security | 1/week | CRITICAL | $0.07 | $0.07 |
| **Total** | | | **$0.147** | **$3.47** |

**Monthly:** $4.40 with routing vs $104 without = **96% savings**

## Documentation

- **[SKILL.md](SKILL.md)** — Complete routing guide and usage patterns
- **[references/model-catalog.md](references/model-catalog.md)** — How to evaluate and select models
- **[references/examples.md](references/examples.md)** — Real-world routing examples
- **[config.json](config.json)** — Model configuration template

## Requirements

- **Python:** 3.8 or higher
- **Dependencies:** None (uses only standard library)
- **Platform:** Cross-platform (Linux, macOS, Windows)

## Contributing

Contributions welcome! Areas for improvement:
- Additional classification heuristics
- Support for more cost factors (latency, throughput, etc.)
- Model capability detection
- Provider-specific optimizations

## License

MIT License — see LICENSE file for details.

## Support

- **Issues:** Open a GitHub issue for bugs or questions
- **Documentation:** See SKILL.md for detailed usage guide
- **Examples:** See references/examples.md for real-world patterns

---

**Built for ClawHub** — Part of the OpenClaw skill ecosystem.
