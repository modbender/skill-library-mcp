---
name: agent-memory-ultimate
version: 3.1.0
description: "Give your OpenClaw agent a memory system that actually works across sessions. Research-backed. Open source."
metadata:
  {
    "openclaw":
      {
        "emoji": "🧠",
        "os": ["linux", "darwin"],
        "requires":
          {
            "bins": ["sqlite3"],
          },
        "notes":
          {
            "security": "This skill stores memories in a local SQLite database. All data stays on your machine. No cloud calls, no external APIs, no data exfiltration. Vector embeddings are computed locally. Memory consolidation and decay run as local processes.",
          },
      },
  }
---

# Agent Memory Ultimate

### Your agent forgets everything. Let's fix that.

You spend 20 minutes explaining your architecture. Next session: *"Could you remind me what we're working on?"*

You decide on PostgreSQL over MongoDB with detailed reasoning. After compaction: *"What database are you using?"*

You tell it your wife's name is Sasha. Three sessions later it calls her Sarah.

This isn't a bug. This is vanilla OpenClaw — context fills up, compaction kicks in, thread lost. Every. Single. Time.

### What we built

A memory skill that makes your agent *significantly* better at retaining what matters. Not perfect — that's still an unsolved problem in AI — but good enough that it stops asking "what project?" for the third time this week.

- **Semantic vector search** — finds relevant context even when you phrase things differently
- **Two-tier index** — fast retrieval instead of scanning 50KB of logs
- **Automatic consolidation** — decisions, preferences, and facts persist across sessions
- **Natural memory decay** — old irrelevant stuff fades, recent memories surface faster
- **60–80% token savings** — loads only what's relevant instead of dumping everything into context
- **SQLite-backed** — everything local, everything persistent, survives restarts
- **Fully offline** — no cloud, no API calls, no data leaving your machine

We didn't guess at the architecture. It's backed by two research papers:

- [**HIPPOCAMPUS**](https://github.com/globalcaos/clawdbot-moltbot-openclaw/blob/main/docs/papers/hippocampus.md) — biologically-inspired memory formation with O(1) concept lookup
- [**ENGRAM**](https://github.com/globalcaos/clawdbot-moltbot-openclaw/blob/main/docs/papers/context-compaction.md) — context compaction as cache eviction, not summarization. Summarization destroys detail. Cache eviction preserves it.

Because we're that kind of obsessive.

### What you get

An agent that remembers your tech stack, your preferences, your team's names, and the decisions you already made — without you repeating yourself every session. It's not omniscient. But it's a dramatic improvement over the default.

## Pairs well with

- [**jarvis-voice**](https://clawhub.com/globalcaos/jarvis-voice) — Memory that speaks back
- [**ai-humor-ultimate**](https://clawhub.com/globalcaos/ai-humor-ultimate) — An agent that remembers *and* has personality
- [**agent-boundaries-ultimate**](https://clawhub.com/globalcaos/agent-boundaries-ultimate) — Perfect memory with clear limits on when to use it

👉 **Explore the full project:** [github.com/globalcaos/clawdbot-moltbot-openclaw](https://github.com/globalcaos/clawdbot-moltbot-openclaw)

Clone it. Fork it. Break it. Make it yours.
