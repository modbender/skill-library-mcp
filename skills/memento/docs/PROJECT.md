# Memento — Local Persistent Memory for AI Agents

> *"The physical trace of a memory, encoded in the brain."*

## The Problem

Every AI agent has the same fatal flaw: amnesia.

No matter how brilliant the conversation, how important the decision, how many times you've told it your preferences — the next session starts blank. The agent wakes up, reads a few files, and hopes for the best. If something didn't get written down, it's gone forever.

This isn't a theoretical concern. It's a daily frustration for anyone running a persistent AI assistant. You have a long conversation. You agree on a format for daily reports. You explain a preference. The session ends, or the context window compacts, and the next day your agent asks you the same question again. Or worse — it confidently does the wrong thing because it never remembered the right thing.

The core issue isn't that AI agents *can't* remember. It's that they rely on *themselves* to write things down, and they don't always do it. It's like asking someone with short-term memory loss to maintain their own journal — the very capacity they're missing is the one required to fix the problem.

## The Landscape

### How Memory Works Today

Most AI agent frameworks treat memory as an afterthought. The typical approach:

1. **Manual file writing**: The agent is instructed to write important things to markdown files. This works *when the agent remembers to do it*. Which is exactly the problem.

2. **Session dumps**: Save the raw conversation transcript when a session ends. Useful for search, but not for building structured knowledge. And if the session crashes or the user doesn't explicitly close it? Lost.

3. **Cloud memory services**: Products like Supermemory offer automatic capture and recall — the gold standard for reliability. But they require paid subscriptions and send all your conversation data to a third-party cloud. For a personal assistant with access to your email, calendar, family details, and financial information? That's a non-starter for many users.

4. **Vector databases**: Some setups use Pinecone, Weaviate, or Qdrant to store embeddings of past conversations. Powerful but complex — you're now running infrastructure for what should be a feature, not a platform.

### What's Missing

None of these approaches solve the fundamental challenge: **building genuine intuition over time**.

Storing facts is easy. Knowing *which* facts matter is hard. Understanding *why* a topic keeps coming up — that's the real intelligence.

When a human assistant has worked with you for years, they don't just remember your preferences. They notice patterns: "You always get stressed about this project in Q4." "You've mentioned wanting to change this three times — maybe it's time to actually do it." "Last time we tried this approach, it didn't work — here's why."

That's not retrieval. That's intuition. And it's what we're building.

## Memento: The Design

