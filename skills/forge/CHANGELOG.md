# Changelog

All notable changes to the Forge project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-02-07

### Added

#### Core Skill (SKILL.md)

- **Autonomous QE Swarm**: 8 specialized agents spawned in parallel for continuous quality verification
  - Specification Verifier (Sonnet) — generates/validates Gherkin behavioral specs and ADRs
  - Test Runner (Haiku) — executes E2E test suites, parses results, maps failures to specs
  - Failure Analyzer (Sonnet) — root cause analysis, pattern matching, dependency impact assessment
  - Bug Fixer (Opus) — applies confidence-tiered fixes from first principles
  - Quality Gate Enforcer (Haiku) — evaluates all 7 gates, arbitrates agent disagreements
  - Accessibility Auditor (Sonnet) — WCAG AA audit: labels, contrast, targets, focus order
  - Auto-Committer (Haiku) — stages fixed files, creates detailed commits with gate statuses
  - Learning Optimizer (Sonnet) — updates confidence tiers, defect prediction, coverage metrics

- **7 Quality Gates**: Evaluated after every fix cycle, all must pass before commit
  - Gate 1 — Functional (100% pass rate, blocking)
  - Gate 2 — Behavioral (100% Gherkin scenario coverage, blocking)
  - Gate 3 — Coverage (>=85% overall, >=95% critical paths, blocking for critical)
  - Gate 4 — Security (0 critical/high violations including SAST checks, blocking)
  - Gate 5 — Accessibility (WCAG AA compliance, warning)
  - Gate 6 — Resilience (offline/timeout/error handling, warning)
  - Gate 7 — Contract (0 API schema mismatches, blocking)

- **Model Routing**: Cost-optimized routing of agents to appropriate model tiers
  - Opus for high-reasoning tasks (Bug Fixer)
  - Sonnet for moderate-reasoning tasks (Spec Verifier, Failure Analyzer, A11y Auditor, Learning Optimizer)
  - Haiku for low-reasoning tasks (Test Runner, Gate Enforcer, Auto-Committer)
  - Configurable via `forge.config.yaml` model_routing overrides
  - Estimated ~60% token cost reduction vs running all agents on highest tier

- **Confidence-Tiered Fix Patterns**: Self-evolving pattern database
  - Platinum (>=0.95) — auto-apply immediately without review
  - Gold (>=0.85) — auto-apply with commit message flag
  - Silver (>=0.75) — suggest to Bug Fixer, don't auto-apply
  - Bronze (>=0.70) — store for learning only
  - Expired (<0.70) — demoted, needs revalidation
  - Success: confidence += 0.05, Failure: confidence -= 0.10

- **Behavioral Specification & Architecture Records (Phase 1)**:
  - Gherkin spec generation from implementation analysis
  - Spec-to-test mapping with zero-gap coverage
  - Agent-optimized ADR generation with MUST/MUST NOT/Verification/Dependencies template
  - ADR storage in `docs/decisions/` or project-configured directory

- **Contract & Dependency Validation (Phase 2)**:
  - API response schema validation against expected DTOs
  - Shared types validation across bounded context boundaries
  - Cross-cutting foundation validation (auth, error format, logging, pagination consistency)
  - Dependency graph with cascade re-testing when fixes touch upstream contexts

- **Structured Agent Prompts**: All 8 agents include
  - CONSTRAINTS section — explicit rules about what NOT to do
  - ACCEPTANCE section — machine-checkable success criteria

- **Autonomous Execution Loop**: Specify → Test → Analyze → Fix → Audit → Gate → Commit → Learn → Repeat
  - Max 10 iterations per run
  - Gate failures categorized for targeted re-runs (not full re-run)

- **Real-Time Progress Reporting**:
  - Structured JSON events from all agents written to `.forge/progress.jsonl`
  - Integration with AG-UI streaming protocol when Agentic QE is available

- **Defect Prediction**: Proactive failure prediction based on
  - Files changed since last green run
  - Historical failure rates per bounded context
  - Fix pattern freshness (recently applied fixes regress more)
  - Complexity metrics and dependency chain length
  - Tests executed in descending probability order for faster convergence

- **Exhaustive Edge Case Testing**: Comprehensive test patterns for
  - Interaction states (single, rapid, long press, disabled)
  - Input field states (empty, focus, valid, invalid, max length, paste, clear)
  - Async operation states (loading, success, error, timeout)
  - Navigation edge cases (back, deep link, invalid deep link)
  - Scroll edge cases (overscroll, hidden content, keyboard)
  - Network edge cases (offline, slow, reconnect, 500/401/403/404)
  - Chaos testing (timeout injection, partial response, rate limiting, concurrent mutations, session expiry)

