# Jack Cloud Services — Deep Dive

## Database (D1) Patterns

### Accessing the Database in Code

D1 is bound as `DB` in your worker environment:

```typescript
// Hono example
app.get("/api/users", async (c) => {
  const { results } = await c.env.DB.prepare("SELECT * FROM users LIMIT 50").all();
  return c.json(results);
});

// With parameters (always use prepared statements)
app.get("/api/users/:id", async (c) => {
  const { results } = await c.env.DB.prepare("SELECT * FROM users WHERE id = ?")
    .bind(c.req.param("id"))
    .all();
  return c.json(results[0] ?? null);
});

// Insert
app.post("/api/users", async (c) => {
  const { name, email } = await c.req.json();
  const result = await c.env.DB.prepare("INSERT INTO users (name, email) VALUES (?, ?)")
    .bind(name, email)
    .run();
  return c.json({ id: result.meta.last_row_id }, 201);
});
```

### Batch Operations

```typescript
const batch = [
  c.env.DB.prepare("INSERT INTO users (name) VALUES (?)").bind("Alice"),
  c.env.DB.prepare("INSERT INTO users (name) VALUES (?)").bind("Bob"),
];
await c.env.DB.batch(batch);
```

### Schema Conventions

```sql
-- Use INTEGER PRIMARY KEY for auto-increment IDs
-- Use TEXT for dates (ISO 8601 format)
-- Use TEXT DEFAULT CURRENT_TIMESTAMP for created_at
CREATE TABLE items (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  data TEXT,  -- JSON stored as text
  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```

---

## Storage (R2) Patterns

### File Upload/Download

```typescript
// Upload
app.put("/api/files/:key", async (c) => {
  const body = await c.req.arrayBuffer();
  await c.env.BUCKET.put(c.req.param("key"), body, {
    httpMetadata: { contentType: c.req.header("content-type") },
  });
  return c.json({ success: true });
});

// Download
app.get("/api/files/:key", async (c) => {
  const object = await c.env.BUCKET.get(c.req.param("key"));
  if (!object) return c.notFound();
  return new Response(object.body, {
    headers: { "content-type": object.httpMetadata?.contentType ?? "application/octet-stream" },
  });
});

// List files
app.get("/api/files", async (c) => {
  const listed = await c.env.BUCKET.list({ limit: 100 });
  return c.json(listed.objects.map(o => ({ key: o.key, size: o.size })));
});
```

---

## Vectorize Patterns

### Inserting Vectors

```typescript
// Generate embeddings using Workers AI or your own model
const embedding = await c.env.AI.run("@cf/baai/bge-base-en-v1.5", { text: ["Hello world"] });

// Insert into Vectorize
await c.env.VECTORIZE_INDEX.insert([{
  id: "doc-1",
  values: embedding.data[0],
  metadata: { text: "Hello world", source: "example" },
}]);
```

### Querying

```typescript
const queryEmbedding = await c.env.AI.run("@cf/baai/bge-base-en-v1.5", { text: [query] });

const results = await c.env.VECTORIZE_INDEX.query(queryEmbedding.data[0], {
  topK: 5,
  returnMetadata: "all",
});
// results.matches = [{ id, score, metadata }, ...]
```

---

## Cron Patterns

### Scheduled Handler

```typescript
// In your worker entry point
export default {
  async fetch(request, env) { /* normal request handling */ },

  async scheduled(event, env, ctx) {
    // Runs on your cron schedule
    // event.cron = the cron expression that triggered this
    // event.scheduledTime = when it was supposed to run

    // Example: clean up old records
    await env.DB.prepare("DELETE FROM sessions WHERE expires_at < datetime('now')").run();
  },
};
```

### Alternative: POST Route

If using Hono, you can handle cron via a route instead:

```typescript
app.post("/__scheduled", async (c) => {
  // This route is called by the cron trigger
  await c.env.DB.prepare("DELETE FROM sessions WHERE expires_at < datetime('now')").run();
  return c.json({ success: true });
});
```

### Common Expressions

| Expression | Schedule |
|-----------|----------|
| `*/15 * * * *` | Every 15 minutes |
| `0 * * * *` | Every hour |
| `0 0 * * *` | Daily at midnight UTC |
| `0 9 * * MON` | Monday at 9am UTC |
| `0 */6 * * *` | Every 6 hours |

---

## Custom Domains

### DNS Setup

After `jack domain assign app.example.com`, add this DNS record:

| Type | Name | Target |
|------|------|--------|
| CNAME | `app` | `<slug>.runjack.xyz` |

For apex domains (example.com without subdomain), some DNS providers support CNAME flattening. Otherwise use a subdomain.

### SSL

SSL certificates are provisioned automatically. After DNS propagation (usually 1-5 minutes), your domain will serve over HTTPS.
