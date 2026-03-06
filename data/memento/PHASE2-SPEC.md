# Phase 2: Extraction + Knowledge Base

## Overview
Add LLM-powered fact extraction from captured conversation segments, and a structured knowledge base with temporal tracking.

## What to Build

### 1. SQLite Schema Extension (`src/storage/schema.ts`)
Add Phase 2 tables to the existing schema:

```sql
-- Extracted facts
CREATE TABLE IF NOT EXISTS facts (
  id TEXT PRIMARY KEY,
  agent_id TEXT NOT NULL,
  category TEXT NOT NULL, -- preference, decision, person, action_item, correction, technical, etc.
  content TEXT NOT NULL,
  summary TEXT, -- one-line summary
  visibility TEXT NOT NULL DEFAULT 'shared', -- private, shared, secret
  confidence REAL DEFAULT 1.0,
  first_seen_at INTEGER NOT NULL,
  last_seen_at INTEGER NOT NULL,
  occurrence_count INTEGER DEFAULT 1,
  supersedes TEXT, -- ID of fact this updates/replaces
  is_active INTEGER DEFAULT 1, -- 0 if superseded
  metadata TEXT -- JSON
);

-- Fact occurrences (temporal tracking)
CREATE TABLE IF NOT EXISTS fact_occurrences (
  id TEXT PRIMARY KEY,
  fact_id TEXT NOT NULL REFERENCES facts(id),
  conversation_id TEXT NOT NULL REFERENCES conversations(id),
  timestamp INTEGER NOT NULL,
  context_snippet TEXT, -- what was said around this mention
  sentiment TEXT -- neutral, frustration, confirmation, correction, update
);

-- Extraction log (track what's been processed)
CREATE TABLE IF NOT EXISTS extraction_log (
  conversation_id TEXT PRIMARY KEY REFERENCES conversations(id),
  extracted_at INTEGER NOT NULL,
  model_used TEXT NOT NULL,
  facts_extracted INTEGER DEFAULT 0,
  facts_updated INTEGER DEFAULT 0,
  facts_deduplicated INTEGER DEFAULT 0,
  error TEXT -- null if successful
);
```

Add indexes on `facts.category`, `facts.agent_id`, `facts.visibility`, `fact_occurrences.fact_id`.

### 2. Extraction Engine (`src/extraction/extractor.ts`)
Core extraction logic:

- Takes a conversation segment (from the `conversations` table)
- Fetches existing relevant facts from the DB (for deduplication context)
- Calls the configured LLM (default: Sonnet 4.6) with an extraction prompt
- Parses the structured JSON response
- Returns an array of extracted facts

**LLM Call**: Use the OpenClaw API to call the configured model. The plugin API provides:
```typescript
// api.runtime should have an LLM call method, but if not available,
// use a direct HTTP call to the Anthropic API via the configured provider.
// For now, use Node's native fetch to call the Anthropic Messages API.
// The API key should come from the environment (ANTHROPIC_API_KEY).
```

Actually, the simplest approach: use `child_process.execSync` to run:
```bash
openclaw chat --model <model> --message "<prompt>" --json
```

Or better: use the Node.js `fetch` API to call Anthropic directly. The API key is available in the environment.

**Extraction Prompt Design** (critical):
```
You are a memory extraction system. Analyze this conversation segment and extract structured facts.

For each fact, provide:
- category: one of [preference, decision, person, action_item, correction, technical, routine, emotional]
- content: the full fact description
- summary: one-line summary (max 100 chars)
- visibility: one of [private, shared, secret]
  - shared: user preferences, family info, general knowledge (default)
  - private: agent-specific operational details
  - secret: credentials, medical info, financial details
- confidence: 0.0-1.0 how certain this is a real fact
- sentiment: one of [neutral, frustration, confirmation, correction, update]

EXISTING FACTS (check for duplicates/updates):
<existing_facts_json>

CONVERSATION:
<conversation_text>

Rules:
1. If a fact UPDATES an existing fact, set supersedes=<existing_fact_id> and note what changed
2. If a fact is a DUPLICATE of an existing fact, note it with duplicate_of=<existing_fact_id> and increment_occurrence=true
3. Extract DECISIONS and AGREEMENTS explicitly — these are high priority
4. Note recurring topics — if something was discussed before, flag it
5. Don't extract trivial exchanges ("hi", "thanks", "ok")
6. For preferences, be specific: "solar report format: emoji headers, import/export breakdown with costs"
7. For people, capture relationships: "Alice is the user's best friend, partner Carol"

Return JSON array of facts.
```

