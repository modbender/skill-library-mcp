# Changelog

All notable changes to this project will be documented in this file.
Format based on [Keep a Changelog](https://keepachangelog.com/).

## [1.1.1] - 2026-02-26

### Fixed
- Python SDK release corrected from v2.0.0 to v2.0.0-alpha.1 (pre-release alpha,
  not GA). Python 3.9 dropped; minimum is now 3.10. Added Logfire instrumentation note.

### Added
- SurrealDB v3.1.0-alpha behavior change: SELECT on non-existent records now returns
  NONE instead of error (#6978). Documented in rules/surrealql.md with migration note.

### Changed
- SOURCES.json synced to HEAD 2026-02-26 (surrealdb fa22ecf0ae93, surrealdb.py b21302c05565)
- AGENTS.md: added context comment on production 0.0.0.0 bind address

## [1.1.0] - 2026-02-25

### Major
- JavaScript SDK v2.0.0 GA released (no longer beta). Updated from beta tag to
  stable: `npm install surrealdb` (not @beta). Full SurrealDB 3.0.1 support,
  client-side transactions, multi-session, query builder, streaming responses.
- Python SDK v2.0.0 released. WebSocket session transaction ID fix, musl Linux
  support for Alpine/containers, improved error handling, README cleanup.

### Changed
- rules/sdks.md: JS v2 section title changed from "beta" to "GA -- recommended
  for new projects". Install commands changed from surrealdb@beta to surrealdb.
  All @surrealdb/wasm@beta and @surrealdb/node@beta tags removed.
- rules/sdks.md: Python SDK updated to v2.0.0 with changelog
- rules/surrealql.md: v3.1.0-alpha tracking updated with error chaining
  infrastructure (#6969), SurrealValue derive convenience (#6970), wasmtime
  update (#6973)
- SOURCES.json: All repos synced to HEAD 2026-02-25. Removed surrealdb.js@beta
  entry (v2 is now GA). surrealdb.js release v2.0.0, surrealdb.py release v2.0.0.
- Additional credential warning markers on remaining unwarned root/root examples
  in SKILL.md workflow section and AGENTS.md decision tree
- deployment.md: --bind flag default annotated with local dev recommendation

## [1.0.6] - 2026-02-24

### Added
- SurrealDB v3.0.1 patch notes in rules/surrealql.md: duration arithmetic, computed
  field index prevention, record ID dereference fix, error serialization, GraphQL
  string enum fix, root user permission fix, parallel index compaction, WASM compat,
  RouterFactory trait for embedders
- v3.1.0-alpha tracking notes (main branch: planner tidy-up, test fixtures, code coverage)
- JS SDK v2.0.0-beta.2 changes: ne (!=) operator, error cause property, createWorker
  factory for Vite-compatible Web Worker engines, minimum SurrealDB version bump to 2.1.0
- Python SDK error handling improvements (#233)

### Changed
- All upstream repos synced to HEAD as of 2026-02-24
- SOURCES.json: surrealdb release updated v3.0.0 -> v3.0.1, added main_tracking field
- SOURCES.json: surrealdb.js@beta release updated beta.1 -> beta.2
- Docker image tags updated from v3.0.0 to v3 (tracks latest v3.x)
- AGENTS.md: fixed remaining 0.0.0.0 bind address to 127.0.0.1
- rules/deployment.md: fixed remaining 0.0.0.0 bind to 127.0.0.1 with comment
- rules/sdks.md: createWasmWorkerEngines example updated for beta.2 createWorker factory
- rules/sdks.md: added ne operator to Expressions API imports

## [1.0.5] - 2026-02-24

### Added
- Native GitHub Copilot agent skill support (.github/skills/surrealdb/SKILL.md)
  - Follows the open Agent Skills standard (agentskills.io)
  - Auto-loads in VS Code, Copilot CLI, and Copilot coding agent when SurrealDB context detected
  - Available as `/surrealdb` slash command in Copilot chat
  - Progressive disclosure: metadata -> instructions -> rule files on demand
  - Supports project-level (.github/skills/) and personal (~/.copilot/skills/) installation
  - Includes `argument-hint` for guided slash command usage
  - References all 12 rule files via relative paths for Copilot resource loading
  - Quick reference section with SurrealQL essentials for immediate context

### Changed
- README: replaced "append AGENTS.md to copilot-instructions.md" with native Copilot
  agent skills instructions (3 install methods: project, personal, /skills menu)
- README: added Cursor .cursor/skills/ integration (same Agent Skills standard)
- Upstream sync to 2026-02-24:
  - surrealdb/surrealdb: +2 commits (error serialization fix, CI fix)
  - surrealdb/surrealist: +1 commit (strict sandbox option fix)
  - surrealdb/surrealdb.js: +2 commits (version bumps)
- SOURCES.json baselines updated to current HEAD SHAs

## [1.0.4] - 2026-02-22

### Security Fixes (addressing OpenClaw/VirusTotal scan findings)
- SKILL.md frontmatter: changed no_network and no_credentials to false with
  explanatory notes (scripts DO connect to user-specified endpoints)
- SKILL.md frontmatter: added requires.binaries declaring surreal, python3, uv, docker
- SKILL.md frontmatter: added requires.env_vars declaring all SURREAL_* vars
  with sensitive: true on SURREAL_USER and SURREAL_PASS
- Replaced all curl|sh install instructions with brew/package manager alternatives
  in SKILL.md, AGENTS.md, README.md, and rules/deployment.md
- Added security notes on curl|sh (download-and-review alternative documented)
- Added credential warnings on all root/root examples across all files
- Changed bind address from 0.0.0.0 to 127.0.0.1 in quick start examples
- Added SurrealQL injection prevention: _sanitize_identifier() in schema.py
  validates table names against [a-zA-Z_][a-zA-Z0-9_]* before query interpolation
- surrealfs sub-skill: added Security Considerations section covering telemetry
  opt-out (LOGFIRE_SEND_TO_LOGFIRE=false), HTTP binding, pipe command risks,
  sandboxing, credential scoping
- surrealfs sub-skill: added requires.env_vars and security block to frontmatter
- README: corrected security properties table (no_network=false, no_credentials=false)
- README: added Required Environment Variables table with sensitivity markers
- README: added Required Binaries table
- README: added Script Safety section

## [1.0.3] - 2026-02-22

### Added
- Nightly upstream freshness check GHA workflow (.github/workflows/upstream-check.yml)
  - Runs at 06:00 UTC daily, auto-creates/updates GitHub issue when repos drift
  - Manual trigger via workflow_dispatch
- ClawHub/OpenClaw publishing (clawhub.ai registry)
- Security metadata in SKILL.md frontmatter (no_network, no_credentials, scripts_auditable, etc.)
- Registries section in README with skills.sh, ClawHub, OpenClaw install commands
- Security properties table in README
- GitHub topics: openclaw, clawhub, agentskills (replacing lower-value topics)
- Opened surrealdb/surrealdb#6958 for community resource listing

### Changed
- Synced upstream sources to latest HEAD (snapshot 2026-02-22):
  - Surrealist v3.7.1 -> v3.7.2 (migration export fix, misc UI fixes)
  - surrealdb.js WASM SDK updated to 3.x, WebWorker Vite compatibility fix
- Updated provenance tables in AGENTS.md, SKILL.md, README.md
- Updated sub-skills with provenance metadata and corrected upstream CLI syntax
- Updated repo description and homepage on GitHub

## [1.0.2] - 2026-02-19

### Added
- JavaScript/TypeScript SDK v2.0.0-beta.1 coverage in rules/sdks.md
  - Engine-based architecture (createRemoteEngines, createNodeEngines, createWasmEngines, createWasmWorkerEngines)
  - Multi-session support (newSession, forkSession, await using)
  - Query builder pattern (.fields, .where, .fetch, .content, .merge, .replace, .patch)
  - Query method overhaul (.collect, .json, .responses, .stream)
  - Expressions API (eq, or, and, between, inside, raw, surql template tag)
  - Redesigned live queries (.subscribe, for await, .liveOf)
  - Auto token refresh (renewAccess)
  - User-defined API invocation (.api)
  - Diagnostics API (applyDiagnostics)
  - Codec visitor API (valueDecodeVisitor, valueEncodeVisitor)
  - v1 to v2 migration guide table
- Tracked surrealdb.js v2.0.0-beta.1 (SHA 6383698daccf) in SOURCES.json

## [1.0.1] - 2026-02-19

### Added
- SOURCES.json with commit SHAs, release tags, and dates for all 7 upstream repos
- check_upstream.py script to diff current upstream state against skill snapshot
- Source provenance tables in AGENTS.md, SKILL.md, and README.md with dates
- Detailed Claude Code plugin installation instructions (4 methods)

### Fixed
- KNN operator syntax in AGENTS.md (`<|K,EF|>` takes two numeric params, not distance metric)
- Added `--check` alias for `--quick` flag in doctor.py
- Added exit code 1 on unhealthy status in doctor.py

## [1.0.0] - 2026-02-19

### Added
- Initial release of SurrealDB 3 skill for AI coding agents
- Comprehensive SurrealQL reference (rules/surrealql.md)
- Multi-model data modeling guide (rules/data-modeling.md)
- Graph query patterns (rules/graph-queries.md)
- Vector search and RAG patterns (rules/vector-search.md)
- Security and access control guide (rules/security.md)
- Performance optimization guide (rules/performance.md)
- SDK integration patterns for JS, Python, Go, Rust, Java, .NET (rules/sdks.md)
- Deployment and operations guide (rules/deployment.md)
- Surrealism WASM extension development (rules/surrealism.md)
- Surreal-Sync data migration guide (rules/surreal-sync.md)
- Surrealist IDE guide (rules/surrealist.md)
- SurrealFS AI agent filesystem guide (rules/surrealfs.md)
- Python onboard script with setup wizard and agent capabilities manifest
- Python doctor script for environment health checks
- Python schema script for database introspection and export
- Sub-skills: surrealism, surreal-sync, surrealfs
- CI/CD workflows for validation and release
- Universal compatibility with 30+ AI coding agents
