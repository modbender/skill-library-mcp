# SurrealDB SDK Reference

This document covers SDK usage patterns for all officially supported languages. SurrealDB provides native SDKs in 9+ languages, each offering HTTP and WebSocket connectivity, with select SDKs also supporting embedded (in-process) database engines.

---

## JavaScript / TypeScript SDK

**Package**: `surrealdb` on npm
**Repository**: github.com/surrealdb/surrealdb.js

### Installation

```bash
npm install surrealdb

# For embedded Node.js engine
npm install @surrealdb/node

# For WASM browser engine
npm install @surrealdb/wasm
```

### Engine Options

The JS/TS SDK supports three distinct engines:

| Engine | Package | Use Case |
|--------|---------|----------|
| Remote (HTTP/WebSocket) | `surrealdb` | Client-server applications |
| Node.js embedded | `@surrealdb/node` | Server-side apps without separate DB process |
| WASM (browser) | `@surrealdb/wasm` | Browser-based applications, offline-first |

### Connection Patterns

```typescript
import { Surreal, RecordId, Table } from "surrealdb";

const db = new Surreal();

// --- Remote connections ---
// WebSocket (recommended for live queries and subscriptions)
await db.connect("wss://host:8000");

// HTTP (stateless, suitable for serverless)
await db.connect("https://host:8000");

// --- Embedded Node.js connections (requires @surrealdb/node) ---
// In-memory (data lost on process exit)
await db.connect("mem://");

// RocksDB persistent storage
await db.connect("rocksdb://path.db");

// SurrealKV persistent storage
await db.connect("surrealkv://path.db");

// SurrealKV with versioned storage (supports historical queries)
await db.connect("surrealkv+versioned://path.db");

// --- WASM browser connections (requires @surrealdb/wasm) ---
// In-memory
await db.connect("mem://");

// IndexedDB persistent storage (browser only)
await db.connect("indxdb://mydb");
```

### Authentication

```typescript
// Root-level authentication
await db.signin({
  username: "root",
  password: "root",
});

// Namespace-level authentication
await db.signin({
  namespace: "my_ns",
  username: "ns_user",
  password: "ns_pass",
});

// Database-level authentication
await db.signin({
  namespace: "my_ns",
  database: "my_db",
  username: "db_user",
  password: "db_pass",
});

// Record-level (scope) authentication
const token = await db.signin({
  namespace: "my_ns",
  database: "my_db",
  access: "user_access",
  variables: {
    email: "user@example.com",
    password: "user_pass",
  },
});

// Sign up a new record user
const token = await db.signup({
  namespace: "my_ns",
  database: "my_db",
  access: "user_access",
  variables: {
    email: "new@example.com",
    password: "new_pass",
    name: "New User",
  },
});

// Use an existing token
await db.authenticate(token);

// Invalidate the current session
await db.invalidate();
```

### Namespace and Database Selection

```typescript
await db.use({
  namespace: "my_ns",
  database: "my_db",
});

// Or set individually
await db.use({ namespace: "my_ns" });
await db.use({ database: "my_db" });
```

### CRUD Operations

```typescript
// --- Create ---
// Create with auto-generated ID
const person = await db.create("person", {
  name: "Alice",
  age: 30,
});

// Create with specific ID
const specific = await db.create(new RecordId("person", "alice"), {
  name: "Alice",
  age: 30,
});

// --- Select ---
// Select all records from a table
const allPeople = await db.select("person");

// Select a specific record
const alice = await db.select(new RecordId("person", "alice"));

// --- Update (full replacement) ---
// Replace all fields on a record
const updated = await db.update(new RecordId("person", "alice"), {
  name: "Alice Smith",
  age: 31,
  email: "alice@example.com",
});

// --- Merge (partial update) ---
// Update only specified fields, keep the rest
const merged = await db.merge(new RecordId("person", "alice"), {
  age: 32,
});

// --- Patch (JSON Patch operations) ---
const patched = await db.patch(new RecordId("person", "alice"), [
  { op: "replace", path: "/age", value: 33 },
  { op: "add", path: "/verified", value: true },
]);

// --- Delete ---
// Delete a specific record
await db.delete(new RecordId("person", "alice"));

// Delete all records in a table
await db.delete("person");
```

