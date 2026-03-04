# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.1.2] - 2026-02-25

### Fixed
- **Output path validation**: `--output` and `--output-dir` paths are now validated before starting research, preventing wasted API spend when the target directory doesn't exist
- **Agent blocking behavior**: added explicit warnings to AGENTS.md and SKILL.md about `--output` blocking behavior and the recommended non-blocking pattern for agent callers

## [2.1.1] - 2026-02-24

### Security
- **CRITICAL: SSRF via WeasyPrint** -- PDF export now uses a custom `url_fetcher` that blocks all URL fetching, preventing SSRF and local file exfiltration via malicious markdown (e.g., `![](file:///etc/passwd)` or `<img src="http://169.254.169.254/">`)
- **YAML frontmatter quoting** -- all SKILL.md values containing colons are now properly double-quoted, and the `metadata` field is single-quoted. Fixes YAML parse failures in Codex, ClawHub scanner, and strict YAML parsers that caused the "suspicious" classification
- **Follow-up sanitization hardened** -- now strips ALL XML-like tags from previous research output (was only stripping `</previous_findings>`), preventing prompt injection via `<system>`, `<instructions>`, or delimiter escape attacks

### Added
- **CLAUDE.md** -- project instructions covering security rules, ClawHub compliance, testing checklist, and release process for all future updates

## [2.1.0] - 2026-02-24

### Security
- **Sensitive file filtering**: `--context` uploads now automatically skip `.env*`, `credentials.json`, `secrets.*`, private keys (`.pem`, `.key`), auth tokens (`.npmrc`, `.pypirc`, `.netrc`), and build directories (`node_modules`, `__pycache__`, `.git`, `dist`, `build`). Applied to both `research.py` and `upload.py`. Skipped files are reported to stderr.
- **API key echo removed**: `onboard.py --interactive` no longer echoes back user-provided API keys to the terminal
- Cross-validated by Gemini 3.1 Pro and Codex

## [2.0.4] - 2026-02-21

### Fixed
- **ClawHub metadata format**: switched from nested YAML to inline JSON string for `metadata` field, matching the format that ClawHub's parser reliably extracts into structured registry data (bins, env vars, install spec). Nested YAML was parsed but not surfaced to the registry UI.

## [2.0.3] - 2026-02-21

### Security
- **Complete env var declaration**: added all 6 env vars the code reads to `clawdis.requires.env` (was only declaring 3 of 6). Added optional model config vars: `GEMINI_DEEP_RESEARCH_AGENT`, `GEMINI_DEEP_RESEARCH_MODEL`, `GEMINI_MODEL`
- **All 3 API key vars** added to `clawdbot.config.requiredEnv` (was only listing 1)
- **Compatibility field** updated to mention optional model config env vars

## [2.0.2] - 2026-02-21

### Security
- **ClawHub registry metadata**: added `metadata.clawdis` and `metadata.clawdbot` structured fields that the OpenClaw scanner reads for registry-level declarations: `requires.bins` (uv), `requires.env` (all 3 API key vars), `primaryEnv` (GOOGLE_API_KEY), `homepage` (GitHub URL), `install` spec (uv), and `clawdbot.config.requiredEnv`. Fixes "no required env vars", "no required binaries", "Source: unknown", and "instruction-only" scanner findings.

## [2.0.1] - 2026-02-21

### Security
- **SKILL.md frontmatter**: declared all requirements (`compatibility`, `allowed-tools`, `metadata.required_env`, `metadata.required_binaries`, `metadata.primary_credential`, `metadata.file_upload_behavior`, `metadata.network_access`, `metadata.no_obfuscation`, `metadata.no_telemetry`) to resolve OpenClaw "suspicious" classification caused by metadata mismatch
- **Security & Transparency section** added to SKILL.md body covering credentials handling, file upload scope, non-interactive mode risks, and no-obfuscation guarantee

## [2.0.0] - 2026-02-21

