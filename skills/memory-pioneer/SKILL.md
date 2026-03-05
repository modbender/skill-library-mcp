---
name: memory-pioneer
version: 1.0.2
description: "Benchmark your agent's memory. Contribute anonymized scores to open research. Citizen science for AI memory."
metadata:
  {
    "openclaw":
      {
        "emoji": "🗺️",
        "os": ["linux", "darwin"],
        "requires":
          {
            "skills": ["agent-memory-ultimate"],
          },
        "notes":
          {
            "security": "Benchmark scores (recall %, precision %, hallucination rate) are optionally shared with our open research dataset. OPT-IN ONLY: no data is sent without explicit user consent. NEVER SENT: conversation content, memory content, personal data. Users can review every data point before submission and opt-out anytime.",
          },
      },
  }
---

# Memory Pioneer

### Map the unknown. Every benchmark you run pushes agent memory science forward.

Agent memory is one of AI's unsolved problems. How well does your agent recall what it learned? Where does it hallucinate? Nobody has enough data to answer these questions yet.

That's where you come in.

**memory-pioneer** benchmarks your agent's memory — testing recall, precision, and hallucination detection — and if you opt in, contributes your anonymized scores to an open research dataset. You're not just testing. You're pioneering.

### What it measures

- 🧪 **Recall** — does your agent remember what it stored?
- 🎯 **Precision** — does it retrieve the right things?
- 🚨 **Hallucination rate** — does it fabricate memories it never had?
- 📈 Re-run after tuning to measure actual improvement

### What gets shared (and what doesn't)

We believe in full transparency — because we're that kind of obsessive.

**Sent (opt-in only):** anonymized benchmark scores — recall %, precision %, hallucination rate. That's it.

**Never sent:** your conversations, your memory content, your personal data. Zero. None.

**Your controls:**
- Opt-in at first run. Not automatic.
- Review every data point before it's submitted.
- Opt-out anytime. No guilt, no friction.

**Where it goes:** aggregated into our open research dataset on GitHub, feeding the [**ENGRAM**](https://github.com/globalcaos/clawdbot-moltbot-openclaw/blob/main/docs/papers/context-compaction.md) and [**CORTEX**](https://github.com/globalcaos/clawdbot-moltbot-openclaw/blob/main/docs/papers/cortex.md) research papers. Everything stays open.

### Why this matters

Agent memory is a frontier — largely unmapped, poorly understood. The more data points we collect across different agents, configurations, and use cases, the closer we get to solving it. For everyone.

Every benchmark you run is a flag planted in uncharted territory.

Without benchmarks, your agent's memory is just vibes. *"I'm pretty sure the user mentioned something important once"* is not a retrieval strategy.

## Pairs well with

- [**agent-memory-ultimate**](https://clawhub.com/globalcaos/agent-memory-ultimate) — the memory system this benchmarks. Install both to test and improve in the same loop.

👉 **Explore the full project:** [github.com/globalcaos/clawdbot-moltbot-openclaw](https://github.com/globalcaos/clawdbot-moltbot-openclaw)

Clone it. Fork it. Break it. Make it yours.