### Queries

```typescript
// Simple query
const results = await db.query("SELECT * FROM person WHERE age > 25");

// Parameterized query (prevents injection)
const results = await db.query(
  "SELECT * FROM person WHERE age > $min_age AND name = $name",
  {
    min_age: 25,
    name: "Alice",
  }
);

// Typed query results
interface Person {
  id: RecordId;
  name: string;
  age: number;
}

const [people] = await db.query<[Person[]]>(
  "SELECT * FROM person WHERE age > $min_age",
  { min_age: 25 }
);

// Multiple statements in one query
const [people, orders] = await db.query<[Person[], Order[]]>(`
  SELECT * FROM person WHERE active = true;
  SELECT * FROM order WHERE status = 'pending';
`);
```

### Live Queries

```typescript
// Subscribe to changes on a table
const stream = await db.live("person");

// Process events with async iteration
for await (const event of stream) {
  switch (event.action) {
    case "CREATE":
      console.log("New person:", event.result);
      break;
    case "UPDATE":
      console.log("Updated person:", event.result);
      break;
    case "DELETE":
      console.log("Deleted person:", event.result);
      break;
  }
}

// Live query with a filter
const stream = await db.live("person", {
  filter: "age > 25",
});

// Kill a live query
await db.kill(stream.id);
```

### RecordId Usage

```typescript
import { RecordId, Table } from "surrealdb";

// Create a RecordId
const id = new RecordId("person", "alice");
console.log(id.table);  // "person"
console.log(id.id);     // "alice"

// Numeric IDs
const numericId = new RecordId("person", 123);

// Complex IDs (arrays, objects)
const complexId = new RecordId("temperature", ["London", new Date()]);

// Table reference (for operations on all records)
const table = new Table("person");
```

### Error Handling

```typescript
import { Surreal, SurrealError, ConnectionError } from "surrealdb";

try {
  await db.connect("wss://host:8000");
  await db.signin({ username: "root", password: "root" });
} catch (error) {
  if (error instanceof ConnectionError) {
    console.error("Failed to connect:", error.message);
  } else if (error instanceof SurrealError) {
    console.error("SurrealDB error:", error.message);
  }
}
```

### Connection Lifecycle and Reconnection

```typescript
const db = new Surreal();

// Connect with event handlers
db.on("connected", () => console.log("Connected"));
db.on("disconnected", () => console.log("Disconnected"));
db.on("error", (err) => console.error("Error:", err));

await db.connect("wss://host:8000");

// Graceful shutdown
await db.close();
```

---

## JavaScript / TypeScript SDK v2 (GA -- recommended for new projects)

**Package**: `surrealdb` on npm (v2.0.0, released 2026-02-25)
**Status**: General availability. Full SurrealDB 3.0.1 support. Recommended for
new projects. The v1 API above is maintained but v2 is the future.

The v2 SDK is a ground-up rewrite with an engine-based architecture, multi-session
support, client-side transactions, query builder patterns, streaming responses,
automatic token refresh, and full SurrealDB 3.0 compatibility.

**v2.0.0 GA highlights** (2026-02-25):
- Full SurrealDB 3.0.1 support (embedded WASM and Node engines updated)
- Engine-based architecture (createRemoteEngines, createNodeEngines, createWasmEngines)
- Multi-session support (newSession, forkSession, await using)
- Client-side transactions
- Automatic token refreshing with refresh token exchange
- Redesigned live query API with subscribe/async iteration
- Query builder pattern with chainable methods
- Expressions API (eq, ne, or, and, between, inside, raw, surql template tag)
- Diagnostics API for protocol-level inspection
- Codec visitor API for custom encode/decode
- User-defined API invocation (.api())
- Web Worker support via createWasmWorkerEngines with createWorker factory

### Installation

```bash
npm install surrealdb

# Embedded engines (published in sync with the SDK)
npm install @surrealdb/node
npm install @surrealdb/wasm
```

### Engine Architecture (v2)

The v2 SDK separates engines from the Surreal class. You compose engines
explicitly in the constructor.