### Added
- **Research depth modes** (`--depth {quick,standard,deep}`) -- control research scope and expected duration; quick targets 2-5 min, deep targets 15-45 min with exhaustive analysis
- **Research caching** with content-hash deduplication -- identical queries return cached results instantly instead of re-running expensive API calls; cache entries auto-expire after 7 days; bypass with `--no-cache`
- **Progress estimation** during polling -- shows "~X% complete" based on adaptive history percentiles (p25/p50/p75) when sufficient data exists
- **Cost ceiling guard** (`--max-cost USD`) -- abort before starting if estimated cost exceeds the limit; prevents runaway spending from agent loops
- **Query from file** (`--input-file PATH`) -- read long/complex research queries from a file instead of the command line
- **Store garbage collection** (`state.py gc`) -- clean up orphaned ephemeral context stores older than 24 hours from crashed runs

### Security
- Removed all `curl | sh` install patterns from documentation (VirusTotal supply chain risk flag)
- Sanitized `--follow-up` output with data delimiters to mitigate prompt injection from compromised previous research output

## [1.3.1] - 2026-02-19

### Changed
- **Default model updated** to `gemini-3.1-pro-preview` for file search store queries (was `models/gemini-flash-latest`)
- Documentation updated to reflect current model defaults

## [1.3.0] - 2026-02-11

