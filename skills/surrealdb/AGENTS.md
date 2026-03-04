# Agent Briefing: surrealdb

Structured reference for AI agents. Minimal prose, maximum signal.

## Quick Start

```bash
# Check if configured
uv run {baseDir}/scripts/onboard.py --check

# Get full capabilities manifest (JSON)
uv run {baseDir}/scripts/onboard.py --agent
```

## Capabilities

| Command | Script | What It Does | When to Use |
|---------|--------|-------------|-------------|
| `doctor` | `scripts/doctor.py` | Health check: CLI, connectivity, version, storage | First run, troubleshooting, verifying environment |
| `doctor --check` | `scripts/doctor.py` | Quick pass/fail (exit code only) | CI pipelines, pre-flight checks |
| `schema introspect` | `scripts/schema.py` | Full schema dump (tables, fields, indexes, events) | Understanding existing database structure |
| `schema tables` | `scripts/schema.py` | List tables with field counts and indexes | Quick overview of database contents |
| `schema table <name>` | `scripts/schema.py` | Inspect a single table in detail | Debugging a specific table definition |
| `schema export` | `scripts/schema.py` | Export schema as SurrealQL or JSON | Reproducible deployments, version control |
| `onboard --agent` | `scripts/onboard.py` | JSON capabilities manifest | Agent self-discovery, integration setup |
| `onboard --check` | `scripts/onboard.py` | Verify prerequisites | First run, CI |

## Decision Trees

### "User wants to create a SurrealDB project"

```
1. Run doctor to verify environment:
   uv run {baseDir}/scripts/doctor.py

2. Is surreal CLI installed?
   NO  -> brew install surrealdb/tap/surreal (or see https://surrealdb.com/install)
   YES -> Continue

3. Choose storage engine (LOCAL DEV -- use scoped credentials in production):
   Development     -> surreal start memory --user root --pass root
   Single-node     -> surreal start rocksdb://data/mydb.db --user root --pass root
   Time-travel     -> surreal start surrealkv://data/mydb --user root --pass root
   Distributed     -> surreal start tikv://... --user root --pass root

4. Design schema:
   -> Reference rules/data-modeling.md for table/field patterns
   -> Reference rules/graph-queries.md if domain has relationships
   -> Reference rules/vector-search.md if semantic search needed

5. Apply schema (local dev credentials -- use scoped users in production):
   surreal import --endpoint $SURREAL_ENDPOINT --user root --pass root \
     --ns <ns> --db <db> schema.surql

6. Verify:
   uv run {baseDir}/scripts/schema.py introspect
```

### "User has a data modeling question"

```
What kind of data?
  Documents/records    -> rules/data-modeling.md (record IDs, field types, schema modes)
  Relationships/graphs -> rules/graph-queries.md (RELATE, edge tables, traversal)
  Vector embeddings    -> rules/vector-search.md (vector fields, HNSW indexes, similarity)
  Time-series          -> rules/data-modeling.md (datetime fields, range queries, aggregations)
  Geospatial           -> rules/data-modeling.md (geometry types, geo functions, spatial indexes)
  Mixed/multi-model    -> rules/data-modeling.md + relevant specialized rules

Need schema validation?
  YES -> DEFINE TABLE ... SCHEMAFULL (strict, all fields must be defined)
  PARTIAL -> DEFINE TABLE ... SCHEMALESS (flexible, defined fields are validated)
```

### "User needs to optimize performance"

```
1. Check current schema and indexes:
   uv run {baseDir}/scripts/schema.py introspect

2. Identify bottleneck type:
   Slow queries        -> rules/performance.md (EXPLAIN, index strategies)
   High write latency  -> rules/performance.md (batch operations, storage engine)
   Memory pressure     -> rules/deployment.md (resource limits, storage engine selection)
   Connection issues   -> rules/sdks.md (connection pooling, WebSocket vs HTTP)

3. Index audit:
   Missing index on filtered field  -> DEFINE INDEX ... ON TABLE ... FIELDS ...
   Full-text search slow             -> DEFINE INDEX ... SEARCH ANALYZER ...
   Vector search slow                -> DEFINE INDEX ... HNSW DIMENSION ... DIST ...

4. Storage engine review:
   Memory       -> Fast but volatile, development only
   RocksDB      -> General purpose, good read/write balance
   SurrealKV    -> Time-travel queries, versioned data
   TiKV         -> Distributed, horizontal scaling
```

### "User wants to write WASM extensions"

