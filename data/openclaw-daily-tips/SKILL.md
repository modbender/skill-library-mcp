---
name: openclaw-daily-tips
slug: openclaw-daily-tips
version: 1.0.1
description: |
  Daily AI agent optimization tips, tricks and self-improvement strategies. Learn cost-saving, speed, memory and automation best practices from the OpenClaw community.
  
  Use when: you want daily tips to optimize your AI agent, reduce costs, improve performance, or learn automation workflows.
  
  Don't use when: you need immediate config changes - use openclaw-agent-optimize for deep audits.
triggers:
  - openclaw tips
  - openclaw daily
  - openclaw tricks
  - ai agent tips
  - agent optimization
  - openclaw improve
  - ai automation tips
  - openclaw cost optimization
  - openclaw memory tips
  - cron optimization
  - daily ai agent
  - agent self improvement
metadata:
  openclaw:
    emoji: "📈"
    requires:
      bins: ["node"]
      env: []
---

# openclaw-daily-tips

Daily AI agent optimization tips and self-improvement strategies for OpenClaw users.

## What This Skill Does

- Fetches daily optimization tips from community sources
- Tracks your preferences and learns what works for you
- Provides actionable advice with impact scores
- Helps reduce costs and improve agent performance

## Quick Start

```bash
# Get today's tip
node ~/.openclaw/workspace/skills/openclaw-daily-tips/scripts/openclaw-daily-tips.mjs tips

# Search for specific topic
node ~/.openclaw/workspace/skills/openclaw-daily-tips/scripts/openclaw-daily-tips.mjs search "cost"

# Weekly report
node ~/.openclaw/workspace/skills/openclaw-daily-tips/scripts/openclaw-daily-tips.mjs weekly

# List all available tips
node ~/.openclaw/workspace/skills/openclaw-daily-tips/scripts/openclaw-daily-tips.mjs all
```

## Features

### Categories
- **Cost**: Save money on API calls, model routing
- **Speed**: Faster responses, reduced latency
- **Memory**: Context optimization, memory patterns
- **Skills**: New skill recommendations
- **Automation**: Cron, heartbeat, workflow optimization

### Impact Score
- 🟢 Low effort / High reward
- 🟡 Medium effort / Medium reward  
- 🔴 High effort / Experimental

### Self-Learning
The skill remembers your preferences:
- Saved tips are tracked
- Skipped topics won't reappear
- Adapts to your needs over time

## Cron Integration

Schedule daily tips at 9 AM:

```json
{
  "id": "openclaw-daily-tips",
  "schedule": { "kind": "cron", "expr": "0 9 * * *" }
}
```

## Output Example

```
📈 OPENCLAW-DAILY-TIPS - Your Agent Smarter Every Day

💡 TIP OF THE DAY (High Impact)
Title: Use tiered model routing

🟢 Low Effort | 📈 High Impact

What:
- Route simple tasks to cheap models
- Route complex tasks to premium models
- Save significant API costs

How:
1. Add model routing in cron jobs
2. Use cheap model for routine tasks
3. Reserve premium for complex reasoning

🔗 docs.openclaw.ai/models

━━━━━━━━━━━━━━
👍 Save this | 👎 Skip | ➕ More tips
```

## Categories Explained

| Category | What You'll Learn |
|----------|------------------|
| Cost | Model routing, token optimization, batching |
| Speed | Caching, lazy loading, parallel execution |
| Memory | Context discipline, progressive disclosure |
| Skills | Skill best practices, modular design |
| Automation | Cron optimization, alert patterns |

## Tips Database

Current tips cover:
- Tiered model selection
- Script-first cron patterns
- Alert-only delivery
- Semantic memory search
- Batch similar jobs
- Isolated sub-agents
- Context discipline
- Idempotent cron jobs
- Heartbeat optimization
- Modular skill design

## Requirements

- Node.js 18+
- OpenClaw workspace
- Optional: reddit-readonly skill for community feeds

## Related Skills

- **openclaw-agent-optimize** - Deep optimization audit
- **openclaw-token-optimizer** - Token cost optimization  
- **memory-setup** - Memory configuration
- **daily-digest** - General daily briefing
- **compound-engineering** - Agent self-improvement

## Credits

Inspired by openclaw-agent-optimize and the OpenClaw community.

---

## Install

```bash
clawhub install openclaw-daily-tips
```

Or manually copy to your skills directory.
