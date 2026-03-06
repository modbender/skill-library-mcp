# openclaw-daily-tips

> Daily AI agent optimization tips, tricks and self-improvement strategies for OpenClaw users.

[![OpenClaw Skill](https://img.shields.io/badge/OpenClaw-Skill-blue)](https://clawhub.ai)
[![Version](https://img.shields.io/badge/version-1.0.1-green)]()
[![Node.js](https://img.shields.io/badge/Node.js-18+-yellow)]()

Daily AI agent optimization tips to make your OpenClaw smarter, faster, and cheaper.

## What You'll Get

- 📈 **Daily Tips** - One actionable optimization per day
- 💰 **Cost Savings** - Reduce API costs with model routing
- ⚡ **Speed Improvements** - Faster responses and execution
- 🧠 **Memory Optimization** - Better context management
- 🤖 **Automation** - Cron and workflow best practices

## Installation

### Via ClawHub (Recommended)

```bash
npx clawhub install openclaw-daily-tips
```

### Manual

```bash
# Clone or copy to your skills folder
cp -r openclaw-daily-tips ~/.openclaw/workspace/skills/
```

## Usage

```bash
# Get today's optimization tip
node ~/.openclaw/workspace/skills/openclaw-daily-tips/scripts/openclaw-daily-tips.mjs tips

# Search for specific topic
node ~/.openclaw/workspace/skills/openclaw-daily-tips/scripts/openclaw-daily-tips.mjs search "cost"

# Weekly report
node ~/.openclaw/workspace/skills/openclaw-daily-tips/scripts/openclaw-daily-tips.mjs weekly

# List all tips
node ~/.openclaw/workspace/skills/openclaw-daily-tips/scripts/openclaw-daily-tips.mjs all
```

## Features

### Categories
| Category | Description |
|----------|-------------|
| Cost | Save money on API calls |
| Speed | Faster execution |
| Memory | Better context management |
| Skills | Skill development tips |
| Automation | Cron and workflow optimization |

### Impact Scores
- 🟢 Low Effort / High Reward
- 🟡 Medium Effort / Medium Reward
- 🔴 High Effort / Experimental

### Self-Learning
The skill tracks your preferences and improves over time:
- Save tips you find useful
- Skip topics you don't need
- Adapts to your workflow

## Tips Database

Current tips cover essential optimizations:

1. **Tiered Model Routing** - Use cheapest capable model
2. **Script-First Cron** - Move logic to scripts
3. **Alert-Only Delivery** - Return NO_REPLY on success
4. **Semantic Memory** - Better context recall
5. **Batch Jobs** - Combine similar tasks
6. **Isolated Sub-Agents** - Reduce context bloat
7. **Context Discipline** - Keep prompts lean
8. **Idempotent Cron** - Safe to re-run
9. **Heartbeat Optimization** - Background checks
10. **Modular Skills** - Keep SKILL.md short

## Cron Schedule

Add to your cron jobs for daily tips:

```json
{
  "id": "openclaw-daily-tips",
  "schedule": { "kind": "cron", "expr": "0 9 * * *" }
}
```

## SEO Keywords

openclaw tips, openclaw daily, openclaw optimization, ai agent tips, agent optimization, openclaw cost, openclaw memory, cron optimization, ai automation, openclaw tricks, daily ai tips, openclaw improve

## Related Skills

- [openclaw-agent-optimize](https://clawhub.ai/phenomenoner/openclaw-agent-optimize) - Deep optimization audit
- [openclaw-token-optimizer](https://clawhub.ai/phenomenoner/openclaw-token-optimizer) - Token cost optimization
- [memory-setup](https://clawhub.ai/phenomenoner/memory-setup) - Memory configuration
- [compound-engineering](https://clawhub.ai/phenomenoner/compound-engineering) - Agent self-improvement

## Contributing

Tips are curated from:
- Reddit communities (r/openclaw, r/LocalLLaMA)
- GitHub issues and discussions
- OpenClaw documentation
- Community feedback

## License

MIT

---

**Star ⭐ if this helps your OpenClaw!**
