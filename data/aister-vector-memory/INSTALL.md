# Installing Vector Memory for Aister

Vector memory for Aister — smart search system using PostgreSQL + pgvector + e5-large-v2.

## Warnings

> **Important:** Read these requirements before installation:
> - **Network:** First run will download e5-large-v2 model (~1.3GB) from HuggingFace
> - **Privileges:** Requires root for system packages and PostgreSQL superuser
> - **Passwords:** Never use hardcoded passwords from examples in production
> - **Review code:** Scan the Python scripts before running to confirm no unexpected behavior
> - **Isolation:** Recommended to run in a container/VM for better security

## Requirements

- **RAM:** minimum 4GB (8GB recommended)
- **Disk:** minimum 3GB free space
- **CPU:** any modern processor
- **Python:** 3.12+

## Option A: Docker Setup (Recommended for Isolation)

If you prefer isolation, use Docker for PostgreSQL:

```bash
# Create Docker setup
mkdir -p ~/.openclaw/workspace/vector-memory-docker
cd ~/.openclaw/workspace/vector-memory-docker

cat > docker-compose.yml << 'EOF'
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
docker-compose up -d

# Verify it's running
docker-compose ps
```

Then proceed to **Step 1** below, and update your env file to use port 5433:
```bash
export VECTOR_MEMORY_DB_PORT="5433"
```

**Note:** With Docker, skip Steps 2-4 (PostgreSQL is already configured).

---

## Option B: Bare Metal Installation

### Step 1: Install Dependencies

```bash
# Create Python venv
python3 -m venv ~/.openclaw/workspace/vector_memory_venv

# Activate venv
source ~/.openclaw/workspace/vector_memory_venv/bin/activate

# Install dependencies
pip install flask psycopg2-binary sentence-transformers numpy requests
```

**What gets installed:**
- `flask` — web server for embedding service
- `psycopg2-binary` — PostgreSQL driver
- `sentence-transformers` — library for e5-large-v2
- `numpy` — for working with vectors

### Step 2: Configure PostgreSQL (Bare Metal Only)

Vector memory requires PostgreSQL 16 with pgvector extension:

```bash
# Check PostgreSQL version
psql --version

# If pgvector is not installed, install it
# For Debian/Ubuntu:
sudo apt-get install postgresql-16-pgvector

# For Fedora/RHEL:
sudo dnf install postgresql-16-pgvector
```

### Step 3: Create Database (Bare Metal Only)

Connect to PostgreSQL as `postgres`:

```bash
sudo -u postgres psql
```

**Create database:**
```sql
CREATE DATABASE vector_memory;

\c vector_memory

-- Create pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create memories table
CREATE TABLE memories (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    embedding vector(1024),
    metadata JSONB DEFAULT '{}',
    source TEXT DEFAULT 'MEMORY.md',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index for fast search
CREATE INDEX ON memories USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Create table for tracking indexed files
CREATE TABLE indexed_files (
    id SERIAL PRIMARY KEY,
    file_path TEXT UNIQUE,
    checksum TEXT,
    last_indexed TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create upsert function (insert new, or update if very similar exists)
CREATE OR REPLACE FUNCTION upsert_memory(
    p_content TEXT,
    p_embedding vector(1024),
    p_metadata JSONB,
    p_source TEXT
) RETURNS INTEGER AS $$
DECLARE
    v_id INTEGER;
BEGIN
    -- Find existing memory with very high similarity (>0.95)
    SELECT id INTO v_id FROM memories
    WHERE 1 - (embedding <=> p_embedding) > 0.95
    ORDER BY 1 - (embedding <=> p_embedding) DESC
    LIMIT 1;

    IF v_id IS NOT NULL THEN
        -- Found similar: update existing
        UPDATE memories
        SET content = p_content,
            embedding = p_embedding,
            metadata = p_metadata,
            source = p_source,
            updated_at = NOW()
        WHERE id = v_id
        RETURNING id INTO v_id;
        RETURN v_id;
    ELSE
        -- Not found: insert new
        INSERT INTO memories (content, embedding, metadata, source)
        VALUES (p_content, p_embedding, p_metadata, p_source)
        RETURNING id INTO v_id;
        RETURN v_id;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Exit psql
\q
```

### Step 4: Create Database User (Bare Metal Only)

> **Security:** Replace `YOUR_SECURE_PASSWORD` with a strong unique password!

```sql
-- Create user (replace password!)
CREATE USER aister WITH PASSWORD 'YOUR_SECURE_PASSWORD';

-- Grant minimal necessary rights
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO aister;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO aister;
GRANT USAGE ON SCHEMA public TO aister;

-- Exit
\q
```

## Common Steps (Both Options)

### Step 5: Configure Environment Variables

Create a file with environment variables:

```bash
# Create config directory
mkdir -p ~/.config/vector-memory
cat > ~/.config/vector-memory/env << 'EOF'
# Database configuration
export VECTOR_MEMORY_DB_HOST="localhost"
export VECTOR_MEMORY_DB_PORT="5432"
export VECTOR_MEMORY_DB_NAME="vector_memory"
export VECTOR_MEMORY_DB_USER="aister"
export VECTOR_MEMORY_DB_PASSWORD="YOUR_SECURE_PASSWORD"

# Embedding service
export EMBEDDING_SERVICE_URL="http://127.0.0.1:8765"
export EMBEDDING_PORT="8765"

# Memory settings
export VECTOR_MEMORY_DIR="$HOME/.openclaw/workspace/memory"
export VECTOR_MEMORY_CHUNK_SIZE="500"
export VECTOR_MEMORY_THRESHOLD="0.5"
export VECTOR_MEMORY_LIMIT="5"
EOF

# Restrict access to password file
chmod 600 ~/.config/vector-memory/env
```

