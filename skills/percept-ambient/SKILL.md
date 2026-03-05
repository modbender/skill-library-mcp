# percept-ambient

Ambient intelligence mode — continuous context awareness without explicit commands.

## What it does

Runs in the background, building a knowledge graph of conversations, entities, and relationships over time. Your agent passively learns context from ambient speech — who you talk to, what projects are active, what decisions were made — without needing explicit commands.

## When to use

- User wants always-on context awareness
- Agent needs background knowledge from daily conversations
- User asks "what do you know about [person/project]?" based on overheard context

## Requirements

- **percept-listen** skill installed and running
- **percept-summarize** skill installed (for entity extraction)

## How it works

1. All conversations are continuously captured and summarized
2. Entities (people, companies, projects, topics) extracted automatically
3. Relationships mapped between entities (works_on, client_of, mentioned_with)
4. Context packets assembled on demand for any agent action
5. Full-text search (FTS5) + vector search (LanceDB) for retrieval

## Context packets

When your agent needs context, Percept assembles a Context Packet:

```json
{
  "recent_conversations": [...],
  "resolved_entities": [...],
  "relationships": [...],
  "relevant_history": [...]
}
```

This gives the agent rich situational awareness without loading entire conversation histories.

## Vector search

Semantic search over utterances using NVIDIA NIM embeddings (primary) with all-MiniLM-L6-v2 as offline fallback. Stored in LanceDB (local, zero-infra).

```bash
# Search via dashboard (port 8960) or API
curl localhost:8960/api/search?q=project+deadline&mode=hybrid
```

## Privacy controls

- All data stored locally in SQLite + LanceDB
- TTL auto-purge (configurable retention periods)
- No audio stored — only transcripts
- Dashboard → Settings → Privacy for granular controls

## Real-time dashboard

Monitor ambient intelligence at `http://localhost:8960`:
- Live conversation feed
- Entity graph visualization
- Search across all conversations
- Analytics and usage stats

## Links

- **GitHub:** https://github.com/GetPercept/percept
