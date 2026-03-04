# surreal-skills

[![CI](https://github.com/24601/surreal-skills/actions/workflows/ci.yml/badge.svg)](https://github.com/24601/surreal-skills/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-1.1.1-blue.svg)](https://github.com/24601/surreal-skills/releases)
[![skills.sh](https://img.shields.io/badge/skills.sh-surrealdb-purple.svg)](https://skills.sh)

Expert SurrealDB 3 skill for AI coding agents. Complete coverage of SurrealQL, multi-model data modeling, graph traversal, vector search, security, deployment, performance tuning, SDK integration, WASM extensions, and the full SurrealDB ecosystem.

## Features

- **SurrealQL mastery** -- Complete language reference with statements, functions, operators, and idioms
- **Multi-model data modeling** -- Document, graph, vector, relational, time-series, and geospatial patterns in a single schema
- **Graph queries** -- First-class edge creation and traversal without JOINs
- **Vector search** -- HNSW indexes, similarity functions, and RAG pipeline patterns
- **Security** -- Row-level permissions, JWT auth, namespace/database/record-level access control
- **Deployment** -- Storage engine selection, Docker, Kubernetes, production hardening
- **Performance** -- Index strategies, EXPLAIN analysis, batch operations, connection pooling
- **9+ SDK integrations** -- JavaScript/TypeScript, Python, Go, Rust, Java, .NET, C, PHP, Dart
- **Surrealism WASM extensions** -- Custom functions and analyzers compiled from Rust (new in v3)
- **Full ecosystem** -- Surrealist IDE, Surreal-Sync CDC, SurrealFS agent filesystem, SurrealML
- **Health checks and introspection** -- Doctor script and schema introspection for any SurrealDB instance
- **Universal agent support** -- Works with 30+ AI coding agents via skills.sh

## Installation

### Claude Code (recommended)

**Option 1 -- Install as a Claude Code skill (global)**

```bash
npx skills add 24601/surreal-skills -a claude-code -g -y
```

This installs the skill globally so it is available in every Claude Code session. The `-g` flag installs globally, `-y` auto-confirms prompts.

**Option 2 -- Install per-project via CLAUDE.md**

Clone the repo and reference it from your project's `CLAUDE.md`:

```bash
git clone https://github.com/24601/surreal-skills.git ~/.claude/skills/surrealdb
```

Then add to your project's `CLAUDE.md` (or `~/.claude/CLAUDE.md` for global):

```markdown
# SurrealDB Skill

@import ~/.claude/skills/surrealdb/AGENTS.md
```

Or inline the reference:

```markdown
# SurrealDB Skill

For SurrealDB work, read the rules at ~/.claude/skills/surrealdb/rules/ and
use the scripts at ~/.claude/skills/surrealdb/scripts/ for health checks
and schema introspection.
```

**Option 3 -- Add as a Claude Code custom slash command**

Create `~/.claude/commands/surrealdb.md`:

```markdown
Load the SurrealDB 3 skill from ~/.claude/skills/surrealdb/AGENTS.md
and use its rules for all SurrealDB architecture, development, and operations tasks.
Available rules: surrealql, data-modeling, graph-queries, vector-search, security,
deployment, performance, sdks, surrealism, surrealist, surreal-sync, surrealfs.
```

Then invoke with `/surrealdb` in any Claude Code session.

**Option 4 -- Project-scoped slash commands**

Add SurrealDB-specific commands to your project:

```bash
mkdir -p .claude/commands
```

Create `.claude/commands/surreal-doctor.md`:

```markdown
Run the SurrealDB health check: uv run ~/.claude/skills/surrealdb/scripts/doctor.py
Report any issues found and suggest fixes based on the deployment rules.
```

Create `.claude/commands/surreal-schema.md`:

```markdown
Introspect the current SurrealDB schema: uv run ~/.claude/skills/surrealdb/scripts/schema.py introspect
Analyze the output using the data-modeling rules and suggest improvements.
```

### Other AI Agents

```bash
# skills.sh (universal -- works with all supported agents)
npx skills add 24601/surreal-skills

# Amp
npx skills add 24601/surreal-skills -a amp -g -y

# Codex
npx skills add 24601/surreal-skills -a codex -g -y

# Gemini CLI
npx skills add 24601/surreal-skills -a gemini-cli -g -y

# OpenCode
npx skills add 24601/surreal-skills -a opencode -g -y

# Pi (badlogic/pi-mono)
npx skills add 24601/surreal-skills -a pi -g -y

# OpenClaw / Clawdbot
npx skills add 24601/surreal-skills -a openclaw -g -y
```

### GitHub Copilot (native agent skills)

Copilot supports the [Agent Skills standard](https://agentskills.io/) natively in VS Code,
Copilot CLI, and the Copilot coding agent. This skill ships a Copilot-native
`.github/skills/surrealdb/SKILL.md` that Copilot auto-loads when your prompt
is SurrealDB-related.

**Option 1 -- Project-level (recommended for teams)**

Copy the entire skill into your project's `.github/skills/` directory:

```bash
# From the surreal-skills repo
cp -r .github/skills/surrealdb <your-project>/.github/skills/surrealdb
cp -r rules/ <your-project>/.github/skills/surrealdb/rules/
```

Copilot discovers this automatically -- no config needed. Type `/surrealdb` in
chat or let Copilot auto-load it when it detects SurrealQL context.

**Option 2 -- Personal (all projects)**

Clone into `~/.copilot/skills/`:

```bash
git clone https://github.com/24601/surreal-skills.git ~/.copilot/skills/surrealdb
```

Or add a custom search location in VS Code settings:

```json
{
  "chat.agentSkillsLocations": [
    "~/.copilot/skills"
  ]
}
```

**Option 3 -- Use `/skills` menu**

Type `/skills` in Copilot chat to open the Configure Skills menu, then browse
to the cloned `surrealdb` directory.

### Other IDE Integrations

```bash
# Cursor -- add skill to .cursor/skills/ (same Agent Skills standard)
cp -r .github/skills/surrealdb <your-project>/.cursor/skills/surrealdb

# Windsurf -- append AGENTS.md to .windsurfrules
cat AGENTS.md >> .windsurfrules

# Cline / Continue -- reference in your config
# Add the AGENTS.md path to your system prompt configuration
```

### Manual installation

```bash
# Clone to any location
git clone https://github.com/24601/surreal-skills.git ~/.claude/skills/surrealdb

# Verify installation
uv run ~/.claude/skills/surrealdb/scripts/doctor.py --check
```

## Quick Start

> **Credential warning**: Examples below use `root/root` for **local development
> only**. Never use default credentials against production or shared instances.

```bash
# Start SurrealDB in-memory for LOCAL DEVELOPMENT ONLY
surreal start memory --user root --pass root --bind 127.0.0.1:8000

# Connect via CLI REPL (local dev)
surreal sql --endpoint http://localhost:8000 --user root --pass root --ns test --db test

# Create records with SurrealQL
CREATE person:alice SET name = 'Alice', email = 'alice@example.com';
CREATE person:bob SET name = 'Bob', email = 'bob@example.com';

# Create graph edges
RELATE person:alice->follows->person:bob SET since = time::now();

# Traverse the graph
SELECT ->follows->person.name AS following FROM person:alice;

# Run the health check
uv run scripts/doctor.py
```

## Architecture

```
surreal-skills/
  SKILL.md              # Skill manifest (frontmatter + body)
  AGENTS.md             # Structured agent briefing
  README.md             # This file
  LICENSE               # MIT license
  scripts/
    onboard.py          # Setup wizard / capabilities manifest
    doctor.py           # Health check (CLI, server, auth, storage)
    schema.py           # Schema introspection and export
  rules/
    surrealql.md        # SurrealQL language reference
    data-modeling.md    # Multi-model schema design patterns
    graph-queries.md    # Graph traversal and RELATE patterns
    vector-search.md    # Vector indexes, similarity search, RAG
    security.md         # Permissions, auth, access control
    deployment.md       # Storage engines, Docker, K8s, production
    performance.md      # Indexes, EXPLAIN, optimization
    sdks.md             # Official SDK integration (9+ languages)
    surrealism.md       # WASM extension system (new in v3)
    surrealist.md       # Surrealist IDE/GUI
    surreal-sync.md     # CDC migration tool
    surrealfs.md        # AI agent filesystem
```

## Rules

| Rule | Description |
|------|-------------|
| `surrealql.md` | Complete SurrealQL language reference: CREATE, SELECT, UPDATE, DELETE, RELATE, INSERT, UPSERT, LIVE SELECT, DEFINE, REMOVE, INFO, subqueries, transactions, futures, all built-in functions, v2-to-v3 migration notes |
| `data-modeling.md` | Schema design patterns: record IDs (typed, generated, composite), field types, schemafull vs schemaless, normalization strategies, multi-model design (document + graph + vector in one schema), time-series and geospatial data |
| `graph-queries.md` | Graph edge creation with RELATE, traversal operators (-> outgoing, <- incoming, <-> bidirectional), path expressions, recursive queries, filtering and aggregation on edges, graph-specific DEFINE TABLE TYPE RELATION |
| `vector-search.md` | Vector field definitions, HNSW and brute-force index creation, distance metrics (cosine, euclidean, manhattan, minkowski), vector::similarity functions, RAG pipeline patterns, hybrid search combining vector + metadata filtering |
| `security.md` | Row-level permissions with WHERE predicates, DEFINE ACCESS for JWT and record-based auth, DEFINE USER for system users, namespace/database/table permission scoping, $auth and $session runtime variables, authentication flow patterns |
| `deployment.md` | Installation methods (curl, brew, Docker, binary), storage engine selection (memory, RocksDB, SurrealKV with time-travel, TiKV for distributed), Docker Compose and Kubernetes Helm charts, production hardening, backup/restore, log levels, monitoring |
| `performance.md` | Index strategies (unique, full-text search analyzers, HNSW vector, MTree), EXPLAIN statement for query analysis, batch operations, connection pooling, storage engine trade-offs by workload, parallel queries, resource limits, compute-to-storage ratios |
| `sdks.md` | Official SDK usage for JavaScript/TypeScript (Node, Deno, Bun, browser), Python, Go, Rust, Java, .NET, C, PHP, Dart: connection setup (HTTP vs WebSocket), authentication flows, CRUD operations, live query subscriptions, typed record handling, error patterns |
| `surrealism.md` | Surrealism WASM extension system introduced in SurrealDB 3: Rust SDK for authoring, custom function registration, custom analyzer creation, module compilation to wasm32-unknown-unknown, deployment to running instances, versioning, testing |
| `surrealist.md` | Surrealist IDE and GUI: schema designer with visual table editing, query editor with syntax highlighting and auto-complete, graph visualizer for relationships, table explorer, connection profiles, import/export, embedding in applications |
| `surreal-sync.md` | Surreal-Sync CDC migration tool: source connectors (PostgreSQL, MySQL, MongoDB, etc.), SurrealDB as target, incremental change data capture, schema translation rules, migration workflow orchestration, conflict resolution, monitoring |
| `surrealfs.md` | SurrealFS AI agent filesystem: file storage backed by SurrealDB, metadata management with SurrealQL queries, directory structures, file versioning, agent-friendly API patterns, integration with AI agent frameworks |

## Scripts

| Script | Usage | Description |
|--------|-------|-------------|
| `onboard.py` | `uv run scripts/onboard.py --check` | Verify prerequisites (surreal CLI, Python, uv, server connectivity) |
| `onboard.py` | `uv run scripts/onboard.py --agent` | Output JSON capabilities manifest for agent integration |
| `doctor.py` | `uv run scripts/doctor.py` | Full health check: CLI version, server reachability, auth, namespace, database, storage engine |
| `doctor.py` | `uv run scripts/doctor.py --check` | Quick pass/fail (exit code 0 = healthy, 1 = issues) |
| `doctor.py` | `uv run scripts/doctor.py --endpoint URL` | Check a specific SurrealDB endpoint |
| `schema.py` | `uv run scripts/schema.py introspect` | Full schema dump of all tables, fields, indexes, events, accesses |
| `schema.py` | `uv run scripts/schema.py tables` | List all tables with field/index counts |
| `schema.py` | `uv run scripts/schema.py table <name>` | Inspect a single table in detail |
| `schema.py` | `uv run scripts/schema.py export --format surql` | Export schema as reproducible DEFINE statements |
| `schema.py` | `uv run scripts/schema.py export --format json` | Export schema as structured JSON |
| `check_upstream.py` | `uv run scripts/check_upstream.py` | Compare upstream repos against skill snapshot; shows what changed |
| `check_upstream.py` | `uv run scripts/check_upstream.py --stale` | Only show repos with new commits since snapshot |
| `check_upstream.py` | `uv run scripts/check_upstream.py --json` | JSON-only output (no Rich table) |

All scripts follow the dual-output convention: stderr for Rich-formatted human output, stdout for machine-readable JSON.

## Sub-Skills

### Surrealism (WASM Extensions)

New in SurrealDB 3. Extend the database with custom functions and analyzers written in Rust, compiled to WebAssembly, and deployed to running instances. The `rules/surrealism.md` rule covers the full Surrealism SDK, module authoring, compilation, deployment, and testing workflow.

### Surreal-Sync (CDC Migration)

Change Data Capture tool for migrating data from external databases (PostgreSQL, MySQL, MongoDB, and others) into SurrealDB. Supports incremental sync, schema translation, and conflict resolution. See `rules/surreal-sync.md`.

### SurrealFS (AI Agent Filesystem)

A filesystem abstraction built on SurrealDB, designed for AI agent workflows. Store files with rich metadata queryable via SurrealQL, version files automatically, and integrate with agent frameworks. See `rules/surrealfs.md`.

## Use Cases

### API Backend

Use SurrealDB as the primary datastore for REST or GraphQL APIs. Define tables with schemafull validation, set up row-level permissions for multi-tenant security, connect via the JavaScript or Python SDK over WebSocket for real-time live queries.

### Real-Time Application

Leverage LIVE SELECT for push-based data subscriptions. Clients receive changes as they happen without polling. Combine with WebSocket SDK connections for chat applications, collaborative editors, dashboards, and notification systems.

### Graph Analytics

Model complex relationships (social networks, organizational hierarchies, dependency trees, knowledge graphs) using RELATE and typed edge tables. Traverse paths of arbitrary depth with `->` operators. Filter and aggregate at each hop without writing JOINs.

### Vector Search and RAG

Store document embeddings alongside content. Create HNSW vector indexes with configurable distance metrics. Query with `vector::similarity::cosine` for semantic search. Build retrieval-augmented generation pipelines that combine vector similarity with metadata filtering in a single SurrealQL query.

### IoT and Time-Series

Ingest high-volume sensor data with schemaless tables. Use datetime fields and range queries for time-series analysis. Aggregate with built-in math and time functions. SurrealKV storage engine enables time-travel queries to access historical state at any point in time.

### Geospatial Applications

Store geometry types (points, polygons, multipoints) as native SurrealDB values. Use built-in geo functions (`geo::distance`, `geo::bearing`, `geo::area`, `geo::contains`) for spatial queries. Combine with other data models -- a single query can traverse a graph, filter by location, and rank by vector similarity.

### Data Migration

Migrate from PostgreSQL, MySQL, MongoDB, or other databases using Surreal-Sync CDC. Translate schemas automatically, sync incrementally, and validate with schema introspection. For SurrealDB v2-to-v3 upgrades, use surreal export/import with the migration notes in `rules/surrealql.md`.

### WASM Extensions

Extend SurrealDB with custom business logic using Surrealism. Write functions and analyzers in Rust, compile to WASM, and deploy without restarting the server. Use cases include custom validation, domain-specific scoring, proprietary tokenizers, and specialized aggregation functions.

### AI Agent Filesystem

Use SurrealFS as a persistent, queryable filesystem for AI agent workflows. Agents can store and retrieve files with rich metadata, query across files with SurrealQL, and leverage SurrealDB's permissions system for multi-agent access control.

### Full-Text Search

Define custom analyzers (tokenizers, filters, stemmers) and create search indexes on text fields. Query with full-text search predicates that integrate with the rest of SurrealQL -- combine text search with graph traversal, vector similarity, and relational filters in a single statement.

## Configuration

Set these environment variables to configure the skill scripts. All are optional with sensible defaults.

| Variable | Description | Default |
|----------|-------------|---------|
| `SURREAL_ENDPOINT` | SurrealDB server URL | `http://localhost:8000` |
| `SURREAL_USER` | Root or namespace username | `root` |
| `SURREAL_PASS` | Root or namespace password | `root` |
| `SURREAL_NS` | Default namespace | `test` |
| `SURREAL_DB` | Default database | `test` |

These variables are also recognized by the surreal CLI and official SurrealDB SDKs.

## Source Provenance

This skill was built on **2026-02-22** from these upstream sources. Use `check_upstream.py`
to detect what changed since this snapshot for incremental updates.

| Repository | Release | SHA | Snapshot Date | Rules Affected |
|------------|---------|-----|---------------|----------------|
| [surrealdb/surrealdb](https://github.com/surrealdb/surrealdb) | v3.0.0 | `2e0a61fd4daf` | 2026-02-19 | surrealql, data-modeling, security, performance, deployment, surrealism |
| [surrealdb/surrealist](https://github.com/surrealdb/surrealist) | v3.7.2 | `a87e89e23796` | 2026-02-21 | surrealist |
| [surrealdb/surrealdb.js](https://github.com/surrealdb/surrealdb.js) | v1.3.2 | `48894dfe70bd` | 2026-02-20 | sdks |
| [surrealdb/surrealdb.js](https://github.com/surrealdb/surrealdb.js) (v2 beta) | v2.0.0-beta.1 | `48894dfe70bd` | 2026-02-20 | sdks |
| [surrealdb/surrealdb.py](https://github.com/surrealdb/surrealdb.py) | v1.0.8 | `1ff4470e6ec0` | 2026-02-03 | sdks |
| [surrealdb/surrealdb.go](https://github.com/surrealdb/surrealdb.go) | v1.3.0 | `89d0f8d1b4c6` | 2026-02-12 | sdks |
| [surrealdb/surreal-sync](https://github.com/surrealdb/surreal-sync) | v0.3.4 | `8166b2b041b1` | 2026-02-12 | surreal-sync |
| [surrealdb/surrealfs](https://github.com/surrealdb/surrealfs) | -- | `0008a3a94dbe` | 2026-01-29 | surrealfs |

Documentation: [surrealdb.com/docs](https://surrealdb.com/docs) snapshot 2026-02-22.

Machine-readable provenance: [`SOURCES.json`](SOURCES.json).

## Registries

This skill is published to multiple agent skill registries:

| Registry | Install Command |
|----------|----------------|
| [skills.sh](https://skills.sh) | `npx skills add 24601/surreal-skills` |
| [ClawHub](https://clawhub.ai) | `npx clawhub install surrealdb` |
| [OpenClaw / Clawdbot](https://github.com/openclaw) | `clawhub install surrealdb` |
| GitHub | `git clone https://github.com/24601/surreal-skills.git` |

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup, code style, and PR process.

## Security

To report a vulnerability, use [GitHub Security Advisories](https://github.com/24601/surreal-skills/security/advisories/new). See [SECURITY.md](SECURITY.md) for details.

This skill declares the following security properties in `SKILL.md` frontmatter:

| Property | Value | Meaning |
|----------|-------|---------|
| `no_network` | **false** | `doctor.py`/`schema.py` connect to user-specified SurrealDB endpoint (WebSocket). `check_upstream.py` calls GitHub API via `gh` CLI. No other third-party calls. |
| `no_credentials` | **false** | Scripts accept `SURREAL_USER`/`SURREAL_PASS` for DB auth. No credentials are stored in the skill itself. |
| `no_env_write` | true | Scripts do not modify environment variables |
| `no_file_write` | true | Rules are read-only; scripts write only to stdout/stderr |
| `no_shell_exec` | false | Scripts invoke `surreal` CLI and `gh` CLI |
| `scripts_auditable` | true | All scripts are readable Python with no obfuscation |
| `scripts_use_pep723` | true | Dependencies declared inline via PEP 723, no requirements.txt |
| `no_obfuscated_code` | true | No obfuscated, encoded, or encrypted code |
| `no_binary_blobs` | true | No compiled binaries or WASM files |
| `no_minified_scripts` | true | No minified JavaScript or compressed code |
| `no_curl_pipe_sh` | **false** | Documentation mentions `curl\|sh` as one install option; safer alternatives (brew, Docker) are listed first. The skill itself never executes `curl\|sh`. |

### Required Environment Variables

Declared in `SKILL.md` `requires.env_vars`:

| Variable | Sensitive | Default | Purpose |
|----------|-----------|---------|---------|
| `SURREAL_ENDPOINT` | No | `http://localhost:8000` | SurrealDB server URL |
| `SURREAL_USER` | **Yes** | `root` | Authentication username |
| `SURREAL_PASS` | **Yes** | `root` | Authentication password |
| `SURREAL_NS` | No | `test` | Default namespace |
| `SURREAL_DB` | No | `test` | Default database |

### Required Binaries

Declared in `SKILL.md` `requires.binaries`:

| Binary | Required | Install |
|--------|----------|---------|
| `surreal` | Yes | `brew install surrealdb/tap/surreal` |
| `python3` (>=3.10) | Yes | System package manager |
| `uv` | Yes | `brew install uv` or `pip install uv` |
| `docker` | No | Optional for containerized instances |
| `gh` | No | Optional -- only used by `check_upstream.py` to compare upstream repo SHAs via GitHub API |

### Script Safety

- All user-provided table names are validated against `[a-zA-Z_][a-zA-Z0-9_]*` before interpolation into SurrealQL queries (prevents SurrealQL injection)
- `doctor.py` and `schema.py` connect only to the SurrealDB endpoint specified by the user (via env var or CLI flag)
- `check_upstream.py` calls GitHub API via `gh` CLI to compare upstream repo SHAs (optional maintenance script, not needed for normal usage)
- No data is sent to third-party services
- Credential warning labels are present on all `root/root` examples

## License

[MIT](LICENSE)

## Credits

Built for the [SurrealDB](https://surrealdb.com) community. SurrealDB is created and maintained by [SurrealDB Ltd](https://github.com/surrealdb/surrealdb).

Published on [skills.sh](https://skills.sh), [ClawHub](https://clawhub.ai), and [GitHub](https://github.com/24601/surreal-skills).
