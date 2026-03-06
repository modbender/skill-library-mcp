# Schema Design Patterns — SQL

## Multi-tenancy

### Shared Tables (simple, one database)

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL REFERENCES tenants(id),
    email TEXT NOT NULL,
    UNIQUE (tenant_id, email)
);

-- Always filter by tenant
CREATE INDEX idx_users_tenant ON users(tenant_id);
```

### Separate Schemas (PostgreSQL)

```sql
CREATE SCHEMA tenant_acme;
SET search_path TO tenant_acme;
CREATE TABLE users (...);

-- Switch tenant
SET search_path TO tenant_bigcorp;
```

---

## Soft Deletes

```sql
CREATE TABLE posts (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    deleted_at TIMESTAMPTZ  -- NULL = not deleted
);

-- Default view excludes deleted
CREATE VIEW active_posts AS
SELECT * FROM posts WHERE deleted_at IS NULL;

-- Partial index for active records only
CREATE INDEX idx_posts_active ON posts(id) WHERE deleted_at IS NULL;
```

---

## Audit Logging

```sql
CREATE TABLE audit_log (
    id SERIAL PRIMARY KEY,
    table_name TEXT NOT NULL,
    record_id INTEGER NOT NULL,
    action TEXT NOT NULL,  -- INSERT, UPDATE, DELETE
    old_data JSONB,
    new_data JSONB,
    changed_by INTEGER REFERENCES users(id),
    changed_at TIMESTAMPTZ DEFAULT NOW()
);

-- Trigger for automatic logging (PostgreSQL)
CREATE OR REPLACE FUNCTION audit_trigger()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO audit_log (table_name, record_id, action, old_data, new_data)
    VALUES (TG_TABLE_NAME, COALESCE(NEW.id, OLD.id), TG_OP, 
            to_jsonb(OLD), to_jsonb(NEW));
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER users_audit
AFTER INSERT OR UPDATE OR DELETE ON users
FOR EACH ROW EXECUTE FUNCTION audit_trigger();
```

---

## Polymorphic Associations

### Single Table (simple queries, sparse columns)

```sql
CREATE TABLE comments (
    id SERIAL PRIMARY KEY,
    body TEXT NOT NULL,
    commentable_type TEXT NOT NULL,  -- 'Post', 'Photo', 'Video'
    commentable_id INTEGER NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_comments_poly ON comments(commentable_type, commentable_id);
```

### Separate FKs (strict integrity)

```sql
CREATE TABLE comments (
    id SERIAL PRIMARY KEY,
    body TEXT NOT NULL,
    post_id INTEGER REFERENCES posts(id),
    photo_id INTEGER REFERENCES photos(id),
    CHECK (
        (post_id IS NOT NULL)::int + 
        (photo_id IS NOT NULL)::int = 1
    )
);
```

---

## Tags/Labels

### Junction Table (standard M:N)

```sql
CREATE TABLE tags (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL
);

CREATE TABLE post_tags (
    post_id INTEGER REFERENCES posts(id) ON DELETE CASCADE,
    tag_id INTEGER REFERENCES tags(id) ON DELETE CASCADE,
    PRIMARY KEY (post_id, tag_id)
);

-- Find posts with all specified tags
SELECT p.* FROM posts p
JOIN post_tags pt ON pt.post_id = p.id
JOIN tags t ON t.id = pt.tag_id
WHERE t.name IN ('sql', 'tutorial')
GROUP BY p.id
HAVING COUNT(DISTINCT t.name) = 2;
```

### Array Column (PostgreSQL, simpler)

```sql
CREATE TABLE posts (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    tags TEXT[] DEFAULT '{}'
);

CREATE INDEX idx_posts_tags ON posts USING GIN(tags);

-- Find posts with tag
SELECT * FROM posts WHERE 'sql' = ANY(tags);

-- Find posts with all tags
SELECT * FROM posts WHERE tags @> ARRAY['sql', 'tutorial'];
```

---

## State Machines

```sql
CREATE TYPE order_status AS ENUM ('draft', 'pending', 'paid', 'shipped', 'delivered', 'cancelled');

CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    status order_status NOT NULL DEFAULT 'draft'
);

-- Status history for auditing
CREATE TABLE order_status_history (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(id),
    from_status order_status,
    to_status order_status NOT NULL,
    changed_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

## Full-Text Search

### PostgreSQL

```sql
-- Add search vector column
ALTER TABLE posts ADD COLUMN search_vector tsvector;

-- Populate and index
UPDATE posts SET search_vector = to_tsvector('english', title || ' ' || body);
CREATE INDEX idx_posts_search ON posts USING GIN(search_vector);

-- Search
SELECT * FROM posts WHERE search_vector @@ to_tsquery('english', 'database & performance');

-- Auto-update trigger
CREATE TRIGGER posts_search_update
BEFORE INSERT OR UPDATE ON posts
FOR EACH ROW EXECUTE FUNCTION 
    tsvector_update_trigger(search_vector, 'pg_catalog.english', title, body);
```

### SQLite (FTS5)

```sql
CREATE VIRTUAL TABLE posts_fts USING fts5(title, body, content=posts, content_rowid=id);

-- Search
SELECT * FROM posts_fts WHERE posts_fts MATCH 'database performance';
```

---

## Versioning (Keep History)

```sql
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    body TEXT NOT NULL,
    version INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE document_versions (
    id SERIAL PRIMARY KEY,
    document_id INTEGER REFERENCES documents(id),
    title TEXT NOT NULL,
    body TEXT NOT NULL,
    version INTEGER NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Save version before update
CREATE OR REPLACE FUNCTION save_document_version()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO document_versions (document_id, title, body, version)
    VALUES (OLD.id, OLD.title, OLD.body, OLD.version);
    NEW.version = OLD.version + 1;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER documents_version
BEFORE UPDATE ON documents
FOR EACH ROW EXECUTE FUNCTION save_document_version();
```

---

## Settings/Config (Key-Value)

### Simple Table

```sql
CREATE TABLE settings (
    key TEXT PRIMARY KEY,
    value JSONB NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Get setting
SELECT value->>'theme' FROM settings WHERE key = 'user_prefs';

-- Upsert setting
INSERT INTO settings (key, value) VALUES ('user_prefs', '{"theme": "dark"}')
ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value, updated_at = NOW();
```

### Per-User Settings

```sql
CREATE TABLE user_settings (
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    key TEXT NOT NULL,
    value JSONB NOT NULL,
    PRIMARY KEY (user_id, key)
);
```

---

## Time-Series Data

```sql
-- Partitioning by month (PostgreSQL 10+)
CREATE TABLE metrics (
    id SERIAL,
    recorded_at TIMESTAMPTZ NOT NULL,
    metric_name TEXT NOT NULL,
    value NUMERIC NOT NULL
) PARTITION BY RANGE (recorded_at);

CREATE TABLE metrics_2026_01 PARTITION OF metrics
FOR VALUES FROM ('2026-01-01') TO ('2026-02-01');

CREATE TABLE metrics_2026_02 PARTITION OF metrics
FOR VALUES FROM ('2026-02-01') TO ('2026-03-01');

-- Automatic partition creation with pg_partman extension
```

---

## Counting (Exact vs Approximate)

```sql
-- Exact count (slow on large tables)
SELECT COUNT(*) FROM large_table;

-- Approximate count (PostgreSQL, instant)
SELECT reltuples::bigint AS estimate 
FROM pg_class WHERE relname = 'large_table';

-- Cached count (maintain manually)
CREATE TABLE table_counts (
    table_name TEXT PRIMARY KEY,
    row_count BIGINT NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```
