# SQL Database Mastery

## Schema Design

```sql
-- Users table
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email VARCHAR(255) UNIQUE NOT NULL,
  name VARCHAR(255),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_users_email ON users(email);
```

## Index Strategy

| Query Pattern | Index Type |
|--------------|-------------|
| WHERE email = ? | Single column |
| WHERE status = ? AND created > ? | Composite |
| ORDER BY created_at DESC | B-tree (default) |
| Full text search | GIN |

## Migration Safety

```sql
-- Always add columns as nullable first
ALTER TABLE users ADD COLUMN phone VARCHAR(20);

-- Backfill data
UPDATE users SET phone = 'unknown' WHERE phone IS NULL;

-- Make not nullable
ALTER TABLE users ALTER COLUMN phone SET NOT NULL;
```

## Checklist

- [ ] Use UUID for primary keys
- [ ] Add timestamps (created_at, updated_at)
- [ ] Create indexes for query patterns
- [ ] Write safe migrations (backfill, nullable first)
- [ ] Use EXPLAIN ANALYZE
- [ ] Set up connection pooling
