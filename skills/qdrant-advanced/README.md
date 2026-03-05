# Qdrant Advanced

Advanced Qdrant vector database operations for AI agents. Semantic search, document ingestion with contextual chunking, collection management, snapshots, and migrations.

## Quick Start

```bash
export QDRANT_HOST="localhost"
export QDRANT_PORT="6333"
export OPENAI_API_KEY="sk-..."

# List collections
bash manage.sh list

# Create collection
bash manage.sh create my_collection 1536 cosine

# Ingest document
bash ingest.sh article.md my_collection paragraph

# Search
bash search.sh "my query" my_collection 5
```

## Scripts

| Script | Purpose |
|--------|---------|
| `search.sh` | Semantic search with filters |
| `ingest.sh` | Document ingestion with chunking |
| `manage.sh` | Collection CRUD operations |
| `backup.sh` | Snapshots and restore |
| `migrate.sh` | Collection migration, model upgrades |

## Semantic Search

```bash
bash search.sh <query> <collection> [limit] [filter_json] [min_score]
```

```bash
# Basic search
bash search.sh "machine learning" my_docs 10

# With filter
bash search.sh "deployment" my_docs 5 '{"must": [{"key": "category", "match": {"value": "devops"}}]}'

# Score threshold
bash search.sh "error handling" my_docs 10 "" 0.8
```

## Document Ingestion

```bash
bash ingest.sh <file_path> <collection> [chunk_strategy] [metadata_json]
```

**Chunk strategies:** paragraph, sentence, fixed, semantic

```bash
bash ingest.sh article.md my_collection paragraph
bash ingest.sh api.md my_collection fixed '{"version": "2.0"}'
```

## Collection Management

```bash
bash manage.sh list
bash manage.sh create my_collection 1536 cosine
bash manage.sh info my_collection
bash manage.sh optimize my_collection
bash manage.sh delete my_collection
```

## Backup & Restore

```bash
bash backup.sh snapshot my_collection
bash backup.sh snapshot my_collection custom_name
bash backup.sh list my_collection
bash backup.sh restore my_collection snapshot_name
bash backup.sh delete my_collection old_snapshot
```

## Migration

```bash
# Copy collection
bash migrate.sh old_collection new_collection

# Upgrade embedding model (re-embeds all)
bash migrate.sh old_collection new_collection --upgrade-model

# Filtered migration
bash migrate.sh old_collection new_collection --filter '{"category": "public"}'
```

## Requirements

- Qdrant v1.0+
- curl, python3, bash
- OpenAI API key (for embeddings)