```
1. Reference rules/surrealism.md for Surrealism module system
2. Prerequisites: Rust toolchain, wasm32-unknown-unknown target
3. Workflow:
   a. Create Rust project with surrealism SDK
   b. Implement custom functions/analyzers
   c. Compile to WASM
   d. Deploy to SurrealDB instance
   e. Use in SurrealQL queries via custom function syntax
```

### "User migrating from another database"

```
Source database?
  PostgreSQL/MySQL/SQL -> rules/data-modeling.md (relational mapping to SurrealDB)
                          rules/surreal-sync.md (CDC migration with Surreal-Sync)
  MongoDB/CouchDB      -> rules/data-modeling.md (document model, record IDs)
                          rules/surreal-sync.md (CDC migration)
  Neo4j/graph DB       -> rules/graph-queries.md (edge table mapping, traversal equivalents)
  SurrealDB v2         -> rules/surrealql.md (v2->v3 breaking changes)
                          surreal export/import for data migration
  Redis/key-value      -> rules/data-modeling.md (record ID patterns, schemaless mode)

Migration steps:
  1. Map source schema to SurrealDB tables/fields
  2. Use Surreal-Sync for CDC if available (rules/surreal-sync.md)
  3. Or export -> transform -> import with surreal CLI
  4. Verify with schema introspection
```

## Common Workflows

### 1. Verify environment and connect

```bash
# Health check
uv run {baseDir}/scripts/doctor.py

# Start dev server (LOCAL DEV ONLY -- use scoped credentials in production)
surreal start memory --user root --pass root --bind 127.0.0.1:8000

# Connect (local dev)
surreal sql --endpoint http://localhost:8000 --user root --pass root --ns test --db test
```

### 2. Design and apply a schema

```surql
-- Define namespace and database context
USE NS myapp DB production;

-- Define a schemafull table with fields and indexes
DEFINE TABLE user SCHEMAFULL;
DEFINE FIELD name ON TABLE user TYPE string;
DEFINE FIELD email ON TABLE user TYPE string ASSERT string::is::email($value);
DEFINE FIELD created ON TABLE user TYPE datetime DEFAULT time::now();
DEFINE INDEX idx_user_email ON TABLE user FIELDS email UNIQUE;

-- Define a graph edge table
DEFINE TABLE follows SCHEMAFULL TYPE RELATION IN user OUT user;
DEFINE FIELD since ON TABLE follows TYPE datetime DEFAULT time::now();

-- Define permissions
DEFINE TABLE post SCHEMALESS
  PERMISSIONS
    FOR select WHERE published = true OR author = $auth.id
    FOR create, update WHERE author = $auth.id
    FOR delete WHERE author = $auth.id OR $auth.role = 'admin';
```

```bash
surreal import --endpoint http://localhost:8000 --user root --pass root \
  --ns myapp --db production schema.surql

uv run {baseDir}/scripts/schema.py introspect
```

### 3. Set up vector search

```surql
-- Define table with vector field
DEFINE TABLE document SCHEMALESS;
DEFINE FIELD content ON TABLE document TYPE string;
DEFINE FIELD embedding ON TABLE document TYPE array<float> ASSERT array::len($value) = 1536;

-- Create HNSW vector index
DEFINE INDEX idx_doc_embedding ON TABLE document FIELDS embedding
  HNSW DIMENSION 1536 DIST COSINE;

-- Query by similarity
SELECT *, vector::similarity::cosine(embedding, $query_vec) AS score
  FROM document
  WHERE embedding <|10,40|> $query_vec
  ORDER BY score DESC
  LIMIT 10;
```

### 4. Graph traversal queries

```surql
-- Create records and relationships
CREATE person:alice SET name = 'Alice', role = 'engineer';
CREATE person:bob SET name = 'Bob', role = 'manager';
CREATE project:atlas SET name = 'Atlas', status = 'active';

RELATE person:alice->works_on->project:atlas SET since = d'2025-01-15';
RELATE person:bob->manages->project:atlas;
RELATE person:bob->mentors->person:alice SET topic = 'architecture';

-- Traverse outgoing edges
SELECT ->works_on->project.name AS projects FROM person:alice;

-- Traverse incoming edges
SELECT <-works_on<-person.name AS engineers FROM project:atlas;

-- Multi-hop traversal
SELECT ->mentors->person->works_on->project.name AS mentee_projects FROM person:bob;

-- Bidirectional traversal
SELECT <->mentors<->person.name AS mentorship_peers FROM person:alice;
```

### 5. Production deployment checklist

