---
name: percept-summarize
description: Automatic conversation summaries with entity extraction and
  relationship mapping.
---

# percept-summarize

Automatic conversation summaries with entity extraction and relationship mapping.

## What it does

When a conversation ends (60 seconds of silence), Percept generates an AI-powered summary with extracted entities (people, companies, topics), action items, and relationship connections. Summaries are stored locally and searchable.

## When to use

- User asks "what did we talk about?" or "summarize that meeting"
- User wants meeting notes or action items from a conversation
- Agent needs context from a recent conversation

## Requirements

- **percept-listen** skill installed and running
- **OpenClaw agent** accessible via CLI (used for LLM summarization)

## How it works

1. Conversation ends (60s silence timeout)
2. Percept builds a speaker-tagged transcript
3. Sends transcript to OpenClaw for AI summarization
4. Extracts entities (people, orgs, topics) and relationships
5. Stores summary + entities in SQLite
6. Entities linked via relationship graph (works_on, client_of, mentioned_with)

## Entity resolution

5-tier cascade for identifying entities:
1. **Exact match** (confidence 1.0)
2. **Fuzzy match** (0.8) — handles typos, nicknames
3. **Contextual/graph** (0.7) — uses relationship connections
4. **Recency** (0.6) — recently mentioned entities ranked higher
5. **Semantic search** (0.5) — vector similarity via LanceDB

## Querying summaries

Summaries are searchable via the Percept dashboard (port 8960) or SQLite directly:

```sql
SELECT * FROM conversations WHERE summary LIKE '%action items%' ORDER BY end_time DESC;
```

Full-text search via FTS5:
```sql
SELECT * FROM utterances_fts WHERE utterances_fts MATCH 'project deadline';
```

## Data retention

- Utterances: 30 days
- Summaries: 90 days
- Relationships: 180 days
- Speaker profiles: never expire

## Links

- **GitHub:** https://github.com/GetPercept/percept
