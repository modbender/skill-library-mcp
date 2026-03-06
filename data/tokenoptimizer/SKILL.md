---
name: token-optimizer
description: Reduce OpenClaw AI costs by 97%. Haiku model routing, free Ollama heartbeats, prompt caching, and budget controls. Go from $1,500/month to $50/month in 5 minutes.
homepage: https://github.com/smartpeopleconnected/openclaw-token-optimizer
triggers:
  - too expensive
  - costs too much
  - burning tokens
  - high token usage
  - reduce costs
  - save money
  - optimize tokens
  - budget exceeded
  - token optimization
  - cut api costs
  - lower ai spend
  - cheaper model
  - cost savings
  - api bill
  - spending too much
  - waste tokens
  - token budget
  - reduce token usage
---

# Token Optimizer for OpenClaw

Slash your AI costs from $1,500+/month to under $50/month.

## The Problem

OpenClaw defaults prioritize capability over cost. You're burning expensive Sonnet/Opus tokens on tasks Haiku handles perfectly, paying for API heartbeats that could run free locally, and loading 50KB of context when 8KB suffices.

## The Solution

Four core optimizations plus powerful tooling:

### Model Routing (92% savings)
Haiku by default, Sonnet/Opus only when needed

### Multi-Provider Heartbeats (100% savings)
Route heartbeats to Ollama, LM Studio, Groq, or disable entirely. Not locked to one provider.

### Session Management (80% savings)
Load 8KB instead of 50KB context

### Caching (90% savings)
Reuse prompts at 10% cost

### New in v1.0.8
- **Rollback** - List and restore config backups instantly
- **Health Check** - Quick system status in one command
- **Diff Preview** - See exactly what changes before applying
- **--no-color** - CI/pipeline friendly output

## Cost Comparison

| Period | Before | After |
|--------|--------|-------|
| Daily | $2-3 | $0.10 |
| Monthly | $70-90 | $3-5 |
| Yearly | $800+ | $40-60 |

## What's Included

- One-command optimizer with diff preview
- Multi-provider heartbeat (Ollama, LM Studio, Groq)
- Config rollback and health check commands
- Ready-to-use config templates
- SOUL.md & USER.md templates
- Optimization rules for agent prompts
- Verification and savings reports

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

```bash
# Install
clawhub install token-optimizer

# Analyze current setup
python cli.py analyze

# Preview changes (dry-run by default)
python cli.py optimize

# Apply all optimizations
python cli.py optimize --apply

# Verify setup
python cli.py verify

# Quick health check
python cli.py health

# Configure heartbeat provider (preview)
python cli.py setup-heartbeat --provider ollama

# Configure heartbeat provider (apply)
python cli.py setup-heartbeat --provider ollama --apply

# List and restore backups
python cli.py rollback --list
python cli.py rollback --to <backup-file>
```

## Configuration Generated

```json
{
  "agents": {
    "defaults": {
      "model": { "primary": "anthropic/claude-haiku-4-5" },
      "cache": { "enabled": true, "ttl": "5m" }
    }
  },
  "heartbeat": {
    "provider": "ollama",
    "model": "ollama/llama3.2:3b"
  },
  "budgets": {
    "daily": 5.00,
    "monthly": 200.00
  }
}
```

## Links

- **GitHub**: https://github.com/smartpeopleconnected/openclaw-token-optimizer
- **Issues**: https://github.com/smartpeopleconnected/openclaw-token-optimizer/issues

## Author

**Smart People Connected**
- GitHub: [@smartpeopleconnected](https://github.com/smartpeopleconnected)
- Email: smartpeopleconnected@gmail.com

## License

MIT License - Free to use, modify, and distribute.

---

*5 minutes to setup. 97% cost reduction. Stop burning tokens. Start building.*