```bash
# 1. Choose storage engine (see rules/deployment.md)
# NOTE: 0.0.0.0 is correct for production servers behind a firewall/load balancer.
# For local dev, use 127.0.0.1 instead.
surreal start rocksdb://data/production.db \
  --user $SURREAL_USER --pass $SURREAL_PASS \
  --bind 0.0.0.0:8000 \
  --log info

# 2. Apply schema
surreal import --endpoint $SURREAL_ENDPOINT \
  --user $SURREAL_USER --pass $SURREAL_PASS \
  --ns production --db main schema.surql

# 3. Set up access control (see rules/security.md)
# 4. Configure backups
surreal export --endpoint $SURREAL_ENDPOINT \
  --user $SURREAL_USER --pass $SURREAL_PASS \
  --ns production --db main backup-$(date +%Y%m%d).surql

# 5. Verify
uv run {baseDir}/scripts/doctor.py --endpoint $SURREAL_ENDPOINT
uv run {baseDir}/scripts/schema.py introspect --endpoint $SURREAL_ENDPOINT
```

## Rules Manifest

| Rule | Description |
|------|-------------|
| `rules/surrealql.md` | Complete SurrealQL language reference: statements, functions, operators, idioms, v2-to-v3 migration notes |
| `rules/data-modeling.md` | Schema design patterns: record IDs, field types, schemafull vs schemaless, normalization, multi-model strategies, time-series, geospatial |
| `rules/graph-queries.md` | Graph edge creation with RELATE, traversal operators (-> <- <->), path expressions, recursive queries, filtering edges, aggregation |
| `rules/vector-search.md` | Vector field definitions, HNSW and brute-force indexes, distance metrics, similarity functions, RAG pipeline patterns, hybrid search |
| `rules/security.md` | Row-level permissions, DEFINE ACCESS (JWT, record), DEFINE USER, namespace/database/table scoping, $auth/$session variables, authentication flows |
| `rules/deployment.md` | Installation methods, storage engines (memory, RocksDB, SurrealKV, TiKV), Docker, Kubernetes Helm charts, production hardening, backup/restore, monitoring |
| `rules/performance.md` | Index strategies (unique, search, HNSW, MTree), EXPLAIN for query analysis, batch operations, connection pooling, storage engine trade-offs, resource limits |
| `rules/sdks.md` | Official SDK usage for JS/TS, Python, Go, Rust, Java, .NET, C, PHP, Dart: connection setup, authentication, CRUD, live queries, typed records |
| `rules/surrealism.md` | Surrealism WASM extension system (new in v3): Rust SDK, custom functions, custom analyzers, module lifecycle, deployment |
| `rules/surrealist.md` | Surrealist IDE/GUI: schema designer, query editor, graph visualizer, table explorer, connection management |
| `rules/surreal-sync.md` | Surreal-Sync CDC tool: source connectors, target connectors, migration workflows, incremental sync, schema translation |
| `rules/surrealfs.md` | SurrealFS AI agent filesystem: file storage and retrieval, metadata management, directory structures, agent integration patterns |

## Configuration Requirements

