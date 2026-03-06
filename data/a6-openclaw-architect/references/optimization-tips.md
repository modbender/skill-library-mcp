# OpenClaw Optimization Tips

## Model Selection & Cost

### Right-size your models
| Task | Recommended | Cost (per 1M tokens) |
|------|------------|---------------------|
| Main conversation | Claude Opus 4 | $5 in / $25 out |
| Sub-agent work | Claude Sonnet 4 | $3 in / $15 out |
| Bulk publishing | Claude Sonnet 4 | $3 in / $15 out |
| Quick classification | Haiku 4.5 | $1 in / $5 out |
| Embeddings | text-embedding-3-small | $0.02 in |
| Entity extraction (Mem0) | Gemini Flash Lite | $0.075 in |

**Rule:** Use the cheapest model that's still good enough for the task.

### Fallback chain design
```json
{
  "primary": "anthropic/claude-opus-4-6",
  "fallbacks": [
    "openrouter/moonshotai/kimi-k2-thinking",
    "openrouter/deepseek/deepseek-v3.2"
  ]
}
```
- Primary: best quality (Opus)
- Fallback 1: good quality, different provider (Kimi K2)
- Fallback 2: cheap but capable (DeepSeek)
- **Test each fallback** — don't assume they work

### Sub-agent cost control
- Use Sonnet 4 for sub-agents, not Opus (5x cheaper)
- Set `maxConcurrent: 8` to prevent runaway parallel costs
- Kill stale sub-agents: `subagents list` then `subagents kill`

## Context Window Management

### Keep workspace files lean
- MEMORY.md: < 4000 tokens (it loads every session)
- AGENTS.md: < 3000 tokens
- TOOLS.md: only active tools, remove unused
- SOUL.md: < 1000 tokens

### Enable context pruning
```json
{
  "contextPruning": {
    "mode": "cache-ttl",
    "ttl": "5m"
  }
}
```
Prunes old cached content, keeping context window efficient.

### Memory flush before compaction
```json
{
  "compaction": {
    "memoryFlush": {
      "enabled": true,
      "softThresholdTokens": 4000
    }
  }
}
```
Saves important info before context is summarized — prevents data loss.

## Cron Job Optimization

### Batch related tasks
Instead of 5 separate cron jobs, combine into 1 that does all 5 checks.
Each cron fire = 1 model call = credits used.

### Use `system` delivery for maintenance
`announce` = streaming response to user = more expensive.
`system` = silent processing = cheaper.

### Disable unused crons
Every running cron burns credits. Audit monthly:
```bash
openclaw cron list
# Disable anything not providing value
openclaw cron disable <id>
```

## Infrastructure Optimization

### Docker resource limits
```yaml
services:
  openclaw:
    deploy:
      resources:
        limits:
          memory: 2G
        reservations:
          memory: 1G
```

### Brain stack tuning
- **Qdrant:** Set `QDRANT__STORAGE__OPTIMIZERS__MEMMAP_THRESHOLD_KB=20480` for lower RAM
- **Neo4j:** Set `NEO4J_server_memory_heap_max__size=512m` to cap memory
- **SQLite:** No tuning needed — it's lightweight

### Network optimization
- Use `trustedProxies` to avoid double proxy overhead
- Enable `allowTailscale` for zero-config internal access
- Keep services on Docker internal network when possible

## Publishing Optimization

### Batch publishing saves money
- Group 15-20 skills per batch
- Use Sonnet 4 sub-agents (not Opus)
- One agent per batch, chain when slots free
- Log results to avoid re-publishing

### Skill quality = ranking
- Longer, more detailed SKILL.md = better discovery
- Include real examples, not just API docs
- Add troubleshooting section
- Use searchable description text

## Monitoring & Alerts

### Credit monitoring cron
Run every 4 hours, alert if balance drops below threshold:
```json
{
  "name": "credit-monitor",
  "schedule": "0 */4 * * *",
  "message": "Check credit balances (Anthropic + OpenRouter), alert if < $5",
  "delivery": "system"
}
```

### Health monitoring
```bash
# Quick check
openclaw health && echo "OK" || echo "PROBLEM"

# Full diagnostic
openclaw doctor
```

## Cost Tracking

### What costs money
1. **Model inference** — every message, every cron fire, every sub-agent
2. **Embeddings** — memory search, brain_engine.py
3. **Search** — Perplexity API calls
4. **Infrastructure** — VPS, domain, services

### Cost reduction tactics
- Switch sub-agents from Opus to Sonnet (5x savings)
- Use Gemini Flash Lite for Mem0 extraction ($0.075 vs $3.00)
- Batch cron jobs to reduce inference calls
- Disable unused cron jobs and skills
- Use cache-ttl context pruning