```typescript
import { Surreal, createRemoteEngines } from "surrealdb";
import { createNodeEngines } from "@surrealdb/node";
import { createWasmEngines, createWasmWorkerEngines } from "@surrealdb/wasm";

// Remote only (HTTP + WebSocket)
const db = new Surreal({
  engines: createRemoteEngines(),
});

// Remote + embedded Node.js
const db = new Surreal({
  engines: {
    ...createRemoteEngines(),
    ...createNodeEngines(),
  },
});

// Remote + WASM (browser)
const db = new Surreal({
  engines: {
    ...createRemoteEngines(),
    ...createWasmEngines(),
  },
});

// WASM in a Web Worker (offloads DB ops from main thread)
// NOTE: beta.2+ requires createWorker factory for Vite compatibility
import WorkerAgent from "@surrealdb/wasm/worker?worker";

const db = new Surreal({
  engines: {
    ...createRemoteEngines(),
    ...createWasmWorkerEngines({
      createWorker: () => new WorkerAgent(),
    }),
  },
});
```

### Connection with Auto Token Refresh (v2)

```typescript
const db = new Surreal();

await db.connect("wss://host:8000", {
  namespace: "test",
  database: "test",
  renewAccess: true,  // auto-refresh expired tokens (default: true)
  authentication: {
    username: "root",
    password: "root",
  },
});

// Or use a callable for async/deferred auth
await db.connect("wss://host:8000", {
  namespace: "test",
  database: "test",
  authentication: () => ({
    username: "root",
    password: "root",
  }),
});
```

### Event Listeners (v2)

```typescript
// Type-safe event subscriptions (replaces v1 .on() pattern)
const unsub = db.subscribe("connected", () => {
  console.log("Connected");
});

// Cleanup
unsub();

// Access internal state
console.log(db.namespace);     // current namespace
console.log(db.database);      // current database
console.log(db.accessToken);   // current access token
console.log(db.refreshToken);  // current refresh token
console.log(db.params);        // defined connection params
```

### Multi-Session Support (v2)

```typescript
// Create an isolated session (own namespace, database, auth state)
const session = await db.newSession();
await session.signin({ username: "other_user", password: "pass" });
await session.use({ namespace: "other_ns", database: "other_db" });

// Fork a session (clone its state)
const forked = await session.forkSession();

// Close a session
await session.closeSession();

// Automatic cleanup with await using (TC39 Explicit Resource Management)
{
  await using session = await db.newSession();
  // session is automatically closed at end of scope
}
```

### Query Builder Pattern (v2)

v2 introduces chainable builder methods on all query functions. `update` and
`upsert` no longer take contents as a second argument; use `.content()`,
`.merge()`, `.replace()`, or `.patch()` instead.

```typescript
import { Table, RecordId } from "surrealdb";

const usersTable = new Table("users");

// Select with field selection and fetch
const record = await db.select(new RecordId("person", "alice"))
  .fields("age", "firstname", "lastname")
  .fetch("orders");

// Select with where filter
const active = await db.select(usersTable)
  .where(eq("active", true));

// Update with merge (v2 pattern)
await db.update(new RecordId("person", "alice")).merge({
  age: 32,
  verified: true,
});

// Update with content (full replace)
await db.update(new RecordId("person", "alice")).content({
  name: "Alice Smith",
  age: 32,
});

// Upsert with merge
await db.upsert(new RecordId("person", "bob")).merge({
  name: "Bob",
  active: true,
});
```

**IMPORTANT (v2 breaking change)**: Query functions no longer accept plain strings
as table names. You must use the `Table` class:

```typescript
// v1 (still works in v1 SDK)
await db.select("person");

// v2 (required)
await db.select(new Table("person"));
```

### Query Method Overhaul (v2)

```typescript
// Basic typed query
const [user] = await db.query<[User]>("SELECT * FROM user:foo");

// Collect specific result indexes from multi-statement queries
const [users, orders] = await db.query(
  "LET $u = SELECT * FROM user; LET $o = SELECT * FROM order; RETURN $u; RETURN $o"
).collect<[User[], Order[]]>(2, 3);

// Auto-jsonify results
const [products] = await db.query<[Product[]]>(
  "SELECT * FROM product"
).json();

// Get full response objects (including status, time, etc.)
const responses = await db.query<[Product[]]>(
  "SELECT * FROM product"
).responses();

// Stream responses (prepare for future per-record streaming)
const stream = db.query("SELECT * FROM large_table").stream();

for await (const frame of stream) {
  if (frame.isValue<Product>()) {
    console.log(frame.value);
  } else if (frame.isDone()) {
    console.log("Stats:", frame.stats);
  } else if (frame.isError()) {
    console.error(frame.error);
  }
}
```

