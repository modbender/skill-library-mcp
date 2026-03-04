---
name: wreckit
description: >
  Bulletproof AI code verification. The agent IS the engine — no external tools required.
  Spawns parallel verification workers that slop-scan, type-check, mutation-test, and
  cross-verify before shipping. Language-agnostic. Framework-agnostic.
  Use when: (1) Building new projects and need verified, tested code ("build X with tests"),
  (2) Migrating/rebuilding codebases ("rewrite in TypeScript"), (3) Fixing bugs with proof
  nothing else broke ("fix this bug, verify no regressions"), (4) Auditing existing code
  quality ("audit this project", "how good are these tests?"), (5) Any request mentioning
  "wreckit", "mutation testing", "verification", "proof bundle", "code audit", or
  "bulletproof". Produces a proof bundle (.wreckit/) with gate results and Ship/Caution/Blocked verdict.
metadata:
  openclaw:
    platforms: [macos, linux]
    notes: "Uses sessions_spawn for parallel verification swarms. Requires maxSpawnDepth >= 2."
---

# wreckit — Bulletproof AI Code Verification

Build it. Break it. Prove it works.

## Philosophy

AI can't verify itself. Structure the pipeline so it can't silently agree with itself.
Separate Builder/Tester/Breaker roles across fresh contexts. Use independent oracles.

> **Full 14-step framework:** `references/verification-framework.md`

## Modes

Auto-detected from context:

| Mode | Trigger | Description |
|------|---------|-------------|
| 🟢 BUILD | Empty repo + PRD | Full pipeline for greenfield |
| 🟡 REBUILD | Existing code + migration spec | BUILD + behavior capture + replay |
| 🔴 FIX | Existing code + bug report | Fix, verify, check regressions |
| 🔵 AUDIT | Existing code, no changes | Verify and report only |

## Gates

Read the gate file before executing it. Each contains: question, checks, pass/fail criteria.

| Gate | BUILD | REBUILD | FIX | AUDIT | File |
|------|-------|---------|-----|-------|------|
| AI Slop Scan | ✅ | ✅ | ✅ | ✅ | `references/gates/slop-scan.md` |
| Type Check | ✅ | ✅ | ✅ | ✅ | `references/gates/type-check.md` |
| Ralph Loop | ✅ | ✅ | ✅ | ❌ | `references/gates/ralph-loop.md` |
| Test Quality | ✅ | ✅ | ✅ | ✅ | `references/gates/test-quality.md` |
| Mutation Kill | ✅ | ✅ | ✅ | ✅ | `references/gates/mutation-kill.md` |
| Cross-Verify | ✅ | ❌ | ❌ | ❌ | `references/gates/cross-verify.md` |
| Behavior Capture | ❌ | ✅ | ❌ | ❌ | `references/gates/behavior-capture.md` |
| Regression | ❌ | ✅ | ✅ | ❌ | `references/gates/regression.md` |
| SAST | ❌ | ❌ | ✅ | ✅ | `references/gates/sast.md` |
| LLM-as-Judge | opt | opt | opt | opt | `references/gates/llm-judge.md` |
| Design Review | ❌ | ❌ | ❌ | ✅ | `references/gates/design-review.md` |
| CI Integration | ✅ | ✅ | ❌ | ✅ | `references/gates/ci-integration.md` |
| Proof Bundle | ✅ | ✅ | ✅ | ✅ | `references/gates/proof-bundle.md` |

## Scripts

Deterministic helpers — run these, don't rewrite them:

**Core (all modes):**
- `scripts/project-type.sh [path]` — classify project context + calibration profile (`skip_gates`, thresholds, tolerated warns)
- `scripts/detect-stack.sh [path]` — auto-detect language, framework, test runner → JSON
- `scripts/check-deps.sh [path]` — verify all deps exist in registries (hallucination check)
- `scripts/slop-scan.sh [path]` — semantic slop scan (tracked vs untracked debt, categorized output) → JSON
- `scripts/type-check.sh [path]` — run type checker (tsc/mypy/cargo/go vet) → JSON
- `scripts/ralph-loop.sh [path]` — validate IMPLEMENTATION_PLAN.md structure → JSON
- `scripts/coverage-stats.sh [path]` — extract raw coverage numbers from test runner
- `scripts/mutation-test.sh [path] [test-cmd]` — mutation testing (mutmut/cargo-mutants/Stryker/AI)
- `scripts/mutation-test-stryker.sh [path]` — Stryker-specific mutation testing → JSON
- `scripts/red-team.sh [path]` — SAST + 20+ vulnerability patterns → JSON
- `scripts/regex-complexity.sh [path] [--context library|app]` — targeted ReDoS analysis → JSON
- `scripts/proof-bundle.sh [path] [mode]` — corroboration-based aggregation + proof bundle writer
- `scripts/run-all-gates.sh [path] [mode] [--log-file]` — sequential gate runner with telemetry + adaptive skipping/tolerance

