---
name: qdrant-advanced
version: 1.0.0
description: "Advanced Qdrant vector database operations for AI agents. Semantic search, contextual document ingestion with chunking, collection management, snapshots, and migration tools. Production-ready scripts for the complete Qdrant lifecycle. Use when: (1) Implementing semantic search across collections, (2) Ingesting documents with intelligent chunking, (3) Managing collections programmatically, (4) Creating backups and migrations."
metadata:
  openclaw:
    requires:
      bins: ["curl", "python3", "bash"]
      env: ["QDRANT_HOST", "QDRANT_PORT", "OPENAI_API_KEY"]
      config: []
    user-invocable: true
  homepage: https://github.com/yoder-bawt
  author: yoder-bawt
---

# Qdrant Advanced

Production-ready Qdrant vector database operations for AI agents. Complete toolkit for semantic search, document ingestion, collection management, backups, and migrations.

## Quick Start

```bash
# Set environment variables
export QDRANT_HOST="localhost"
export QDRANT_PORT="6333"
export OPENAI_API_KEY="sk-..."

# List collections
bash manage.sh list

# Create a collection
bash manage.sh create my_collection 1536 cosine

# Ingest a document
bash ingest.sh /path/to/document.txt my_collection paragraph

# Search
bash search.sh "my search query" my_collection 5
```

## Scripts Overview

| Script | Purpose | Key Features |
|--------|---------|--------------|
| `search.sh` | Semantic search | Multi-collection, filters, score thresholds |
| `ingest.sh` | Document ingestion | Contextual chunking, batch upload, progress |
| `manage.sh` | Collection management | Create, delete, list, info, optimize |
| `backup.sh` | Snapshots | Full collection snapshots, restore, list |
| `migrate.sh` | Migrations | Collection-to-collection, embedding model upgrades |

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `QDRANT_HOST` | No | `localhost` | Qdrant server hostname |
| `QDRANT_PORT` | No | `6333` | Qdrant server port |
| `OPENAI_API_KEY` | Yes* | - | OpenAI API key for embeddings |
| `QDRANT_API_KEY` | No | - | Qdrant API key (if auth enabled) |

*Required for ingest and search operations

## Detailed Usage

### Semantic Search

```bash
bash search.sh <query> <collection> [limit] [filter_json]
```

**Examples:**

```bash
# Basic search
bash search.sh "machine learning tutorials" my_docs 10

# With metadata filter
bash search.sh "deployment guide" my_docs 5 '{"must": [{"key": "category", "match": {"value": "devops"}}]}'

# Score threshold
bash search.sh "error handling" my_docs 10 "" 0.8
```

**Output:**
```json
{
  "results": [
    {
      "id": "doc-001",
      "score": 0.92,
      "text": "When handling errors in production...",
      "metadata": {"source": "docs/error-handling.md"}
    }
  ]
}
```

### Document Ingestion

```bash
bash ingest.sh <file_path> <collection> [chunk_strategy] [metadata_json]
```

**Chunk Strategies:**

| Strategy | Description | Best For |
|----------|-------------|----------|
| `paragraph` | Split by paragraphs (\n\n) | Articles, docs |
| `sentence` | Split by sentences | Short content |
| `fixed` | Fixed 1000 char chunks | Code, logs |
| `semantic` | Semantic boundaries | Long documents |

**Examples:**

```bash
# Ingest with paragraph chunking
bash ingest.sh article.md my_collection paragraph

# With custom metadata
bash ingest.sh api.md my_collection paragraph '{"category": "api", "version": "2.0"}'

# Ingest multiple files
for f in docs/*.md; do
    bash ingest.sh "$f" my_collection paragraph
done
```

### Collection Management

```bash
bash manage.sh <command> [args...]
```

**Commands:**

| Command | Arguments | Description |
|---------|-----------|-------------|
| `list` | - | List all collections |
| `create` | `name dim distance` | Create new collection |
| `delete` | `name` | Delete collection |
| `info` | `name` | Get collection info |
| `optimize` | `name` | Optimize collection |

**Examples:**

