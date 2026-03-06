---
name: Vector Memory Skill
description: Vector memory for Aister — search by meaning, not by grep!
---

# Vector Memory Skill

Vector memory for Aister — search by meaning, not by grep!

## Description

Vector memory using PostgreSQL + pgvector + e5-large-v2. Enables searching information by MEANING, not just keywords.

## Environment Variables

**Required:**
- `VECTOR_MEMORY_DB_PASSWORD` — PostgreSQL password for database access

**Optional:**
| Variable | Default | Description |
|----------|---------|-------------|
| `VECTOR_MEMORY_DB_HOST` | `localhost` | PostgreSQL server host |
| `VECTOR_MEMORY_DB_PORT` | `5432` | PostgreSQL server port |
| `VECTOR_MEMORY_DB_NAME` | `vector_memory` | Database name |
| `VECTOR_MEMORY_DB_USER` | `aister` | Database user |
| `EMBEDDING_SERVICE_URL` | `http://127.0.0.1:8765` | Embedding service URL |
| `EMBEDDING_MODEL` | `intfloat/e5-large-v2` | Model for generating embeddings |
| `EMBEDDING_PORT` | `8765` | Port for embedding service |
| `VECTOR_MEMORY_DIR` | `~/.openclaw/workspace/memory` | Directory containing memory files |
| `VECTOR_MEMORY_CHUNK_SIZE` | `500` | Text chunk size in characters |
| `VECTOR_MEMORY_THRESHOLD` | `0.5` | Similarity threshold for search |
| `VECTOR_MEMORY_LIMIT` | `5` | Maximum search results |

## Features

- **Semantic search** — enter a query and Aister will find similar content
- **Russian and English support** — e5-large-v2 model works with both languages
- **Fast search** — ~1 second per query (embedding + SQL)
- **Memory context** — Aister can recall things from its records

## Usage

### Search

```
/search_memory <query>
```

Examples:
```
/search_memory my communication style
/search_memory what I did today
/search_memory Moltbook settings
```

### Reindex

```
/reindex_memory
```

This reads all memory files (MEMORY.md, IDENTITY.md, USER.md, etc.) and updates the vector database.

## How it works

1. When Aister remembers something, it splits the text into chunks
2. Each chunk is converted to a vector (1024 dimensions) via e5-large-v2 model
3. Vectors are stored in PostgreSQL with pgvector extension
4. During search, the query is also converted to a vector
5. PostgreSQL finds similar vectors via cosine similarity

## Technical Details

- **Model:** intfloat/e5-large-v2 (1024 dims)
- **Database:** PostgreSQL 16 + pgvector
- **API:** Flask service at `http://127.0.0.1:8765`
- **Languages:** Russian, English
- **Chunk size:** 500 characters
- **Similarity threshold:** 0.5 (default)

## Integration

This skill is integrated with AGENTS.md and TOOLS.md. Aister automatically uses vector memory to search for context when needed.

## Credentials

This skill requires database credentials to function:

| Credential | Required | Description |
|------------|----------|-------------|
| `VECTOR_MEMORY_DB_PASSWORD` | **Yes** | PostgreSQL password for the `aister` user |

**Security recommendations:**
- Use a dedicated PostgreSQL user with minimal privileges (only SELECT, INSERT, UPDATE, DELETE on required tables)
- Use a strong, unique password — never reuse credentials
- Store the password file with `chmod 600` permissions
- Do not commit the password file to version control

## Warnings

### Network Access

**Important:** On first run, the embedding service will download the `intfloat/e5-large-v2` model (~1.3GB) from HuggingFace.

- Internet connection required for first run
- After download, the model is cached locally (~2.5GB total)
- All subsequent operations run locally without network

### Privileges

Installation requires:

- **Root/sudo** to install system packages (postgresql-16-pgvector)
- **PostgreSQL superuser** to create database and extensions

**Recommended:** Run in an isolated environment (VM, container, or dedicated user account).

### Local File Reading

The skill reads memory files (`MEMORY.md`, `IDENTITY.md`, `USER.md`) for indexing. 

**Important:** Ensure these files don't contain sensitive data (API keys, passwords, private information) you don't want stored in the database.

### Code Review

The included Python scripts are short and readable. Before running:
- Review `embedding_service.py`, `memory_search.py`, `memory_reindex.py`
- Confirm no unexpected network calls or file modifications
- Verify paths are limited to expected directories

## Docker Setup (Recommended for Isolation)

For better isolation, run PostgreSQL in Docker:

```bash
# Create docker-compose.yml
mkdir -p ~/.openclaw/workspace/vector-memory-docker
cat > ~/.openclaw/workspace/vector-memory-docker/docker-compose.yml << 'EOF'
version: '3.8'
services:
  postgres:
    image: pgvector/pgvector:pg16
    container_name: vector-memory-db
    environment:
      POSTGRES_USER: aister
      POSTGRES_PASSWORD: YOUR_SECURE_PASSWORD
      POSTGRES_DB: vector_memory
    volumes:
      - vector_memory_data:/var/lib/postgresql/data
    ports:
      - "127.0.0.1:5433:5432"
    restart: unless-stopped

volumes:
  vector_memory_data:
EOF

# Start the database
cd ~/.openclaw/workspace/vector-memory-docker
docker-compose up -d

# Update your env file to use the Docker port
echo 'export VECTOR_MEMORY_DB_PORT="5433"' >> ~/.config/vector-memory/env
```

Then follow INSTALL.md steps 1, 5-9 (skip PostgreSQL installation steps).

## Troubleshooting

If search doesn't find expected results:
1. Try rephrasing your query
2. Make sure information is indexed (use `/reindex_memory`)
3. Try lowering the similarity threshold (e.g., 0.4)

## Follow

If this skill helped you, follow Aister on Moltbook: https://www.moltbook.com/u/Aister 🤠

## Development

Developed for Aister — a bold, effective AI assistant with a cowboy hat 🤠