| Requirement | How to Check | How to Fix |
|-------------|-------------|------------|
| surreal CLI | `surreal version` | `brew install surrealdb/tap/surreal` or see [install docs](https://surrealdb.com/install) |
| Python 3.10+ | `python3 --version` | Install from python.org or use system package manager |
| uv runtime | `which uv` | `brew install uv` or `pip install uv` |
| SurrealDB server | `uv run {baseDir}/scripts/doctor.py` | `surreal start memory --user root --pass root` |

Environment variables (optional, all have defaults):

| Variable | Default | Description |
|----------|---------|-------------|
| `SURREAL_ENDPOINT` | `http://localhost:8000` | SurrealDB server URL |
| `SURREAL_USER` | `root` | Authentication username |
| `SURREAL_PASS` | `root` | Authentication password |
| `SURREAL_NS` | `test` | Default namespace |
| `SURREAL_DB` | `test` | Default database |

## Output Contracts

All scripts: **stderr** = human-readable (Rich), **stdout** = JSON.

### `doctor.py`

```json
{
  "status": "healthy",
  "checks": {
    "cli_installed": true,
    "cli_version": "3.0.0",
    "server_reachable": true,
    "auth_valid": true,
    "namespace_exists": true,
    "database_exists": true,
    "storage_engine": "rocksdb"
  },
  "issues": []
}
```

### `doctor.py` (with issues)

```json
{
  "status": "unhealthy",
  "checks": {
    "cli_installed": true,
    "cli_version": "3.0.0",
    "server_reachable": false,
    "auth_valid": false,
    "namespace_exists": false,
    "database_exists": false,
    "storage_engine": null
  },
  "issues": ["Server not reachable at http://localhost:8000"]
}
```

### `schema.py introspect`

```json
{
  "namespace": "test",
  "database": "test",
  "tables": [
    {
      "name": "user",
      "type": "normal",
      "schema_mode": "schemafull",
      "fields": [
        {"name": "name", "type": "string", "default": null, "assert": null},
        {"name": "email", "type": "string", "default": null, "assert": "string::is::email($value)"}
      ],
      "indexes": [
        {"name": "idx_user_email", "fields": ["email"], "unique": true, "search": false, "vector": false}
      ],
      "events": [],
      "permissions": {"select": "FULL", "create": "FULL", "update": "FULL", "delete": "FULL"}
    }
  ],
  "accesses": [],
  "users": []
}
```

### `schema.py tables`

```json
{
  "tables": [
    {"name": "user", "type": "normal", "fields": 5, "indexes": 2, "events": 0},
    {"name": "follows", "type": "relation", "fields": 1, "indexes": 0, "events": 0},
    {"name": "post", "type": "normal", "fields": 8, "indexes": 3, "events": 1}
  ]
}
```

### `onboard.py --agent`

```json
{
  "skill": "surrealdb",
  "version": "1.0.0",
  "capabilities": ["surrealql", "data-modeling", "graph-queries", "vector-search", "security", "deployment", "performance", "sdks", "surrealism", "surrealist", "surreal-sync", "surrealfs"],
  "scripts": ["doctor.py", "schema.py", "onboard.py"],
  "rules": ["surrealql.md", "data-modeling.md", "graph-queries.md", "vector-search.md", "security.md", "deployment.md", "performance.md", "sdks.md", "surrealism.md", "surrealist.md", "surreal-sync.md", "surrealfs.md"],
  "prerequisites": {
    "surreal_cli": true,
    "python": true,
    "uv": true,
    "server_reachable": true
  }
}
```

## Error Handling

| Exit Code | Meaning | Recovery |
|-----------|---------|----------|
| 0 | Success | N/A |
| 1 | Error | Check stderr for details |

Common errors:

- **surreal CLI not found**: Install with `brew install surrealdb/tap/surreal` or see https://surrealdb.com/install
- **Server not reachable**: Start a server with `surreal start memory --user root --pass root`
- **Authentication failed**: Verify `SURREAL_USER` and `SURREAL_PASS` environment variables
- **Namespace/database not found**: Create with `DEFINE NAMESPACE ...` / `DEFINE DATABASE ...` or use `USE NS ... DB ...` in SurrealQL
- **Schema import failed**: Check SurrealQL syntax; run `surreal sql` to test queries interactively
- **Permission denied**: Check table-level permissions in `rules/security.md`

## Version Information

| Component | Version |
|-----------|---------|
| SurrealDB target | 3.0.0+ |
| Skill version | 1.1.1 |
| SurrealQL compat | SurrealDB 3.x |
| Python requirement | 3.10+ |

## Source Provenance

This skill was built from the following upstream sources. Use `check_upstream.py`
to detect what changed since this snapshot for incremental updates.

```bash
uv run {baseDir}/scripts/check_upstream.py          # full diff report
uv run {baseDir}/scripts/check_upstream.py --stale   # only changed repos
```

| Repository | Release | SHA (short) | Snapshot Date | Rules Affected |
|------------|---------|-------------|---------------|----------------|
| surrealdb/surrealdb | v3.0.0 | `2e0a61fd4daf` | 2026-02-19 | surrealql, data-modeling, security, performance, deployment, surrealism |
| surrealdb/surrealist | v3.7.2 | `a87e89e23796` | 2026-02-21 | surrealist |
| surrealdb/surrealdb.js | v1.3.2 | `48894dfe70bd` | 2026-02-20 | sdks |
| surrealdb/surrealdb.js (v2 beta) | v2.0.0-beta.1 | `48894dfe70bd` | 2026-02-20 | sdks |
| surrealdb/surrealdb.py | v1.0.8 | `1ff4470e6ec0` | 2026-02-03 | sdks |
| surrealdb/surrealdb.go | v1.3.0 | `89d0f8d1b4c6` | 2026-02-12 | sdks |
| surrealdb/surreal-sync | v0.3.4 | `8166b2b041b1` | 2026-02-12 | surreal-sync |
| surrealdb/surrealfs | -- | `0008a3a94dbe` | 2026-01-29 | surrealfs |

Documentation: [surrealdb.com/docs](https://surrealdb.com/docs) snapshot 2026-02-22.

Full provenance data: `SOURCES.json` (machine-readable).