```bash
bash manage.sh list
bash manage.sh create my_vectors 1536 cosine
bash manage.sh create my_vectors 768 euclid
bash manage.sh info my_vectors
bash manage.sh optimize my_vectors
bash manage.sh delete my_vectors
```

### Backup & Restore

```bash
bash backup.sh <command> [args...]
```

**Commands:**

| Command | Arguments | Description |
|---------|-----------|-------------|
| `snapshot` | `collection [snapshot_name]` | Create snapshot |
| `restore` | `collection snapshot_name` | Restore from snapshot |
| `list` | `collection` | List snapshots |
| `delete` | `collection snapshot_name` | Delete snapshot |

**Examples:**

```bash
# Create snapshot
bash backup.sh snapshot my_collection
bash backup.sh snapshot my_collection backup_2026_02_10

# List snapshots
bash backup.sh list my_collection

# Restore
bash backup.sh restore my_collection backup_2026_02_10

# Delete old snapshot
bash backup.sh delete my_collection old_backup
```

### Migration

```bash
bash migrate.sh <source_collection> <target_collection> [options]
```

**Migration Types:**

1. **Copy Collection:** Same embedding model, different name
2. **Model Upgrade:** Upgrade to new embedding model (re-embeds)
3. **Filter Migration:** Migrate subset with filter

**Examples:**

```bash
# Simple copy
bash migrate.sh old_collection new_collection

# With model upgrade (re-embeds all content)
bash migrate.sh old_collection new_collection --upgrade-model

# Filtered migration
bash migrate.sh old_collection new_collection --filter '{"category": "public"}'

# Batch size for large collections
bash migrate.sh old_collection new_collection --batch-size 50
```

## Chunking Deep Dive

The ingest script provides intelligent chunking to preserve context:

### Paragraph Chunking
- Splits on double newlines
- Preserves paragraph structure
- Adds overlap of 2 sentences between chunks
- Best for: Articles, documentation, blogs

### Sentence Chunking
- Splits on sentence boundaries
- Minimal overlap
- Best for: Short content, tweets, quotes

### Fixed Chunking
- Fixed 1000 character chunks
- 200 character overlap
- Best for: Code files, logs, unstructured text

### Semantic Chunking
- Uses paragraph + header detection
- Preserves document structure
- Best for: Long documents with headers

## API Reference

All scripts use Qdrant REST API:

```
GET    /collections              # List collections
PUT    /collections/{name}       # Create collection
DELETE /collections/{name}       # Delete collection
GET    /collections/{name}       # Collection info
POST   /collections/{name}/points/search     # Search
PUT    /collections/{name}/points           # Upsert points
POST   /snapshots                # Create snapshot
GET    /collections/{name}/snapshots         # List snapshots
```

Full docs: https://qdrant.tech/documentation/

## Performance Tips

1. **Batch uploads:** ingest.sh automatically batches uploads (default 100)
2. **Optimize after bulk insert:** `bash manage.sh optimize my_collection`
3. **Use filters:** Narrow search scope with metadata filters
4. **Set score thresholds:** Filter low-quality matches
5. **Index metadata:** Add payload indexes for faster filtering

## Troubleshooting

### "Connection refused"
- Check Qdrant is running: `curl http://$QDRANT_HOST:$QDRANT_PORT/healthz`
- Verify host/port environment variables

### "Collection not found"
- List collections: `bash manage.sh list`
- Check collection name spelling

### "No search results"
- Verify documents were ingested: `bash manage.sh info my_collection`
- Check vector dimensions match (e.g., 1536 for text-embedding-3-small)
- Try lowering score threshold

### Embedding errors
- Verify OPENAI_API_KEY is set
- Check API key has quota available
- Verify network access to OpenAI API

### Snapshot fails
- Check disk space available
- Verify Qdrant has snapshot permissions
- For large collections, try during low-traffic periods

## Requirements

- Qdrant server v1.0+
- curl, python3, bash
- OpenAI API key (for embeddings)
- Network access to Qdrant and OpenAI

## See Also

- Qdrant Docs: https://qdrant.tech/documentation/
- OpenAI Embeddings: https://platform.openai.com/docs/guides/embeddings
- Vector Search Guide: https://qdrant.tech/documentation/concepts/search/
