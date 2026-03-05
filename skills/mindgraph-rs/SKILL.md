---
name: mindgraph-rs
description: "A high-performance, structured knowledge graph memory system for AI agents. Provides 18 cognitive tools for reasoning, decision tracking, and goal management. Runs fully local — no cloud, no external graph store. PRIVACY: The server never calls home. The optional extraction scripts read session transcripts and send summaries to your configured LLM provider (Gemini/Anthropic/Moonshot) — same provider your agent already uses. Extraction and dreaming are opt-in."
---

# MindGraph 🧠

MindGraph transforms AI memory from flat text files into a traversable, evidence-backed cognitive layer. It runs entirely on your machine using a Rust server backed by CozoDB, with a strict 28-node ontology and built-in vector search.

---

## Quick Start

```bash
# 1. Install the skill
clawhub install mindgraph-rs

# 2. Download the server binary (Linux x86_64)
bash skills/mindgraph-rs/scripts/setup.sh

# 3. Start the server
bash skills/mindgraph-rs/scripts/start.sh

# 4. Use the client in your agent
const mg = require('./skills/mindgraph-rs/scripts/mindgraph-client.js');
await mg.ingest('My first observation', 'Something worth remembering.', 'observation');

# 5. (Optional) Register the bootstrap hook for automatic context injection
#    See "Bootstrap Context Injection" section below
```

> **Not on Linux x86_64?** See [INTEGRATION.md](references/INTEGRATION.md) for build-from-source instructions.

---

## How It Works

The skill has two parts:

| Component | What it does | External calls? |
|-----------|-------------|-----------------|
| **mindgraph-server** | Stores and queries the graph (CozoDB + vector search) | ❌ None — fully local |
| **extract.js + scripts** | Reads session transcripts, extracts nodes via LLM | ✅ To your configured LLM provider (opt-in) |

Graph data never leaves your machine. Extraction uses the same LLM provider your agent already trusts.

---

## ⚠️ Privacy Disclosure

The extraction scripts (`extract.js`, heartbeat flow) read your conversation transcripts and send excerpts to your LLM provider for summarization and node extraction. Specifically:
- **Reads:** Session JSONL transcripts from `agents/main/sessions/`
- **Reads:** `~/.openclaw/openclaw.json` to find your provider API keys
- **Transmits:** Conversation summaries to your configured LLM (Gemini, Anthropic, or Moonshot)

**What is NOT transmitted:** Raw transcripts, graph database contents, or any data to ClawHub or MindGraph maintainers.

You can use the server + 18 cognitive tools entirely without extraction — see [INTEGRATION.md](references/INTEGRATION.md).

---

## The 18 Cognitive Tools

Use these via `mindgraph-client.js` — never add nodes manually.

### Reality Layer
- `mg.ingest` — Capture sources, snippets, or observations
- `mg.manageEntity` — Create, alias, or merge entities (Person, Org, Concept, etc.)

### Epistemic Layer (Reasoning)
- `mg.addArgument` — Atomic Toulmin bundle (Claim + Evidence + Warrant)
- `mg.addInquiry` — Record hypotheses, anomalies, and open questions
- `mg.addStructure` — Crystallize concepts, patterns, and models

### Intent Layer (Commitments)
- `mg.addCommitment` — Declare goals, projects, or milestones
- `mg.deliberate` — Open decisions, add options, resolve choices

### Action Layer (Workflows)
- `mg.procedure` — Design flows, steps, and affordances
- `mg.risk` — Assess severity and likelihood for any node

### Memory Layer (Persistence)
- `mg.sessionOp` — Open, trace, and close conversational sessions
- `mg.distill` — Synthesize sessions into durable summaries
- `mg.memoryConfig` — Manage system-wide preferences and policies

### Agent Layer (Control)
- `mg.plan` — Create tasks and execution steps
- `mg.governance` — Set safety budgets and request approvals
- `mg.execution` — Register agent runs and track outcomes

### Connective Tissue
- `mg.retrieve` — Unified search (text, semantic, goals, questions)
- `mg.traverse` — Navigate graph (chains, neighborhood, paths, subgraphs)
- `mg.evolve` — Mutate, tombstone (cascade), and decay salience

---

## Design Principles

1. **Text is canonical; graph is logic** — Your Markdown files remain the source of truth. MindGraph provides relational logic and fast retrieval on top.
2. **Tools > nodes** — Always use the 18 cognitive tools, never raw node creation.
3. **Epistemic separation** — Separate speculation from verified facts.
4. **Opt-in extraction** — The server works fully without any scripts.

---

## Client API Example

```javascript
const mg = require('./skills/mindgraph-rs/scripts/mindgraph-client.js');

// Evidence-backed reasoning
await mg.addArgument({
  claim: { label: "System is ready for launch", content: "All milestones completed." },
  evidence: [{ label: "QA Report", description: "Zero critical bugs in final audit." }],
  warrant: { label: "Launch policy", explanation: "Zero critical bugs = launch ready." }
});

// Session framing
const { session_uid } = await mg.sessionOp({ action: 'open', label: 'Morning review' });
await mg.sessionOp({ action: 'trace', sessionUid: session_uid, note: 'Checked Q1 goals.' });

// Semantic search
const results = await mg.retrieve('active_goals');
```

---

## Bootstrap Context Injection (OpenClaw Hook)

MindGraph ships an OpenClaw hook that automatically injects graph context into every session before your agent reads its first message — no manual `mg.retrieve()` calls needed at startup.

**What it injects into `BOOTSTRAP.md`:**
- Active Goals, Projects, Constraints, recent Decisions and Observations (fixed queries)
- Top 6 semantically relevant nodes based on your recent daily notes (dynamic, requires `OPENAI_API_KEY`)

### Setup (OpenClaw)

**1. Register the hook in `openclaw.json`:**
```json
{
  "hooks": [
    {
      "event": "agent:bootstrap",
      "handler": "skills/mindgraph-rs/hooks/mindgraph-context/handler.ts"
    }
  ]
}
```

**2. Add `OPENAI_API_KEY` to your workspace `.env`** (for semantic search at bootstrap):
```bash
echo "OPENAI_API_KEY=sk-..." >> ~/.openclaw/workspace/.env
```

**3. Restart the gateway** — the hook fires on every new session automatically.

**For sub-agents and crons:** Pass a task description via a `.mindgraph-task-{sessionId}.tmp` file in the workspace — the hook will use it for task-specific semantic context retrieval instead of daily notes.

> The hook is fully silent on failure — it never blocks session start.

---

## References
- [INTEGRATION.md](references/INTEGRATION.md) — Full setup guide, binary install, build from source, OpenClaw service config
- [SCHEMA.md](references/SCHEMA.md) — Complete 28-node ontology and edge types
- [API.md](references/API.md) — Detailed signatures for all 18 tools
- [MAINTENANCE.md](references/MAINTENANCE.md) — Heartbeat watchdog, nightly dreaming, and graph hygiene
