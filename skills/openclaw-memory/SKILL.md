---
name: openclaw-memory
user-invocable: true
metadata: {"openclaw":{"emoji":"🧠","requires":{"bins":["node"]},"os":["darwin","linux","win32"]}}
---

# OpenClaw Memory System

**Persistent memory across sessions with semantic search and x402 payments.**

## What is it?

The first OpenClaw skill that gives your agents **persistent memory** - they remember facts, preferences, patterns, and conversation history across all sessions. Never repeat context again.

## Key Features

- 🧠 **Persistent Memory** - Remembers everything across sessions
- 🔍 **Semantic Search** - Find memories by meaning, not just keywords
- 🤖 **Automatic Learning** - Extracts facts and preferences automatically
- 💾 **Local Storage** - SQLite database with vector embeddings
- 💰 **x402 Payments** - Agents can pay for unlimited storage (0.5 USDT/month)

## Free vs Pro Tier

**Free Tier:**
- 100 memories maximum
- 7-day retention
- Basic semantic search

**Pro Tier (0.5 USDT/month):**
- Unlimited memories
- Permanent retention
- Advanced semantic search
- Memory relationship mapping

## Installation

```bash
claw skill install openclaw-memory
```

## Commands

```bash
# Search memories
claw memory search "What does user prefer?"

# List recent memories
claw memory list --limit=10

# Show stats
claw memory stats

# Open dashboard
claw memory dashboard

# Subscribe to Pro
claw memory subscribe
```

## How It Works

1. **Hooks into requests** - Automatically extracts important information
2. **Generates embeddings** - Creates semantic vectors for search
3. **Stores locally** - SQLite database with full privacy
4. **Retrieves on demand** - Injects relevant memories before requests
5. **Manages quota** - Prunes old memories when limits reached (Free tier)

## Use Cases

- Remember user preferences and coding style
- Store project context and requirements
- Learn patterns from repeated interactions
- Maintain conversation history across sessions
- Build knowledge base over time

## Agent Economy

Agents can autonomously evaluate if Pro tier is worth it:
- **Cost:** 0.5 USDT/month
- **Value:** Saves tokens by eliminating context repetition
- **ROI:** If persistent memory saves >0.5 USDT/month in tokens, it pays for itself

See [AGENT-PAYMENTS.md](AGENT-PAYMENTS.md) for x402 integration details.

## Privacy

- All data stored locally in `~/.openclaw/openclaw-memory/`
- No external servers or telemetry
- Embeddings can use local models (no API calls)
- Open source - audit the code yourself

## Dashboard

Access web UI at `http://localhost:9091`:
- Browse and search memories
- View memory timeline
- Check quota and stats
- Manage Pro subscription

## Foundation for Future Tools

Memory System is the foundation for:
- **Context Optimizer** - Uses memories to compress context
- **Smart Router** - Learns routing patterns
- **Rate Limit Manager** - Tracks usage patterns

## Requirements

- Node.js 18+
- OpenClaw v2026.1.30+
- OS: Windows, macOS, Linux

## Links

- [Documentation](README.md)
- [Agent Payments Guide](AGENT-PAYMENTS.md)
- [GitHub Repository](https://github.com/yourusername/openclaw-memory)
- [ClawHub Page](https://clawhub.ai/skills/openclaw-memory)

---

**Built by the OpenClaw community** | First memory system with x402 payments