### Expressions API (v2)

Compose dynamic, param-safe WHERE expressions:

```typescript
import { eq, ne, or, and, between, inside, raw, surql } from "surrealdb";

// Use with query builder .where()
await db.select(usersTable).where(eq("active", true));

// Compose complex expressions
await db.select(usersTable).where(
  or(
    eq("role", "admin"),
    and(
      eq("active", true),
      between("age", 18, 65)
    )
  )
);

// Use with surql template tag
const isActive = true;
await db.query(surql`SELECT * FROM users WHERE ${eq("active", isActive)}`);

// Raw expression insertion (use with caution)
await db.query(surql`SELECT * FROM users ${raw("WHERE active = true")}`);
```

### Redesigned Live Queries (v2)

```typescript
const live = await db.live(new Table("users"));

// Callback-based (action, result, recordId)
live.subscribe((action, result, record) => {
  console.log(action, result, record);
});

// Async iteration
for await (const { action, value } of live) {
  console.log(action, value);
}

// Kill the live query
live.kill();

// Attach to an existing live query ID
const [id] = await db.query("LIVE SELECT * FROM users");
const existing = await db.liveOf(id);
```

### User-Defined API Invocation (v2)

```typescript
// Call user-defined APIs registered in SurrealDB
const result = await db.api("my_custom_endpoint", {
  param1: "value",
});
```

### Diagnostics API (v2)

Intercept protocol-level communication for debugging:

```typescript
import { applyDiagnostics, createRemoteEngines } from "surrealdb";

const db = new Surreal({
  engines: applyDiagnostics(createRemoteEngines(), (event) => {
    // event: { type, key, phase, duration?, success?, result? }
    console.log(`[${event.type}] ${event.phase}`, event.duration);
  }),
});
```

Event types: `open`, `version`, `use`, `signin`, `query`, `reset`.
Each event has `before`, `progress` (queries only), and `after` phases.

### Codec Visitor API (v2)

Custom encode/decode processing for SurrealDB values:

```typescript
const db = new Surreal({
  codecOptions: {
    valueDecodeVisitor(value) {
      // Transform RecordIds, Dates, or custom types on decode
      return value;
    },
    valueEncodeVisitor(value) {
      // Transform values before sending to SurrealDB
      return value;
    },
  },
});
```

### Migration Guide: v1 to v2

| v1 Pattern | v2 Equivalent |
|------------|---------------|
| `new Surreal()` | `new Surreal({ engines: createRemoteEngines() })` |
| `db.connect("wss://...")` | Same, but with `authentication` option for auto-refresh |
| `db.on("connected", fn)` | `db.subscribe("connected", fn)` -- returns unsub function |
| `db.select("person")` | `db.select(new Table("person"))` |
| `db.update(id, data)` | `db.update(id).content(data)` or `.merge(data)` |
| `db.merge(id, data)` | `db.update(id).merge(data)` |
| `db.query(q).then(([r]) => ...)` | `db.query(q).collect<[T]>(0)` |
| `db.live("person")` then iterate | `db.live(new Table("person"))` then `.subscribe()` or `for await` |
| N/A | `db.newSession()` -- isolated sessions |
| N/A | `db.query(q).stream()` -- streaming responses |
| N/A | `db.api("endpoint")` -- user-defined APIs |
| N/A | `applyDiagnostics()` -- protocol inspection |

---

## Python SDK

**Package**: `surrealdb` on PyPI (v2.0.0-alpha.1, released 2026-02-26)
**Repository**: github.com/surrealdb/surrealdb.py
**Status**: Pre-release alpha. SurrealDB 3.x support, Python 3.10+ required (3.9 dropped).