- **Visual Regression Testing**:
  - Before/after screenshot capture and pixel-by-pixel comparison
  - Configurable threshold (default 0.1% diff tolerance)
  - Platform-specific capture (Playwright, Cypress, Flutter golden files)
  - Flagged as Gate 5 warnings

- **Rollback & Conflict Resolution**:
  - Rollback to last known good commit with pattern demotion
  - Fix Conflict Protocol — halt, re-analyze, categorize, revert limit (max 2 cycles)
  - Agent Disagreement Resolution — Gate Enforcer as arbiter, more-gates-passing wins
  - Escalation to user review after 2 failed revert cycles

- **Optional Agentic QE MCP Integration**:
  - Auto-detection via `claude mcp list`
  - ReasoningBank for vector-indexed pattern storage (replaces claude-flow memory)
  - Delegation to specialized AQE domains: defect-intelligence, security-compliance, visual-accessibility, contract-testing, learning-optimization, requirements-validation
  - AG-UI protocol for real-time progress streaming
  - All features additive — Forge works identically without AQE

- **Architecture Adaptability**: Supports monoliths, modular monoliths, microservices, monorepos, mobile+backend, full-stack monoliths
  - Auto-discovers backend/frontend technology, test framework, project structure, API protocol, build system
  - Optional `forge.config.yaml` for explicit configuration
  - Optional `forge.contexts.yaml` for bounded context definitions

- **Defensive Test Patterns**: Framework-specific safe interaction helpers
  - Flutter: safeTap, safeEnterText, visualDelay, scrollUntilVisible, waitForApiResponse
  - Cypress/Playwright: safeClick, waitForApi

- **Common Fix Patterns**: Pre-loaded patterns for common failure types
  - Element Not Found (Platinum, 0.97 confidence)
  - Timeout (Gold, 0.89 confidence)
  - Assertion Failed (Silver, 0.78 confidence)
  - API Response Mismatch (Gold, 0.86 confidence)

- **Invocation Modes**: 14 CLI modes
  - `--autonomous --all` / `--autonomous --context [name]`
  - `--verify-only` / `--fix-only`
  - `--learn` / `--predict`
  - `--add-coverage --screens [names]`
  - `--spec-gen --context [name]` / `--spec-gen --all`
  - `--gates-only` / `--chaos`

- **No Mocking Rule**: Absolute rule — all tests run against real backend API, no mock frameworks allowed

- **Memory Namespaces**: 8 namespaces for persistent state
  - forge-patterns, forge-results, forge-state, forge-commits, forge-screens, forge-specs, forge-contracts, forge-predictions

#### Documentation (README.md)

- Comprehensive project documentation with:
  - Project overview and philosophy (Build/Verify/Heal pillars, "DONE DONE" concept)
  - Quick start guide
  - Full invocation modes table (14 CLI modes)
  - Architecture diagram (autonomous loop visualization)
  - Quality gates reference table
  - Agent roles table with model tiers
  - Configuration examples (forge.config.yaml, forge.contexts.yaml)
  - Agentic QE integration capability matrix
  - Links to all 4 reference sources (CBV article, BWQ article, V3 QE Skill, Agentic QE)
  - MIT license

#### Project Setup

- `.gitignore` — excludes node_modules, .DS_Store, logs, .env, .dev.vars
- `LICENSE` — MIT license

### Reference Sources

This release was validated against and incorporates concepts from:

1. **Continuous Behavioral Verification** (Ikenna Okpala) — "DONE DONE" concept, Gherkin behavioral contracts, artifact layer, agent-optimized ADRs
2. **Build with Quality Skill** (Mondweep Chakravorty) — DDD+ADR+TDD pillars, hierarchical-mesh agent topology, quality gates during development
3. **V3 QE Skill** (mondweep/vibe-cast) — Confidence tiers, 7 quality gates, TinyDancer model routing, coverage thresholds
4. **Agentic QE** (proffesor-for-testing/agentic-qe) — ReasoningBank, 51 specialized agents, AG-UI protocol, BrowserSwarmCoordinator

[1.0.0]: https://github.com/ikennaokpala/forge/releases/tag/v1.0.0