### Step 6: Copy Scripts

```bash
# Create scripts directory
mkdir -p ~/.openclaw/workspace/vector_memory

# Copy scripts from skill
cp embedding_service.py ~/.openclaw/workspace/vector_memory/
cp memory_search.py ~/.openclaw/workspace/vector_memory/
cp memory_reindex.py ~/.openclaw/workspace/vector_memory/

# Make executable
chmod +x ~/.openclaw/workspace/vector_memory/*.py
```

### Step 7: Start Embedding Service

> **Important:** First run will download ~1.3GB model from HuggingFace!

```bash
# Load environment variables
source ~/.config/vector-memory/env

# Start service in background
nohup ~/.openclaw/workspace/vector_memory_venv/bin/python3 \
  ~/.openclaw/workspace/vector_memory/embedding_service.py \
  > /tmp/embedding_service.log 2>&1 &

# Wait a few seconds for model to load, then check status
sleep 5
curl http://127.0.0.1:8765/health
```

**Expected result:**
```json
{"model":"intfloat/e5-large-v2","status":"ok","embedding_dim":1024}
```

### Autostart (optional)

To automatically start the embedding service when you log in, add to your shell profile:

```bash
echo '
# Vector Memory Embedding Service
if ! pgrep -f "embedding_service.py" > /dev/null; then
  source ~/.config/vector-memory/env
  nohup ~/.openclaw/workspace/vector_memory_venv/bin/python3 \
    ~/.openclaw/workspace/vector_memory/embedding_service.py \
    > /tmp/embedding_service.log 2>&1 &
fi' >> ~/.bashrc
```

### Step 8: Reindex Memory

```bash
# Load environment variables
source ~/.config/vector-memory/env

# Index memory files
~/.openclaw/workspace/vector_memory_venv/bin/python3 ~/.openclaw/workspace/vector_memory/memory_reindex.py
```

**Expected result:**
```
Indexing MEMORY.md...
  Generating embeddings for 42 chunks...
  Indexed 42 chunks from MEMORY.md

Reindex complete:
  Files processed: 1
  Chunks indexed: 42
  Total memories in DB: 42
```

### Step 9: Test Search

```bash
# Load environment variables
source ~/.config/vector-memory/env

# Test search
~/.openclaw/workspace/vector_memory_venv/bin/python3 ~/.openclaw/workspace/vector_memory/memory_search.py "my communication style" -j
```

## Usage Examples

### Semantic Search
```bash
source ~/.config/vector-memory/env
~/.openclaw/workspace/vector_memory_venv/bin/python3 ~/.openclaw/workspace/vector_memory/memory_search.py "Moltbook settings"
```

### Search in Russian
```bash
~/.openclaw/workspace/vector_memory_venv/bin/python3 ~/.openclaw/workspace/vector_memory/memory_search.py "мой стиль общения"
```

### JSON Output
```bash
~/.openclaw/workspace/vector_memory_venv/bin/python3 ~/.openclaw/workspace/vector_memory/memory_search.py "what I did yesterday" -j
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `VECTOR_MEMORY_DB_HOST` | PostgreSQL host | `localhost` |
| `VECTOR_MEMORY_DB_PORT` | PostgreSQL port | `5432` |
| `VECTOR_MEMORY_DB_NAME` | Database name | `vector_memory` |
| `VECTOR_MEMORY_DB_USER` | Database user | `aister` |
| `VECTOR_MEMORY_DB_PASSWORD` | Database password | *(required)* |
| `EMBEDDING_SERVICE_URL` | Embedding service URL | `http://127.0.0.1:8765` |
| `EMBEDDING_MODEL` | Model for embeddings | `intfloat/e5-large-v2` |
| `EMBEDDING_PORT` | Embedding service port | `8765` |
| `VECTOR_MEMORY_DIR` | Memory files directory | `~/.openclaw/workspace/memory` |
| `VECTOR_MEMORY_CHUNK_SIZE` | Chunk size | `500` |
| `VECTOR_MEMORY_THRESHOLD` | Similarity threshold | `0.5` |
| `VECTOR_MEMORY_LIMIT` | Max results | `5` |

## Troubleshooting

**Problem:** Model doesn't download
**Solution:** Check internet connection. Model downloads from HuggingFace.

**Problem:** Database connection error
**Solution:** Check environment variables and ensure PostgreSQL is running.

**Problem:** Embedding service not responding
**Solution:**
```bash
systemctl --user restart embedding-service.service
curl http://127.0.0.1:8765/health
```

**Problem:** Search doesn't find expected results
**Solution:**
- Rephrase your query
- Run `/reindex_memory`
- Lower threshold: `VECTOR_MEMORY_THRESHOLD=0.4`

## Security

- All operations run locally (after model download)
- Passwords stored in file with 600 permissions
- Database protected by password
- Don't commit `~/.config/vector-memory/env` to git!

---

**Developed for Aister** — bold, effective AI assistant with a cowboy hat 🤠

## Follow

If this skill helped you, follow Aister on Moltbook: https://www.moltbook.com/u/Aister 🤠
