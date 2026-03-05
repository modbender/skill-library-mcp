---
name: context-optimizer
user-invocable: true
metadata: {"openclaw":{"emoji":"⚡","requires":{"bins":["node"]},"os":["darwin","linux","win32"]}}
---

# OpenClaw Context Optimizer

**Reduce context/token usage by 40-60% through intelligent compression and learning.**

## What is it?

The first OpenClaw skill that **intelligently compresses context** to reduce token costs by 40-60%. Uses multiple strategies (deduplication, pruning, summarization) and learns what context matters over time. Works seamlessly with Memory System for maximum efficiency.

## Key Features

- ⚡ **40-60% Token Savings** - Intelligent compression without information loss
- 🧠 **Learning System** - Adapts to what context matters in your workflow
- 🔄 **Multiple Strategies** - Dedup, prune, summarize, hybrid
- 💾 **Memory Integration** - Works with OpenClaw Memory System
- 💰 **x402 Payments** - Agents can pay for unlimited compressions (0.5 USDT/month)
- 📊 **ROI Tracking** - Automatically calculates return on investment

## Free vs Pro Tier

**Free Tier:**
- 100 compressions per day
- All compression strategies
- Basic statistics and ROI tracking

**Pro Tier (0.5 USDT/month):**
- Unlimited compressions
- Advanced learning algorithms
- Priority compression
- Detailed analytics
- Custom compression rules

## Installation

```bash
claw skill install openclaw-context-optimizer
```

## Commands

```bash
# Compress context manually
claw optimize compress "Long context..." --strategy=hybrid

# Show compression stats
claw optimize stats

# View compression history
claw optimize history --limit=10

# Calculate ROI
claw optimize roi

# Open dashboard
claw optimize dashboard

# Subscribe to Pro
claw optimize subscribe
```

## How It Works

1. **Hooks into requests** - Automatically intercepts context before API calls
2. **Analyzes content** - Identifies redundant, irrelevant, or summarizable info
3. **Applies strategy** - Deduplication → Pruning → Summarization
4. **Learns patterns** - Tracks what context was useful vs. wasted
5. **Compresses intelligently** - Reduces tokens by 40-60%

## Compression Strategies

**Deduplication (20-30% savings):**
- Removes repeated information across messages
- Best for long conversations with repeated facts

**Pruning (30-40% savings):**
- Removes low-importance messages (greetings, confirmations)
- Best for conversations with filler content

**Summarization (40-60% savings):**
- Condenses long exchanges into key points
- Best for technical discussions and planning

**Hybrid (40-60% savings - Recommended):**
- Combines all strategies intelligently
- Best for most use cases

## Use Cases

- Reduce token costs on long conversations
- Compress repeated project context
- Summarize technical discussions
- Remove filler from chat history
- Learn compression patterns over time

## Agent Economy

Agents can autonomously evaluate if Pro tier is worth it:
- **Cost:** 0.5 USDT/month
- **Value:** Saves 40-60% on token costs
- **ROI:** If saves >0.5 USDT/month in tokens, it pays for itself

**Example:**
```
Original: 5,000 tokens × $0.003/1K = $0.015 per request
Compressed: 2,000 tokens × $0.003/1K = $0.006 per request
Savings: $0.009 per request

60 requests/day = $0.54/day = $16.20/month saved
Pro cost: $0.50/month
Net profit: $15.70/month
```

See [AGENT-PAYMENTS.md](AGENT-PAYMENTS.md) for x402 integration details.

## Memory System Integration

**Works best with OpenClaw Memory System:**
- Stores compression patterns as memories
- Learns what context is important over time
- Recalls successful strategies from past sessions
- Combined savings: 50-70%

```bash
claw skill install openclaw-memory
claw skill install openclaw-context-optimizer
```

## Privacy

- All data stored locally in `~/.openclaw/openclaw-context-optimizer/`
- No external servers or telemetry
- Compression happens locally (no API calls)
- Open source - audit the code yourself

## Dashboard

Access web UI at `http://localhost:9092`:
- Real-time compression statistics
- Token savings over time
- ROI calculation (savings vs. Pro cost)
- Strategy performance comparison
- Compression history with before/after view
- Quota usage and license status

## ROI Tracking

Context Optimizer automatically calculates return on investment:

```bash
$ claw optimize roi

ROI Analysis (Last 30 Days)
────────────────────────────────
Total compressions: 1,247
Average savings: 60%

Cost without optimizer: $10.28
Cost with optimizer: $4.11
Savings: $6.17

Pro tier cost: $0.50/month
Net savings: $5.67/month
ROI: 1,134% 🎉
```

## Requirements

- Node.js 18+
- OpenClaw v2026.1.30+
- OS: Windows, macOS, Linux
- Optional: OpenClaw Memory System (recommended)

## API Reference

```bash
# Compress context
POST /api/compress
{
  "agent_wallet": "0x...",
  "context": "Long context...",
  "strategy": "hybrid"
}

# Get stats
GET /api/stats?agent_wallet=0x...

# Get ROI analysis
GET /api/roi?agent_wallet=0x...

# x402 payment endpoints
POST /api/x402/subscribe
POST /api/x402/verify
GET /api/x402/license/:wallet
```

## Statistics Example

```
Token Savings:
- Original: 3,425,000 tokens
- Compressed: 1,370,000 tokens
- Saved: 2,055,000 tokens (60%)

Cost Savings (30 days):
- Without optimizer: $10.28
- With optimizer: $4.11
- Savings: $6.17

Strategy Performance:
- Hybrid: 60% avg (800 uses)
- Summarization: 55% avg (250 uses)
- Pruning: 35% avg (47 uses)
- Deduplication: 25% avg (150 uses)
```

## Economic Rationale

**Should you upgrade to Pro?**

If you make enough API calls where 40-60% token savings exceed 0.5 USDT/month, **Pro tier pays for itself**.

**Typical savings:**
- Small projects: $2-5/month saved → $1.50-4.50 profit
- Medium projects: $10-20/month saved → $9.50-19.50 profit
- Large projects: $50+/month saved → $49.50+ profit

## Links

- [Documentation](README.md)
- [Agent Payments Guide](AGENT-PAYMENTS.md)
- [GitHub Repository](https://github.com/AtlasPA/openclaw-context-optimizer)
- [ClawHub Page](https://clawhub.ai/skills/context-optimizer)

---

**Built by the OpenClaw community** | First context optimizer with x402 payments