**v2.0.0-alpha.1 changes**:
- SurrealDB 3.x feature support added (#230)
- Python 3.9 dropped; minimum is now Python 3.10
- Fixed WebSocket session transaction ID bug (#236)
- Added musl Linux support for Alpine/container deployments (#241)
- Improved error handling with structured error types (#233)
- Pydantic Logfire instrumentation with code examples (#229)
- README and dev docs moved to CONTRIBUTING.md (#243)

### Installation

```bash
pip install surrealdb
```

### Synchronous API

```python
from surrealdb import Surreal

# Context manager ensures clean connection lifecycle
with Surreal("ws://localhost:8000/rpc") as db:
    db.signin({"username": "root", "password": "root"})
    db.use("test", "test")

    # Create
    person = db.create("person", {"name": "Alice", "age": 30})

    # Create with specific ID
    db.create("person:alice", {"name": "Alice", "age": 30})

    # Select all
    people = db.select("person")

    # Select one
    alice = db.select("person:alice")

    # Update (full replace)
    db.update("person:alice", {"name": "Alice Smith", "age": 31})

    # Merge (partial update)
    db.merge("person:alice", {"age": 32})

    # Delete
    db.delete("person:alice")

    # Query with parameters
    result = db.query(
        "SELECT * FROM person WHERE age > $min_age",
        {"min_age": 25}
    )

    # Raw query
    result = db.query("SELECT * FROM person")
```

### Asynchronous API

```python
import asyncio
from surrealdb import AsyncSurreal

async def main():
    async with AsyncSurreal("ws://localhost:8000/rpc") as db:
        await db.signin({"username": "root", "password": "root"})
        await db.use("test", "test")

        # All CRUD operations are async
        person = await db.create("person", {"name": "Bob", "age": 25})
        people = await db.select("person")
        result = await db.query("SELECT * FROM person WHERE age > $min", {"min": 20})

asyncio.run(main())
```

### Embedded Connections

```python
# In-memory (data lost when process exits)
async with AsyncSurreal("memory") as db:
    await db.use("test", "test")
    await db.create("person", {"name": "Alice"})

# SurrealKV persistent storage
async with AsyncSurreal("surrealkv://mydb") as db:
    await db.use("test", "test")
    await db.create("person", {"name": "Alice"})

# RocksDB persistent storage
async with AsyncSurreal("rocksdb://mydb") as db:
    await db.use("test", "test")
    await db.create("person", {"name": "Alice"})
```

### Authentication Patterns

```python
# Root authentication
db.signin({"username": "root", "password": "root"})

# Namespace authentication
db.signin({
    "namespace": "my_ns",
    "username": "ns_user",
    "password": "ns_pass",
})

# Database authentication
db.signin({
    "namespace": "my_ns",
    "database": "my_db",
    "username": "db_user",
    "password": "db_pass",
})

# Record user authentication
token = db.signin({
    "namespace": "my_ns",
    "database": "my_db",
    "access": "user_access",
    "variables": {
        "email": "user@example.com",
        "password": "secret",
    },
})

# Sign up
token = db.signup({
    "namespace": "my_ns",
    "database": "my_db",
    "access": "user_access",
    "variables": {
        "email": "new@example.com",
        "password": "new_pass",
    },
})

# Token-based authentication
db.authenticate(token)
```

### Sessions and Transactions (WebSocket only)

```python
# Transactions are only available over WebSocket connections
with Surreal("ws://localhost:8000/rpc") as db:
    db.signin({"username": "root", "password": "root"})
    db.use("test", "test")

    # Run multiple statements atomically
    result = db.query("""
        BEGIN TRANSACTION;
        CREATE account:alice SET balance = 100;
        CREATE account:bob SET balance = 50;
        UPDATE account:alice SET balance -= 25;
        UPDATE account:bob SET balance += 25;
        COMMIT TRANSACTION;
    """)
```

### Pydantic and Dataclass Mapping

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class Person:
    name: str
    age: int
    email: Optional[str] = None

# Query results can be mapped to dataclasses
result = db.query("SELECT * FROM person")
people = [Person(**record) for record in result]
```

### Pydantic Logfire Observability

The Python SDK integrates with Pydantic Logfire for tracing and observability of database operations. Refer to the Logfire documentation for setup details.

---

## Go SDK

**Package**: `github.com/surrealdb/surrealdb.go`
**Repository**: github.com/surrealdb/surrealdb.go

### Installation

```bash
go get github.com/surrealdb/surrealdb.go
```

### Connection

```go
package main

import (
    "context"
    "fmt"
    surrealdb "github.com/surrealdb/surrealdb.go"
)

func main() {
    ctx := context.Background()

    // WebSocket connection
    db, err := surrealdb.New("ws://localhost:8000")
    if err != nil {
        panic(err)
    }
    defer db.Close()

    // HTTP connection
    db, err = surrealdb.New("http://localhost:8000")
    if err != nil {
        panic(err)
    }

    // Embedded in-memory
    db, err = surrealdb.New("mem://")

    // Embedded on-disk
    db, err = surrealdb.New("surrealkv://path.db")
}
```

### Authentication and Namespace Selection

```go
// Sign in
_, err = db.Signin(ctx, &surrealdb.Auth{
    Username: "root",
    Password: "root",
})
if err != nil {
    panic(err)
}

// Select namespace and database
err = db.Use(ctx, "my_ns", "my_db")
if err != nil {
    panic(err)
}
```

### CRUD with Struct Mapping

```go
type Person struct {
    ID    string `json:"id,omitempty"`
    Name  string `json:"name"`
    Age   int    `json:"age"`
    Email string `json:"email,omitempty"`
}

// Create
person, err := surrealdb.Create[Person](db, ctx, "person", Person{
    Name: "Alice",
    Age:  30,
})

// Select all
people, err := surrealdb.Select[[]Person](db, ctx, "person")

// Select one
alice, err := surrealdb.Select[Person](db, ctx, "person:alice")

// Update (full replace)
updated, err := surrealdb.Update[Person](db, ctx, "person:alice", Person{
    Name:  "Alice Smith",
    Age:   31,
    Email: "alice@example.com",
})

// Merge (partial update)
merged, err := surrealdb.Merge[Person](db, ctx, "person:alice", map[string]interface{}{
    "age": 32,
})

// Delete
err = db.Delete(ctx, "person:alice")

// Query
results, err := surrealdb.Query[[]Person](db, ctx,
    "SELECT * FROM person WHERE age > $min_age",
    map[string]interface{}{"min_age": 25},
)
```

### Context-Based Operations

All Go SDK operations accept a `context.Context` parameter, enabling timeout control, cancellation propagation, and deadline management.

```go
ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
defer cancel()

people, err := surrealdb.Select[[]Person](db, ctx, "person")
if err != nil {
    // Handle timeout or cancellation
}
```

---

## Rust SDK

**Crate**: `surrealdb`
**Repository**: github.com/surrealdb/surrealdb

### Cargo.toml

```toml
[dependencies]
surrealdb = "3"
tokio = { version = "1", features = ["full"] }
serde = { version = "1", features = ["derive"] }
```

### Connection

```rust
use surrealdb::Surreal;
use surrealdb::engine::remote::ws::Ws;
use surrealdb::engine::remote::http::Http;
use surrealdb::engine::local::{Mem, RocksDb, SurrealKv};

// WebSocket
let db = Surreal::new::<Ws>("localhost:8000").await?;

// HTTP
let db = Surreal::new::<Http>("localhost:8000").await?;

// Embedded in-memory
let db = Surreal::new::<Mem>(()).await?;

// Embedded RocksDB
let db = Surreal::new::<RocksDb>("path.db").await?;

// Embedded SurrealKV
let db = Surreal::new::<SurrealKv>("path.db").await?;
```

### Authentication

```rust
use surrealdb::opt::auth::Root;

db.signin(Root {
    username: "root",
    password: "root",
}).await?;

db.use_ns("my_ns").use_db("my_db").await?;
```

### CRUD with Serde

```rust
use serde::{Deserialize, Serialize};
use surrealdb::RecordId;

#[derive(Debug, Serialize, Deserialize)]
struct Person {
    name: String,
    age: u32,
    email: Option<String>,
}

#[derive(Debug, Deserialize)]
struct Record {
    id: RecordId,
}

// Create
let created: Vec<Record> = db.create("person")
    .content(Person {
        name: "Alice".to_string(),
        age: 30,
        email: None,
    })
    .await?;

// Create with specific ID
let alice: Option<Record> = db.create(("person", "alice"))
    .content(Person {
        name: "Alice".to_string(),
        age: 30,
        email: None,
    })
    .await?;

// Select all
let people: Vec<Person> = db.select("person").await?;

// Select one
let alice: Option<Person> = db.select(("person", "alice")).await?;

// Update
let updated: Option<Person> = db.update(("person", "alice"))
    .content(Person {
        name: "Alice Smith".to_string(),
        age: 31,
        email: Some("alice@example.com".to_string()),
    })
    .await?;

// Merge
let merged: Option<Person> = db.update(("person", "alice"))
    .merge(serde_json::json!({ "age": 32 }))
    .await?;

// Delete
let _: Option<Person> = db.delete(("person", "alice")).await?;
```

### Queries

```rust
// Parameterized query
let mut result = db.query("SELECT * FROM person WHERE age > $min_age")
    .bind(("min_age", 25))
    .await?;

let people: Vec<Person> = result.take(0)?;

// Multiple statements
let mut result = db.query("SELECT * FROM person; SELECT * FROM order;").await?;
let people: Vec<Person> = result.take(0)?;
let orders: Vec<Order> = result.take(1)?;
```

### Live Queries

```rust
use surrealdb::Notification;
use futures::StreamExt;

let mut stream = db.select("person").live().await?;

while let Some(notification) = stream.next().await {
    let notification: Notification<Person> = notification?;
    match notification.action {
        Action::Create => println!("Created: {:?}", notification.data),
        Action::Update => println!("Updated: {:?}", notification.data),
        Action::Delete => println!("Deleted: {:?}", notification.data),
        _ => {}
    }
}
```

---

## Java SDK

**Package**: Available on Maven Central
**Repository**: github.com/surrealdb/surrealdb.java

### Maven Dependency

```xml
<dependency>
    <groupId>com.surrealdb</groupId>
    <artifactId>surrealdb</artifactId>
    <version>3.0.0</version>
</dependency>
```

### Connection and Authentication

```java
import com.surrealdb.Surreal;

// WebSocket connection
Surreal db = new Surreal();
db.connect("ws://localhost:8000");
db.signin("root", "root");
db.use("my_ns", "my_db");

// HTTP connection
db.connect("http://localhost:8000");
```

### CRUD Operations

```java
// Create
db.create("person", Map.of(
    "name", "Alice",
    "age", 30
));

// Select
List<Map<String, Object>> people = db.select("person");

// Query with parameters
List<Map<String, Object>> results = db.query(
    "SELECT * FROM person WHERE age > $min_age",
    Map.of("min_age", 25)
);

// Update
db.update("person:alice", Map.of(
    "name", "Alice Smith",
    "age", 31
));

// Merge
db.merge("person:alice", Map.of("age", 32));

// Delete
db.delete("person:alice");
```

### Async Operations with CompletableFuture

```java
CompletableFuture<List<Map<String, Object>>> future = db.queryAsync(
    "SELECT * FROM person WHERE age > $min_age",
    Map.of("min_age", 25)
);

future.thenAccept(results -> {
    results.forEach(System.out::println);
}).exceptionally(error -> {
    System.err.println("Query failed: " + error.getMessage());
    return null;
});
```

---

## .NET SDK

**Package**: `SurrealDb.Net` on NuGet
**Repository**: github.com/surrealdb/surrealdb.net

### Installation

```bash
dotnet add package SurrealDb.Net
```

### Basic Usage

```csharp
using SurrealDb.Net;
using SurrealDb.Net.Models;

// Create client
var db = new SurrealDbClient("ws://localhost:8000/rpc");
await db.SignIn(new RootAuth { Username = "root", Password = "root" });
await db.Use("my_ns", "my_db");

// Create
var person = await db.Create("person", new Person
{
    Name = "Alice",
    Age = 30
});

// Select all
var people = await db.Select<Person>("person");

// Query
var results = await db.Query(
    "SELECT * FROM person WHERE age > $min_age",
    new { min_age = 25 }
);

// Dispose
await db.DisposeAsync();
```

### Dependency Injection

```csharp
// In Startup.cs or Program.cs
builder.Services.AddSurreal(options =>
{
    options.Endpoint = "ws://localhost:8000/rpc";
    options.Namespace = "my_ns";
    options.Database = "my_db";
});

// In a service or controller
public class PersonService
{
    private readonly ISurrealDbClient _db;

    public PersonService(ISurrealDbClient db)
    {
        _db = db;
    }

    public async Task<IEnumerable<Person>> GetPeople()
    {
        return await _db.Select<Person>("person");
    }
}
```

### LINQ Integration

```csharp
// Query using LINQ-style expressions where supported
var adults = await db.Select<Person>("person")
    .Where(p => p.Age >= 18)
    .OrderBy(p => p.Name)
    .ToListAsync();
```

---

## PHP SDK

**Package**: `surrealdb/surrealdb.php` on Packagist
**Repository**: github.com/surrealdb/surrealdb.php

### Installation

```bash
composer require surrealdb/surrealdb.php
```

### Basic Usage

```php
use Surreal\Surreal;

$db = new Surreal();

// Connect via WebSocket
$db->connect("ws://localhost:8000/rpc");

// Or via HTTP
$db->connect("http://localhost:8000");

// Authenticate
$db->signin([
    "username" => "root",
    "password" => "root",
]);

$db->use(["namespace" => "my_ns", "database" => "my_db"]);

// Create
$person = $db->create("person", [
    "name" => "Alice",
    "age" => 30,
]);

// Select
$people = $db->select("person");
$alice = $db->select("person:alice");

// Query
$results = $db->query(
    "SELECT * FROM person WHERE age > $min_age",
    ["min_age" => 25]
);

// Update
$db->update("person:alice", [
    "name" => "Alice Smith",
    "age" => 31,
]);

// Merge
$db->merge("person:alice", ["age" => 32]);

// Delete
$db->delete("person:alice");

// Close
$db->close();
```

---

## SDK Selection Guide

### Decision Matrix

| Factor | JS/TS | Python | Go | Rust | Java | .NET | PHP |
|--------|-------|--------|----|------|------|------|-----|
| Embedded engine | Yes | Yes | Yes | Yes | No | No | No |
| WebSocket | Yes | Yes | Yes | Yes | Yes | Yes | Yes |
| HTTP | Yes | Yes | Yes | Yes | Yes | Yes | Yes |
| Live queries | Yes | Yes | Yes | Yes | Limited | Limited | No |
| WASM (browser) | Yes | No | No | No | No | No | No |
| Async API | Yes | Yes | Yes | Yes | Yes | Yes | No |
| Type safety | TS generics | Type hints | Generics | Strong | Generics | Generics | Weak |

### When to Use Each SDK

- **JavaScript/TypeScript**: Web applications, full-stack JS projects, browser-based apps (WASM), serverless functions, real-time apps with live queries.
- **Python**: Data science, machine learning pipelines, scripting, backend APIs (FastAPI/Django), prototyping.
- **Go**: Microservices, high-concurrency servers, CLI tools, cloud-native applications.
- **Rust**: Performance-critical applications, systems programming, embedded databases in Rust apps, when you need direct library integration without network overhead.
- **Java**: Enterprise applications, Spring Boot services, Android development.
- **.NET**: ASP.NET applications, Windows services, enterprise C# codebases, Blazor apps.
- **PHP**: Laravel/Symfony applications, WordPress plugins, traditional web applications.

### Embedded vs Remote Trade-offs

**Embedded** (in-process database):
- No network latency
- Single-process deployment
- No separate database server to manage
- Limited to single-node (no distributed queries)
- Uses process memory for database operations
- Available in: JS/TS (Node.js, WASM), Python, Go, Rust

**Remote** (HTTP/WebSocket to server):
- Shared database across multiple application instances
- Supports TiKV for distributed storage
- Independent scaling of compute and storage
- Network latency overhead
- Requires running SurrealDB server
- Available in: All SDKs

### Performance Characteristics

- **Rust SDK**: Lowest overhead; direct library calls when embedded, minimal serialization.
- **Go SDK**: Low overhead; efficient goroutine-based concurrency.
- **Node.js embedded**: V8 + native bindings; good for I/O-heavy workloads.
- **Python SDK**: Higher overhead due to GIL; use async API for I/O-bound workloads.
- **WASM (browser)**: Runs entirely client-side; performance depends on browser WASM runtime.