### Added
- **Output formats** (`--format {md,html,pdf}`) -- export research reports as HTML (dark-themed, styled) or PDF (requires weasyprint). Markdown remains default and canonical format. (Issue #6)
- **Prompt templates** (`--prompt-template {typescript,python,general,auto}`) -- domain-specific prompt prefixes that optimize research for TypeScript/JavaScript or Python codebases. Auto-detect mode scans `--context` file extensions. (Issue #3)
- **Edge case tests** (`tests/test_cost_estimation.py`) -- 10 tests covering empty dirs, binary-only dirs, Unicode content, mixed history, zero/negative duration, and more. Run with `uv run tests/test_cost_estimation.py`. (Issue #5)
- **Example research reports** (`docs/examples/`) -- 3 real research outputs demonstrating the tool's capabilities: WebSocket vs SSE comparison, event sourcing patterns, WebAssembly state of the art. (Issue #4)

### Changed
- Bumped GitHub Actions: actions/setup-python v5→v6, astral-sh/setup-uv v6→v7, actions/setup-node v4→v6

## [1.2.3] - 2026-02-10

### Added
- **Use cases section** in README with 7 domain-specific categories: trading & finance, competitive intelligence, software architecture, security audit prep, design & UX research, academic research & analysis, regulatory compliance -- all with copy-pasteable `--context` examples

## [1.2.2] - 2026-02-09

### Changed
- **SKILL.md description optimized** to ~75 tokens for agent context window efficiency
- **Security & Trust section** added to README (no obfuscation, no telemetry, fully auditable)
- **GitHub topics expanded** to 20 (added agent-skill, openclaw-skill, claude-code-skill, autonomous-agent, python, uv, and more)
- **Pi agent installation** instructions added to README
- **ClawHub auto-publish** on release via GitHub Actions (uses CLAWHUB_TOKEN secret)
- **skills.sh re-index** triggered automatically on release

### Added
- 4 contributor-friendly GitHub issues seeded (good-first-issue, prompt-engineering, documentation, test-case)
- Pi agent (`badlogic/pi-mono`) and OpenClaw/ClawHub install instructions in README

## [1.2.1] - 2026-02-08

### Changed
- **Skill renamed** from `agent-deep-research` to `deep-research` in SKILL.md for better skills.sh search discoverability
- **Description clarified**: explicitly states Gemini Interactions API usage with no Gemini CLI dependency
- **Description enriched**: highlights automatic RAG grounding (`--context`), cost estimation (`--dry-run`), adaptive polling, and structured output

## [1.2.0] - 2026-02-08

### Added
- **Agent onboarding** (`scripts/onboard.py`) -- interactive setup wizard for humans (`--interactive`) and JSON capabilities manifest for AI agents (`--agent`), with quick config check (`--check`)
- **AGENTS.md** -- structured agent briefing with capabilities table, decision trees, output contracts, common workflows, and pricing reference
- **Cost estimation** (`--dry-run` flag on `research.py start`) -- preview estimated costs before running research, based on context file size and pricing heuristics
- **Post-run usage metadata** -- after research completes with `--output-dir`, `metadata.json` includes a `usage` key with estimated tokens, costs, context stats, and source counts
- **"For AI Agents" section** in SKILL.md pointing to onboard.py and AGENTS.md

## [1.1.0] - 2026-02-09

### Added
- **`--context` flag** (`scripts/research.py`) -- point at a local file or directory to automatically create an ephemeral file search store, upload files, and run RAG-grounded deep research in a single command
- **`--context-extensions` flag** -- filter which file types to upload from a context path (e.g. `--context-extensions py,md`)
- **`--keep-context` flag** -- prevent automatic cleanup of the ephemeral store after research completes, allowing reuse via `--store`
- Ephemeral context stores are tracked in `.gemini-research.json` under `contextStores` for cleanup visibility

## [1.0.0] - 2026-02-08

### Added
- **Deep research** (`scripts/research.py`) -- start background research jobs, check status, save reports via Google Gemini's deep research agent
- **File search stores** (`scripts/store.py`) -- create, list, query, and delete stores for RAG-grounded research
- **File upload** (`scripts/upload.py`) -- upload files and directories to file search stores with MIME type detection
- **Session management** (`scripts/state.py`) -- persistent workspace state for research sessions and store mappings
- **Adaptive polling** -- history-based poll interval tuning that learns from past research completion times (p25-p75 window targeting, separate curves for grounded vs non-grounded research)
- **Structured output** (`--output-dir`) -- save reports, metadata, interaction data, and extracted sources to a structured directory
- **Smart sync** (`--smart-sync`) -- hash-based file change detection to skip unchanged uploads
- **JSON output** (`--json`) -- machine-readable output on stdout for agent consumption
- **Timeout control** (`--timeout`) -- configurable maximum wait time for blocking operations
- **Non-interactive mode** -- automatic TTY detection to skip confirmation prompts for AI agent and CI integration
- **PEP 723 inline metadata** -- all scripts declare dependencies inline, run via `uv run` with zero pre-installation
- **skills.sh distribution** -- SKILL.md manifest for installation across 30+ AI coding agents
- **CI workflow** -- SKILL.md validation, py_compile, uv smoke test
- **Dependabot** -- automated GitHub Actions dependency updates

### Changed
- Rebranded from `gemini-cli-deep-research` (Gemini CLI extension) to `agent-deep-research` (universal AI agent skill)
- Replaced Node.js MCP server and TOML commands with Python CLI scripts
- License clarified as MIT (was labeled ISC in some places)

### Removed
- Node.js MCP server (`src/index.ts`, `package.json`, `tsconfig.json`, etc.)
- Gemini CLI TOML commands (`commands/deep-research/*.toml`)
- ESLint, Prettier, Jest configuration
- Build infrastructure (`build.mjs`, `release/`)

[2.1.2]: https://github.com/24601/agent-deep-research/compare/v2.1.1...v2.1.2
[2.1.1]: https://github.com/24601/agent-deep-research/compare/v2.1.0...v2.1.1
[2.1.0]: https://github.com/24601/agent-deep-research/compare/v2.0.4...v2.1.0
[2.0.4]: https://github.com/24601/agent-deep-research/compare/v2.0.3...v2.0.4
[2.0.3]: https://github.com/24601/agent-deep-research/compare/v2.0.2...v2.0.3
[2.0.2]: https://github.com/24601/agent-deep-research/compare/v2.0.1...v2.0.2
[2.0.1]: https://github.com/24601/agent-deep-research/compare/v2.0.0...v2.0.1
[2.0.0]: https://github.com/24601/agent-deep-research/compare/v1.3.1...v2.0.0
[1.3.1]: https://github.com/24601/agent-deep-research/compare/v1.3.0...v1.3.1
[1.3.0]: https://github.com/24601/agent-deep-research/compare/v1.2.3...v1.3.0
[1.2.3]: https://github.com/24601/agent-deep-research/compare/v1.2.2...v1.2.3
[1.2.2]: https://github.com/24601/agent-deep-research/compare/v1.2.1...v1.2.2
[1.2.1]: https://github.com/24601/agent-deep-research/compare/v1.2.0...v1.2.1
[1.2.0]: https://github.com/24601/agent-deep-research/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/24601/agent-deep-research/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/24601/agent-deep-research/releases/tag/v1.0.0