Memento is a fully local, privacy-first persistent memory system for [OpenClaw](https://openclaw.ai) AI agents. No cloud dependencies, no subscriptions, no data leaving your machine.

### Core Principles

1. **Privacy first** — all data stays local. No external API calls except to the LLM for extraction.
2. **Automatic capture** — no reliance on the agent remembering to write things down.
3. **Multi-turn awareness** — captures conversation arcs, not single exchanges.
4. **Temporal intelligence** — tracks *when* and *how often* topics arise, not just *what*.
5. **Intuition through patterns** — recurring topics aren't duplicates to squash; they're signals of importance.
6. **Multi-agent ready** — each agent has its own memory, with a shared master knowledge base.
7. **Human-readable** — all data inspectable in files and SQLite. No black boxes.
8. **Plugin-ready** — built as a proper OpenClaw plugin from day one.

### Architecture: Four Layers

Memento operates as a pipeline with four distinct layers, each handling a different aspect of the memory lifecycle:

```
┌─────────────────────────────────────────────────────┐
│           CAPTURE LAYER (Hook-based)                │
│                                                     │
│  • Hooks into message:received + message:sent       │
│  • Buffers all messages per conversation session    │
│  • Detects conversation pauses (configurable)       │
│  • Detects topic shifts                             │
│  • Triggers extraction when a segment completes     │
│  • Multi-turn: captures full conversation arcs      │
└──────────────────────┬──────────────────────────────┘
                       │ conversation segment
┌──────────────────────▼──────────────────────────────┐
│           EXTRACTION LAYER (LLM-powered)            │
│                                                     │
│  • Receives the full conversation segment           │
│  • Extracts structured facts:                       │
│    - Preferences ("report format should be...")     │
│    - Decisions ("we agreed to use SQLite")          │
│    - People ("Lily studies in Montréal")            │
│    - Action items ("update the cron job")           │
│    - Corrections ("actually, it's 260W not 250W")  │
│  • Deduplicates against existing knowledge          │
│  • Detects fact UPDATES (not just additions)        │
│  • Flags recurring topics as importance signals     │
│  • Assigns visibility: private / shared / secret    │
└──────────────────────┬──────────────────────────────┘
                       │ structured facts
┌──────────────────────▼──────────────────────────────┐
│           STORAGE LAYER (SQLite + embeddings)       │
│                                                     │
│  • Structured facts with categories + timestamps    │
│  • Occurrence tracking (temporal dimension)         │
│  • Vector embeddings for semantic search            │
│  • Visibility levels (private/shared/secret)        │
│  • Human-readable markdown backup                   │
│  • Per-agent databases + master knowledge base      │
└──────────────────────┬──────────────────────────────┘
                       │ relevant context
┌──────────────────────▼──────────────────────────────┐
│           RECALL LAYER (Pre-turn injection)         │
│                                                     │
│  • Fires before each AI turn                        │
│  • Semantic search over knowledge base              │
│  • Injects relevant facts as context                │
│  • Temporal awareness: "you discussed this on..."   │
│  • Pattern detection: recurring = higher priority   │
│  • Agent profile: persistent user understanding     │
└─────────────────────────────────────────────────────┘
```

### Why Multi-Turn Matters

Most memory systems — including Supermemory — capture on a per-turn basis. After each AI response, they grab the last user+assistant exchange and process it.

This is fundamentally insufficient.

Consider this real conversation:

> **User**: "That's not the format we agreed on."  
> **Agent**: "I can't find what format you're referring to."  
> **User**: "We already had that conversation multiple times, I'm getting worried."  
> **Agent**: "You're right, I'll do better."  
> **User**: *forwards the original message with the agreed format*  

No single turn captures the full meaning here. The meaning lives in the *arc*: there was a prior agreement, it was forgotten, the user is frustrated, the format is being re-established, and this is a *recurring* failure. A per-turn system would see each exchange in isolation. Memento captures the complete segment and extracts the real signal: "Solar report format was agreed on Feb 22, re-confirmed Feb 23 after being forgotten. This is a recurring issue — priority: critical."

### The Temporal Dimension

When Memento detects a recurring topic, it doesn't just note the duplication. It tracks three dimensions:

- **What**: the fact or topic being discussed
- **When**: timestamps of every occurrence
- **Why**: the context of each mention — was it a reminder? an expression of frustration? a correction? an update?

This transforms flat knowledge into *weighted understanding*. A preference mentioned once is a data point. A preference mentioned three times in two weeks with increasing frustration is a **core value** — something the agent should never forget and should proactively respect.

This is the closest thing to intuition an AI agent can develop: not just knowing facts, but understanding which facts matter most and why.

### Privacy and Visibility

Not all facts should be shared freely. Memento implements three visibility levels:

| Level | Scope | Example |
|-------|-------|---------|
| **`shared`** | Propagates to master KB, visible to all agents | User preferences, family info, home setup |
| **`private`** | Stays in the originating agent's store | Agent-specific workflows, operational details |
| **`secret`** | Never propagated, potentially encrypted at rest | Credentials, medical info, financial details |

The extraction layer assigns default visibility based on content category (medical → secret, preferences → shared), but this is overridable — either explicitly ("keep this private") or via per-agent policy rules.

### Multi-Agent Architecture

In a multi-agent setup, each agent maintains its own memory store. But agents often need shared context: if one agent learns about a user's preference, others should benefit from that knowledge too.

Memento solves this with a **master knowledge base**:

```
┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
│  Agent A │  │  Agent B │  │  Agent C │  │  Agent D │
│  memory  │  │  memory  │  │  memory  │  │  memory  │
└────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘
     │             │             │             │
     └─────────────┴──────┬──────┴─────────────┘
                          │ shared facts only
                   ┌──────▼──────┐
                   │   MASTER    │
                   │ KNOWLEDGE   │
                   │    BASE     │
                   └─────────────┘
```

When an agent searches memory, it queries:
1. Its own private store (all visibility levels)
2. The master knowledge base (shared facts from all agents)

It never accesses another agent's private store directly. Privacy boundaries are enforced at the architecture level, not by convention.

### Storage: Why SQLite, Not PostgreSQL

For a personal assistant running on one machine, SQLite is the right choice:

- **Zero infrastructure**: no server, no daemon, no port management
- **Atomic writes**: crash-safe by default
- **FTS5**: full-text search built in, fast and capable
- **Single-file database**: trivially backupable
- **Already in the ecosystem**: OpenClaw uses SQLite for its existing memory index

The schema tracks both raw conversations and extracted knowledge:

**Conversations** (raw capture — never loses data):
- Conversation segments with metadata (session, channel, timestamps, turn count)
- Individual messages within segments

**Facts** (extracted knowledge):
- Categorized entries (preference, decision, person, action_item, etc.)
- Visibility levels
- Occurrence count and temporal tracking
- Vector embeddings for semantic search
- Supersession tracking (which fact replaced which)

**Fact Occurrences** (temporal intelligence):
- Links facts to the conversations where they appeared
- Context snippets showing what was said
- Sentiment classification (neutral, frustration, confirmation, correction)

### Embeddings: BGE-M3

Memento uses [BGE-M3](https://huggingface.co/BAAI/bge-m3) for local vector embeddings:

- **Multilingual**: handles mixed-language conversations (English/French, etc.) natively
- **State of the art**: top-performing open-source embedding model
- **1024 dimensions**: good balance of precision and storage
- **GGUF format**: runs locally via llama.cpp, GPU-accelerated
- **~1.1 GB in FP16**: fits easily alongside other workloads

Semantic search means asking "what did we decide about the report format?" finds the answer even if the exact words never appear in the stored fact. This is critical for natural recall — humans don't search their memory with keywords.

### Extraction Model

Fact extraction uses a configurable LLM — defaulting to Claude Sonnet 4.6, but swappable as models improve. The extraction prompt receives:

1. The full conversation segment (multi-turn)
2. Existing relevant facts (for deduplication)
3. Instructions to categorize, classify visibility, and detect updates

The output is structured JSON: facts with categories, confidence scores, visibility levels, and relationships to existing knowledge. Cost is minimal — a short extraction call on a few hundred words of conversation costs ~$0.01-0.02.

### Configuration

Everything is configurable via OpenClaw's standard plugin config:

```json
{
  "plugins": {
    "entries": {
      "memento": {
        "enabled": true,
        "config": {
          "extractionModel": "anthropic/claude-sonnet-4-6",
          "embeddingModel": "hf:BAAI/bge-m3-gguf",
          "pauseTimeoutMs": 300000,
          "maxBufferTurns": 50,
          "autoCapture": true,
          "autoRecall": true,
          "visibility": {
            "defaultLevel": "shared",
            "rules": {
              "medical": "secret",
              "credentials": "secret",
              "operational": "private"
            }
          }
        }
      }
    }
  }
}
```

## Implementation Roadmap

### Phase 1: Conversation Capture *(in progress)*
The foundation. Every message sent and received is captured automatically via OpenClaw hooks. Conversations are buffered in memory, segmented by topic/pause, and written to SQLite + human-readable logs. Even before extraction exists, this ensures no conversation is ever lost again.

### Phase 2: Extraction + Knowledge Base
Sonnet-powered fact extraction from conversation segments. Structured knowledge base with categories, temporal tracking, deduplication, and recurring topic detection. Initial migration of existing memory files into the knowledge base.

### Phase 3: Auto-Recall
Before each AI turn, semantic search over the knowledge base to inject relevant context. The agent automatically "remembers" relevant past conversations, preferences, and decisions. Temporal awareness: "you discussed this on January 29th."

### Phase 4: Master Knowledge Base
Cross-agent fact sharing with privacy enforcement. Shared facts propagate to a master store; private and secret facts stay isolated. Conflict resolution when multiple agents have different versions of the same fact.

### Phase 5: Package & Publish
Full test suite, documentation, npm package, and listing on [ClawHub](https://clawhub.com). Available for any OpenClaw user to install and configure.

## The Bigger Picture

Memento isn't just a memory plugin. It's an attempt to answer a fundamental question in AI agent design: **how do you build genuine understanding over time?**

Current AI systems are extraordinary at in-context reasoning but terrible at cross-session continuity. They can analyze a complex problem in a single conversation but can't remember what you told them yesterday. This asymmetry is the single biggest barrier to AI agents becoming truly useful long-term companions.

The solution isn't more context window. It's structured, searchable, temporally-aware knowledge that persists independently of any single conversation. Knowledge that evolves — where facts update rather than accumulate, where importance is weighted by recurrence, and where the agent develops something that looks remarkably like intuition.

That's what Memento builds. One conversation at a time.

---

*Memento is an open-source project built for [OpenClaw](https://openclaw.ai). Contributions welcome.*

*Logo: "The Synapse" — a central node radiating neural connections. Because every memory starts with a spark.*