### 3. Deduplication Engine (`src/extraction/deduplicator.ts`)
- Before inserting new facts, check for semantic similarity with existing facts
- If a fact is essentially the same: increment occurrence_count, update last_seen_at, add to fact_occurrences
- If a fact UPDATES an existing one: create new fact with supersedes reference, mark old as inactive
- If a fact is genuinely new: insert normally
- **Key insight**: duplicate detection is a SIGNAL, not just cleanup. Track it in fact_occurrences with context.

### 4. Visibility Classifier (`src/extraction/classifier.ts`)
- Default rules based on category:
  - medical → secret
  - credentials/passwords/tokens → secret
  - operational/workflow → private
  - everything else → shared
- Content-based heuristics (keywords like "password", "token", "diagnosis")
- Configurable override rules from plugin config

### 5. Database Operations (`src/storage/db.ts`)
Add methods to ConversationDB:
- `getUnextractedConversations()` — conversations not in extraction_log
- `getRelevantFacts(agentId, limit)` — active facts for context
- `insertFact(fact)` — insert a new fact
- `updateFactOccurrence(factId, conversationId, context, sentiment)` — add occurrence
- `supersedeFact(oldId, newFact)` — mark old inactive, insert new
- `logExtraction(conversationId, result)` — record extraction attempt
- `getFactsByCategory(agentId, category)` — for recall
- `searchFacts(agentId, query)` — text search via FTS5

### 6. FTS5 Full-Text Search
Add FTS5 virtual table for fact content search:
```sql
CREATE VIRTUAL TABLE IF NOT EXISTS facts_fts USING fts5(
  content, summary, 
  content=facts, content_rowid=rowid
);
```
With triggers to keep it in sync.

### 7. Extraction Trigger (`src/extraction/trigger.ts`)
- Hook into the capture layer: after a segment is written, queue it for extraction
- Run extraction asynchronously (don't block the message flow)
- Respect rate limits (configurable max extractions per minute)
- Skip very short segments (< 3 turns by default, configurable)

### 8. Initial Migration (`src/extraction/migrate.ts`)
- One-time script to process existing memory/*.md files
- Read each file, create a synthetic "conversation" from its content
- Run extraction on each to populate the knowledge base
- This gives us a "warm start" with all existing knowledge

## Configuration Additions
```json
{
  "extraction": {
    "minTurnsForExtraction": 3,
    "maxExtractionsPerMinute": 10,
    "includeExistingFactsCount": 50,
    "autoExtract": true
  }
}
```

## Technical Constraints
- Use Node's native `fetch` for Anthropic API calls (no extra deps)
- The Anthropic API key comes from environment: `process.env.ANTHROPIC_API_KEY`
- All extraction is async and must never block message capture
- Extraction errors should be logged but never crash the plugin
- Use the model from config (`extractionModel` field, default "anthropic/claude-sonnet-4-6")
- Parse the model string: if it starts with "anthropic/", use the Anthropic Messages API
- Model name mapping: "anthropic/claude-sonnet-4-6" → API model "claude-sonnet-4-6"

## What NOT to Build Yet
- Embeddings / vector search (Phase 2b or Phase 3)
- Auto-recall injection (Phase 3)
- Master knowledge base (Phase 4)
- Migration script for existing memory files (defer to after core works)

## File Structure
```
src/extraction/
├── extractor.ts      # LLM-based fact extraction
├── deduplicator.ts   # Fact dedup + recurrence detection  
├── classifier.ts     # Visibility level assignment
└── trigger.ts        # Extraction trigger (post-capture hook)
```
