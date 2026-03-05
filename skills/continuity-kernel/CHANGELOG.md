# Changelog

## [0.2.0] - 2026-02-22

### Added
- `memoryarena-mini-perturb` suite with deterministic perturb profile controls (`deletion`, `noise_injection`, `reorder`) and observed-trace filtering
- Core-shadow suite lane for synthetic stress gating without trace dependency
- Runtime state fingerprint drift metric (`runtime_state_fingerprint_drift_rate`) with zero-drift threshold enforcement in shadow eval outputs
- Rolling 5-snapshot observed-trace weak/strong calibration receipts (`verification_calibration`) applied at append time
- A/B/C compaction ablation receipts (`compaction_abc`) comparing size-only, dual-route size-only, and dual-route attention-preserving variants
- Summary artifact now emits `trace-bundle.jsonl` (trace_id/span_id/hook/tool_intent/result_status/confidence/selector_mode)
- MemoryArena perturb trace fixture and regression tests for profile routing, calibration windowing, CLI profile handling, and compaction A/B/C schema integrity

### Changed
- `run_shadow_eval.py` now accepts `--suite core-shadow|memoryarena-mini|memoryarena-mini-perturb` and `--perturb-profile`
- Shadow eval snapshot schema now includes `perturb_profile`, `runtime_state_fingerprint_drift_rate`, `verification_calibration`, and `compaction_abc`

## [0.1.3] - 2026-02-22

### Added
- Durable default SQLite runtime path in `ContinuityHookAdapter()` with automatic parent-directory creation (`~/.local/state/continuity-kernel/continuity.db`)
- Explicit `CONTINUITY_KERNEL_DB_PATH` override and `:memory:` opt-in constructor support
- Restart-survivability integration test for default adapter construction
- Strict trace-evidence gate in shadow eval (`--allow-synthetic` opt-in path with forced `pass=false`)
- Stable key pairing (`trace_id` or `(run_index, task_id)`) for kernel-vs-baseline alignment in observed evals
- Regression tests for missing traces, missing observed size-only compaction baseline, and misaligned outcome sets

### Fixed
- Removed synthetic substitution for observed compaction A/B baselines; observed mode now fails when required size-only traces are missing
- Prevented review-pass artifacts from non-trace eval runs

## [0.1.2] - 2026-02-22

### Added
- Trace-backed shadow eval ingestion (`--trace-jsonl`, `--trace-dir`) with observed-run scoring and deterministic digests over recorded outcomes
- MemoryArena-mini trace fixture and regression tests proving observed continuity_lift_delta / verification telemetry calculation
- Task-grounding receipts now include eval source + trace provenance metadata for auditability

### Changed
- Repackaged continuity-kernel to a flat skill layout (no nested Python package, no in-skill test/spec folders) to match reference-skill structure
- Eval/test artifacts moved to repo-level locations: `tests/continuity-kernel/*` and `artifacts/continuity-kernel/p0-evals.json`
- Skill command docs updated for flat layout paths and trace-backed eval flow

## [0.1.1] - 2026-02-22

### Added
- Deterministic `runtime_state_fingerprint` injected into continuity packets and runtime contracts
- Restart-invariance coverage for runtime fingerprint in service tests
- Experimental `dual_route_experimental` field selector mode with fail-open fallback to deterministic mode
- Experimental `attention_preserving_experimental` compaction policy with size-only A/B receipt comparison (`dropped_fields_delta`, `resume_success_delta`)
- Selector/compaction-mode diagnostics + shadow-eval receipt fields for A/B comparison
- `--suite memoryarena-mini` support in `scripts/run_shadow_eval.py`
- Shadow-eval schema expansion: `continuity_lift_delta`, `weak_check_score`, `strong_check_triggered`, `incorrect_accept_rate`, `incorrect_reject_rate`
- Task-grounded per-run outcome persistence for shadow eval snapshots

### Fixed
- Runtime contract canonicalization now validates fingerprint format and fail-opens malformed values
- Shadow-eval pipeline now computes quality metrics from explicit evaluated tasks (not fixed global percentages)

## [0.1.0] - 2026-02-21

### Added
- Soul Card + Mission Ticket persistence via SQLite with explicit schema-version guards
- Bounded `llm_input` continuity packet injection with deterministic field ordering
- First-run auto-migrate bootstrap guard in runtime service
- Fail-open diagnostics envelope across store/injector/runtime boundaries
- Runtime contract canonicalization + digest helpers for packet/warning determinism
- Drift warning classifier integration support for `before_tool_call`
- Shadow eval harness (`scripts/run_shadow_eval.py`) with snapshot append semantics
- Shadow eval receipts written to `artifacts/p0-evals/<timestamp>/summary.json`
- Runtime proof script (`scripts/generate_runtime_contract_proof.py`) with reproducible artifact output
- Test suite covering bootstrap, deterministic bounds, fail-open passthrough, canonicalization safety, and eval harness schema