**Mode-specific:**
- `scripts/behavior-capture.sh [path]` — capture golden fixtures before rebuild (REBUILD)
- `scripts/design-review.sh [path]` — dep graph, coupling, circular deps (AUDIT/REBUILD) → JSON
- `scripts/ci-integration.sh [path]` — CI config detection and scoring → JSON
- `scripts/differential-test.sh [path]` — oracle comparison, golden tests (BUILD/REBUILD) → JSON

**Extended verification:**
- `scripts/dynamic-analysis.sh [path]` — memory leaks, race conditions, FD leaks → JSON
- `scripts/perf-benchmark.sh [path]` — benchmark detection + regression vs baseline → JSON
- `scripts/property-test.sh [path]` — property-based/fuzz testing, generates stubs → JSON

**Bootstrap:**
- `scripts/run-audit.sh [path] [mode] [--spawn]` — generate orchestrator task + optional spawn

## Swarm Architecture

For multi-gate parallel execution, read `references/swarm/orchestrator.md`.

**Quick overview:**
```
Main agent → wreckit orchestrator (depth 1)
  ├─ Planning: Architect worker
  ├─ Building: Sequential Implementer workers
  ├─ Verification: Parallel gate workers
  ├─ Sequential: Cross-verify / regression / judge
  └─ Decision: Proof bundle → Ship / Caution / Blocked
```

**Critical:** Read `references/swarm/collect.md` before spawning workers.
Never fabricate results. Wait for all workers to report back.
Worker output format: `references/swarm/handoff.md`.

**Config required:**
```json
{ "agents.defaults.subagents": { "maxSpawnDepth": 2, "maxChildrenPerAgent": 8 } }
```

## Decision Framework

| Verdict | Criteria |
|---------|----------|
| **Ship** ✅ | No hard blocks; no corroborated multi-domain fail evidence above block threshold |
| **Caution** ⚠️ | Single non-hard fail, warning-only risk, or corroboration below block threshold |
| **Blocked** 🚫 | Any hard block OR corroborated non-hard failure pattern (multi-signal, multi-domain, high-confidence) |

Hard-block + corroboration rule details: `references/gates/corroboration.md`

## Running an Audit (Single-Agent, No Swarm)

For small projects or when swarm isn't needed, run gates sequentially:

1. `scripts/detect-stack.sh` → know your target (language, test cmd, type checker)
2. `scripts/check-deps.sh` → verify deps are real (not hallucinated)
3. `scripts/slop-scan.sh` → find placeholders, template artifacts, empty stubs
4. Run type checker (from detect-stack output) → `references/gates/type-check.md`
5. Run tests + `scripts/coverage-stats.sh` → `references/gates/test-quality.md`
6. `scripts/mutation-test.sh` → `references/gates/mutation-kill.md` (uses mutmut/cargo-mutants/Stryker if available)
7. `scripts/red-team.sh` → `references/gates/sast.md` (20+ vulnerability patterns, JSON report)
8. `scripts/design-review.sh` → `references/gates/design-review.md` (dep graph, circular deps, god modules)
9. `scripts/ci-integration.sh` → `references/gates/ci-integration.md` (CI config detection + scoring)
10. `scripts/dynamic-analysis.sh` → `references/gates/dynamic-analysis.md` (memory leaks, race conditions)
11. `scripts/perf-benchmark.sh` → `references/gates/performance.md` (benchmark detection + regression)
12. `scripts/property-test.sh` → `references/gates/property-based.md` (fuzzing, invariant checks)
13. `scripts/differential-test.sh` → `references/gates/differential.md` (oracle comparison, metamorphic tests)
14. echo '[...gate-results-json...]' | `scripts/proof-bundle.sh [path] [mode]` → writes `.wreckit/proof.json`, `dashboard.json`, `decision.md`

## Quick Start

```
"Use wreckit to audit [project]. Don't change anything."
"Use wreckit to build [project] from this PRD."
"Use wreckit to fix [bug]. Prove nothing else breaks."
"Use wreckit to rebuild [project] in [framework]."
```

## Dashboard

`assets/dashboard/` contains a local web dashboard for viewing proof bundles across repos.
Run: `node assets/dashboard/server.mjs` (port 3939). Reads `.wreckit/dashboard.json` from projects.

## Codex CLI Notes (2026-02-22)

When using Codex CLI to build/run projects:
- `--full-auto` sandbox blocks `npm install` network access (ENOTFOUND registry.npmjs.org)
- Fix: use `--dangerously-bypass-approvals-and-sandbox` flag instead
- Auth: `echo "$OPENAI_API_KEY" | codex login --with-api-key` stores credentials to `~/.codex/auth.json`
- Config: `~/.codex/config.toml` with `model = "gpt-5.2-codex"` and `[shell_environment_policy] inherit = "all"`
- `gpt-5.3-codex` is Copilot/VS Code only — not available via direct API. Use `gpt-5.2-codex`.
