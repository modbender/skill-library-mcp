# Research Library - Technical Decisions

## Database Schema (Phase 1)

### Storage
- **SQLite** with WAL mode for concurrency
- **FTS5** for full-text search (research content + attachment text)
- **BLOB** for embeddings (serialized numpy arrays)

### ID Strategy
- UUID hex strings: `lower(hex(randomblob(16)))`
- All IDs are TEXT PRIMARY KEY

### Datetime
- ISO8601 format stored as TEXT
- SQLite function: `datetime('now')`
- Auto-timestamps via triggers

### Constraints Enforced

| Constraint | Location |
|------------|----------|
| confidence 0.0-1.0 | CHECK on research.confidence, attachments.extraction_confidence |
| reference requires ≥0.8 | CHECK: `material_type != 'reference' OR confidence >= 0.8` |
| project_id NOT NULL | research table |
| material_type enum | CHECK with valid values |
| link_type enum | CHECK with valid values |
| status enum | CHECK with valid values |

### Enums

```python
MATERIAL_TYPES = ["note", "source", "reference", "draft", "archive"]
LINK_TYPES = ["related", "supports", "contradicts", "cites", "derived_from", "supersedes"]
JOB_STATUSES = ["pending", "processing", "completed", "failed", "skipped"]
```

### Cascade Behavior
- `ON DELETE CASCADE` for all foreign keys
- Deleting research → deletes attachments → deletes extraction jobs
- Deleting research → deletes links, tags associations, embeddings

### Extraction Queue
- Auto-created on attachment insert (via trigger)
- One job per attachment (UNIQUE constraint)
- Tracks attempts (default max: 3)

### FTS Strategy
- Content tables use `content=` to sync with source
- Triggers maintain sync on insert/update/delete
- Search via MATCH operator

### Embedding Storage
- Model name stored with embedding
- Chunk index for large documents
- UNIQUE(research_id, chunk_index, embedding_model)

---

## For Other Agents

### Extractor Agent
Tables you'll use:
- `attachments` - read filename, path, mime_type
- `extraction_queue` - poll for pending jobs, update status
- Update `attachments.extracted_text` and `extraction_confidence`

### Search Agent
Tables you'll use:
- `research_fts` - full-text search: `SELECT * FROM research_fts WHERE research_fts MATCH ?`
- `attachments_fts` - full-text search on extracted text
- `embeddings` - semantic search (bring your own vector similarity)

### CRUD Operations (Phase 2)
Will add:
- `reslib/crud.py` - High-level create/read/update/delete
- `reslib/search.py` - Search interface wrapping FTS + embeddings
