# Changelog

All notable changes to this project will be documented in this file.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Versioning follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.4] - 2026-03-02

### Removed
- **`require('crypto')` dependency** — replaced `crypto.randomBytes()` with `Math.random()`-based hex generation for node IDs and filename suffixes. Cryptographic randomness is unnecessary for tree-local uniqueness across 5-30 nodes.

### Changed
- **SKILL.md language reframing** — replaced surveillance-pattern language ("unobtrusively maps," "runs in the background tracking," "capture," "the human") with neutral alternatives ("records structure," "saves as local JSON tree," "record," "the user"). Renamed "Unobtrusive Operation" → "Output Style" and "What to Track" → "When to Record a Node."
- **README.md alignment** — updated opening, feature list, and configuration section to match SKILL.md reframing.
- **Security header comment** added to topology.js declaring: no network access, no external deps, no eval/child_process, stdin-only input.
- **Explanatory comments** added near stdin reading section and CLI router in topology.js.

### Added
- **SECURITY.md** — dedicated security document covering threat model, what the skill does NOT do, modules used, input handling, filesystem scope, ID generation, and vulnerability reporting.
- **Security Properties section** in SKILL.md — bullet list of security guarantees (zero network, zero deps, no content stored, no process spawning, stdin-only input, user-controlled storage).

## [1.0.2] - 2026-03-02

### Fixed
- **Shell injection vulnerability:** Added stdin support to topology.js so the agent pipes JSON args instead of embedding user-derived content in shell strings. This prevents shell metacharacter injection (e.g. `$(cmd)`, backticks, `&&`) in topics, summaries, queries, and other user input.

### Changed
- All SKILL.md command examples now use stdin piping pattern (`echo '{}' | node topology.js cmd`) instead of inline shell args
- CLI router reads args from stdin when no argv[3] is provided; no-arg commands (`list`, `analyze`, `rebuild-index`) skip stdin entirely
- Updated README and CONTRIBUTING.md examples to match

## [1.0.1] - 2026-03-02

### Changed
- Reframed "silent/covert" language as "unobtrusive" to better reflect intent
- Renamed "Silent Operation" section to "Unobtrusive Operation"
- Clarified that nodes store structural summaries, never verbatim conversation content

### Added
- Privacy note in SKILL.md: user consents by installing, all data stays local
- Rule 8: local only — no network calls, no external APIs, no telemetry
- `always: true` in metadata to match always-on activation behavior

## [1.0.0] - 2026-03-02

### Added
- Initial release
- Tree structure with 4 node types: root, proposal, pivot, merge
- 3 status values: active, dead, merged
- Schema v2 with 6-char hex IDs
- 13 CLI commands: init, add-node, kill-branch, merge, render, export, fork, list, stats, associate, analyze, concept, rebuild-index
- Concept index with automatic cross-tree linking
- Companion .md file generation for semantic search indexing
- Auto-association: score-based matching to existing trees
- ASCII tree rendering and Mermaid diagram export
- Cross-tree analysis with pattern detection
- Configurable storage via `TOPOLOGY_TREES_DIR` environment variable
- Zero external dependencies (Node.js built-ins only)
