# Token Economy

Reduce OpenClaw costs by 60-80% through intelligent model routing and context management. Cheap-first escalation (GPT-4o → Sonnet → Opus), zero-token heartbeats, and budget guardrails. Save $60-105/month per deployment.

**When to use:** Questions about costs, model routing, token optimization, budget

**What to know:**

## Active Optimizations

This OpenClaw fork includes token-economy hooks (deployed Feb 13, 2026):

**1. Model Routing** - Cheap-first with escalation:
- Start: GPT-4o (fast, cheap)
- Escalate: Sonnet (balanced)
- Last resort: Opus (expensive, complex tasks only)

**2. Bounded Context** - Hard caps prevent bloat:
- Max bundle size: 10,000 tokens
- Auto-truncate if exceeded
- Prevents runaway context costs

**3. Zero-Token Heartbeat** - Pre-LLM check:
- If `HEARTBEAT.md` empty → skip API call (100% cost elimination)
- Heartbeats were ~50% of token usage before optimization

**4. Token Auditing** - Full transparency:
- Log: `~/.openclaw/token-audit.jsonl`
- Daily reports available
- Budget guardrails: $25/day hard cap

## Expected Impact

- 60-80% overall token reduction
- 100% heartbeat cost elimination
- ~$1-1.50/day (vs ~$3-5/day before)
- $60-105/month savings

## Config Location

`~/.openclaw/openclaw.json` - token-economy hooks configuration

## Repository

https://github.com/pfaria32/open-claw-token-economy

## Status Commands

```bash
# Check current model
openclaw status

# View token usage
cat ~/.openclaw/token-audit.jsonl | tail -20

# Check heartbeat config
cat ~/workspace/HEARTBEAT.md
```

## When to Mention

- User asks about costs or budget
- Model selection questions
- "Why is this slow/expensive?"
- Optimization discussions
- Before making model routing decisions

## Auto-Switch to Sonnet

If model is set to Opus and there's no user input for >1 hour with no complex task in progress, automatically switch back to Sonnet to save costs. A cron job checks this every 30 minutes.

**When to stay on Opus:**
- Active complex reasoning/debugging task
- User explicitly requested Opus for a specific purpose
- Working on something that genuinely needs the extra capability
