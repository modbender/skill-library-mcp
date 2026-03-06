# Token Optimizer for OpenClaw

**Reduce your AI costs by 97% - From $1,500+/month to under $50/month**

[![Version](https://img.shields.io/badge/version-1.0.18-blue.svg)](https://github.com/smartpeopleconnected/openclaw-token-optimizer)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![OpenClaw](https://img.shields.io/badge/OpenClaw-Compatible-purple.svg)](https://openclaw.ai)
[![Cost Savings](https://img.shields.io/badge/savings-97%25-brightgreen.svg)](https://github.com/smartpeopleconnected/openclaw-token-optimizer)
[![Ko-fi](https://img.shields.io/badge/Ko--fi-Support%20this%20project-FF5E5B?logo=ko-fi&logoColor=white)](https://ko-fi.com/smartpeopleconnected)

---

## The Problem

If you've been running OpenClaw and watching your API bills climb, you're not alone. The default configuration prioritizes capability over cost, which means you're probably burning through tokens on routine tasks that don't need expensive models.

**Common issues:**
- Loading 50KB of history on every message (2-3M wasted tokens/session)
- Using Sonnet/Opus for simple tasks that Haiku handles perfectly
- Paying for API heartbeats that could run on a free local LLM
- No rate limits leading to runaway automation costs

## The Solution

Token Optimizer applies four key optimizations that work together to slash your costs:

| Optimization | Before | After | Savings |
|--------------|--------|-------|---------|
| Session Management | 50KB context | 8KB context | 80% |
| Model Routing | Sonnet for everything | Haiku default | 92% |
| Heartbeat to Ollama | Paid API | Free local LLM | 100% |
| Prompt Caching | No caching | 90% cache hits | 90% |

**Combined result: 97% cost reduction**

## Cost Comparison

| Time Period | Before | After |
|-------------|--------|-------|
| Daily | $2-3 | **$0.10** |
| Monthly | $70-90 | **$3-5** |
| Yearly | $800+ | **$40-60** |

## What This Tool Modifies

All changes are written under `~/.openclaw/`. A backup is created before any modification.

| Path | Purpose |
|------|---------|
| `~/.openclaw/openclaw.json` | Main OpenClaw config (model routing, heartbeat, budgets) |
| `~/.openclaw/backups/` | Timestamped config backups (created automatically) |
| `~/.openclaw/workspace/` | Template files (SOUL.md, USER.md, IDENTITY.md) |
| `~/.openclaw/prompts/` | Agent prompt optimization rules |
| `~/.openclaw/token-optimizer-stats.json` | Usage stats for savings reports |

**Safe by default** - All commands run in dry-run (preview) mode. Pass `--apply` to write changes.

## Quick Start

### Installation

```bash
# Preview changes (dry-run by default)
python cli.py optimize

# Apply changes
python cli.py optimize --apply

# Quick health check
python cli.py health
```

### Verify Setup

```bash
python cli.py verify
```

## Features

### 1. Intelligent Model Routing
Sets Haiku as the default model with easy aliases for switching:
- `haiku` - Fast, cheap, perfect for 80% of tasks
- `sonnet` - Complex reasoning, architecture decisions
- `opus` - Mission-critical only

### 2. Free Heartbeats via Ollama
Routes heartbeat checks to a local LLM (llama3.2:3b) instead of paid API:
- Zero API calls for status checks
- No impact on rate limits
- Saves $5-15/month automatically

### 3. Lean Session Management
Optimized context loading rules that reduce startup context from 50KB to 8KB:
- Load only essential files (SOUL.md, USER.md)
- On-demand history retrieval
- Daily memory notes instead of history bloat

### 4. Prompt Caching
Automatic 90% discount on repeated content:
- Agent prompts cached and reused
- 5-minute TTL for optimal cache hits
- Per-model cache configuration

### 5. Budget Controls
Built-in rate limits and budget warnings:
- Daily/monthly budget caps
- Warning at 75% threshold
- Rate limiting between API calls

## Usage

### Analyze Current Setup
```bash
python cli.py analyze
```

Shows current configuration status, workspace file sizes, optimization opportunities, and estimated monthly savings.

### Preview Changes (Dry Run - Default)
```bash
python cli.py optimize
```

Shows a colored unified diff of what would change, without modifying anything.

### Apply Full Optimization
```bash
python cli.py optimize --apply
```

Applies all optimizations: model routing, heartbeat, caching, rate limits, workspace templates, and agent prompts.

### Apply Specific Optimizations
```bash
python cli.py optimize --apply --mode routing    # Model routing only
python cli.py optimize --apply --mode heartbeat  # Heartbeat only
python cli.py optimize --apply --mode caching    # Prompt caching only
python cli.py optimize --apply --mode limits     # Rate limits only
```

### Quick Health Check
```bash
python cli.py health
```

Checks config exists, valid JSON, provider reachable, workspace lean, and budget active.

### Configure Heartbeat Provider
```bash
# Preview (dry-run by default)
python cli.py setup-heartbeat --provider ollama

# Apply changes
python cli.py setup-heartbeat --provider ollama --apply
python cli.py setup-heartbeat --provider lmstudio --apply
python cli.py setup-heartbeat --provider groq --apply
python cli.py setup-heartbeat --provider none --apply
python cli.py setup-heartbeat --provider groq --fallback ollama --apply
```

### Rollback Configuration
```bash
python cli.py rollback --list            # List available backups
python cli.py rollback --to <filename>   # Restore a specific backup
```

### Verify Setup
```bash
python cli.py verify
```

### Disable Colors
```bash
python cli.py --no-color optimize
# or
NO_COLOR=1 python cli.py optimize
```

## Configuration

After installation, edit these files:

### `~/.openclaw/workspace/SOUL.md`
Agent principles and operating rules. Includes:
- Model selection rules
- Session initialization rules
- Rate limit rules

### `~/.openclaw/workspace/USER.md`
Your context: name, role, mission, success metrics.

### `~/.openclaw/prompts/OPTIMIZATION-RULES.md`
Copy these rules into your agent prompt.

## Requirements

- Python 3.8+
- OpenClaw installed and configured
- Ollama (optional, for free heartbeats)

### Installing Ollama (Optional)

Ollama is only needed if you want free local heartbeats. Download from [https://ollama.ai](https://ollama.ai), then:
```bash
ollama pull llama3.2:3b
ollama serve
```

Or use the CLI to configure a different provider:
```bash
python cli.py setup-heartbeat --provider lmstudio
python cli.py setup-heartbeat --provider none  # disable heartbeat
```

## File Structure

```
token-optimizer/
+-- skill.json                 # Skill manifest
+-- README.md                  # This file
+-- src/
|   +-- __init__.py            # Version (single source of truth)
|   +-- colors.py              # Shared ANSI colors
|   +-- analyzer.py            # Analyzes current config
|   +-- optimizer.py           # Applies optimizations
|   +-- verify.py              # Verifies setup
+-- templates/
|   +-- openclaw-config-optimized.json
|   +-- SOUL.md
|   +-- USER.md
|   +-- OPTIMIZATION-RULES.md
+-- test/
    +-- simulation_test.py     # Simulation tests
```

## Troubleshooting

### Context size still large
- Ensure SESSION INITIALIZATION RULE is in your agent prompt
- Check that SOUL.md and USER.md are lean (<15KB total)

### Still using Sonnet for everything
- Verify `~/.openclaw/openclaw.json` has correct model configuration
- Ensure MODEL SELECTION RULE is in agent prompt

### Heartbeat errors
- Make sure Ollama is running: `ollama serve`
- Verify model is installed: `ollama list`

### Costs haven't dropped
- Run `python src/verify.py` to check all optimizations
- Ensure agent prompt includes all optimization rules

## Support

- **Issues:** [GitHub Issues](https://github.com/smartpeopleconnected/openclaw-token-optimizer/issues)

**If this tool saved you money, consider supporting development:**

[![Ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/smartpeopleconnected)

## License

MIT License. See [LICENSE](LICENSE) for details.

---

**Built with care by Smart People Connected**

*Stop burning tokens. Start building things.*
