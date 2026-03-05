## v11.2.0 (2026-02-27)

### New: Persistent worker daemon (`crabpath daemon`)
- `crabpath/daemon.py`: loads state once, keeps graph+index hot in memory
- JSON-RPC over stdin/stdout (NDJSON protocol)
- Methods: query, learn, maintain, health, info, save, reload, shutdown
- Query responses include timing: `embed_query_ms`, `traverse_ms`, `total_ms`
- Auto-save after N write ops, graceful SIGTERM/SIGINT handling
- Eliminates per-call state reload (~100-800ms savings)
- `examples/ops/client_example.py`: Python client demo

### New: Constitutional anchors (`crabpath anchor`)
- Authority levels: constitutional (never decay/prune/merge), canonical (slow decay), overlay (default)
- `crabpath maintain` respects authority levels during all structural ops
- CLI: `crabpath anchor --state PATH --node-id ID --authority constitutional|canonical`

### New: Incremental file sync (`crabpath sync`)
- `crabpath/sync.py`: detect file changes, re-embed only what changed
- Default authority map for common files (SOUL.md → constitutional, USER.md → canonical)
- CLI: `crabpath sync --state PATH --workspace DIR`

### New: Daily note compaction (`crabpath compact`)
- `crabpath/compact.py`: old notes → extract facts → inject into graph → shrink files
- Optional LLM summarization, deterministic fallback
- CLI: `crabpath compact --state PATH --memory-dir DIR`

### Fix: save_state() embedder metadata preservation
- Now reads existing meta before writing; no more silent hash-v1/1024 overwrite
- Dimension mismatch raises ValueError (prevents corrupt state)
- Fixes GitHub Issue #1 item #7 (CormorantAI production data corruption)

### Fix: Rebuild preserves injected nodes
- `--preserve-injected` flag (default True) in init_agent_brain.py and rebuild_all_brains.py
- Snapshots + restores CORRECTION/TEACHING nodes across rebuilds
- Fixes GitHub Issue #1 item #5

### Docs
- README overhaul: all 17 CLI commands, apply_outcome_pg section, "Why CrabPath", write policy
- `docs/architecture.md`: persistent worker, context lifecycle, constitutional anchors
- `docs/setup-guide.md`: steps 7-9 (sync, anchors, compact)
- Production stats: 4 brains (MAIN, PELICAN, BOUNTIFUL, CORMORANT)
- `jonathangu.com/crabpath/gu2016/`: accessible policy gradient derivation page

### Tests
- 246 tests (was 220), 15 simulations

## v11.1.0 (2026-02-27)

### New: Maintenance engine (`crabpath maintain`)
- `crabpath/maintain.py`: `run_maintenance()`, `prune_edges()`, `prune_orphan_nodes()`
- CLI: `crabpath maintain --state PATH --tasks health,decay,prune,merge [--dry-run]`
- Scheduler-agnostic: call from cron, systemd, Airflow, or any batch runner

### New: Two-timescale architecture docs
- `docs/architecture.md`: online learning (fast loop) vs maintenance (slow loop)
- Integration contract: what frameworks provide, what CrabPath produces
- Brain directory layout specification

### New: Framework-agnostic examples (`examples/ops/`)
- `callbacks.py`: `make_embed_fn()` and `make_llm_fn()` factory functions
  - Default: OpenAI text-embedding-3-small + gpt-5-mini
  - Fallback: HashEmbedder (zero-dep, for testing)
- `query_and_learn.py`: fast loop example with --embedder flag
- `run_maintenance.py`: slow loop example with --embedder and --llm flags

### New: True REINFORCE policy gradient (`apply_outcome_pg`)
- Full derivation: softmax score function ∇log π = (1/τ)(eₐ - π)
- Updates ALL outgoing edges at each visited node (not just traversed)
- Conservation property: weight updates sum to zero per node
- Temperature scaling, baseline support, discount along trajectory

### New: 12 simulations + expanded benchmarks
- PG vs heuristic ablation (weight conservation)
- Noise robustness (graceful to 20%, degrades at 30%)
- Static vs learning baseline
- Scaling analysis (sub-linear: 50→2000 nodes)
- Internal benchmark: 45 queries, 8 methods
- External benchmarks: MultiHop-RAG (n=1000) + HotPotQA (n=500) with OpenAI embeddings

### Paper updates
- Title: "Learned Graph Traversal for Retrieval Routing"
- Full PG derivation with numerical examples
- External benchmark results (cold traverse +7.7% MultiHop, +33.6% HotPotQA)
- De-marketing pass: removed metaphors, added crisp definitions
- Honest finding: naive online learning degrades on non-repeating queries

# CHANGELOG

## Unreleased

### Maintenance loop and ops docs
- Added `crabpath.maintain` with `run_maintenance`, `prune_edges`, and `prune_orphan_nodes`.
- Added `crabpath maintain` CLI command with `--state`, `--tasks`, `--dry-run`, `--max-merges`, and `--prune-below`.
- Added framework-agnostic examples in `examples/ops/` for fast loop and maintenance loop.
- Added `docs/architecture.md` documenting fast/slow loops, integration contracts, and scheduler guidance.
- Added `tests/test_maintain.py` covering maintenance execution, dry-run behavior, prune operations, merge effects, and report accounting.

## v10.4.0 (2026-02-27)

### True REINFORCE policy gradient
- Added `apply_outcome_pg` in `crabpath.learn` for true policy-gradient updates:
  - numerically stable softmax over outgoing edges plus synthetic STOP
  - updates for all outgoing edges at each step using `(1[chosen] - π)` score gradient
  - optional baseline and temperature support
  - weight clipping + Hebbian co-firing preserved
- Exported `apply_outcome_pg` from `crabpath.__init__`.
- Extended `LearningConfig` with `temperature` and `baseline`.

### External benchmark additions
- Added external benchmark harness support for MultiHop-RAG and HotPotQA.
- Added OpenAI embedding cache support for benchmark scripts to support fast repeat runs.

## v10.3.0 (2026-02-27)

### Traversal tiers recalibrated from production data
- **Defaults changed:** `reflex_threshold: 0.8 -> 0.6`, `habitual_range: 0.3-0.8 -> 0.2-0.6`, `inhibitory_threshold: -0.3 -> -0.01`.
- **Production root-cause fix:** inhibitory edges were non-functional because the default threshold was `-0.3` while negatives were near `-0.035`.
- **Tests and sims updated:** adjusted tier-classification expectations and added coverage for `-0.02` as inhibitory.
- Test count increased to **204** in docs to match new coverage.

## v10.2.0 (2026-02-27)

### Traversal engine hardening
- **Traversal termination updated:** stops on hop ceiling, fired-node budget, and context-character budget.
- **Defaults changed:** `beam_width: 3 → 8`, `max_hops: 15 → 30`, `fire_threshold: 0.0 → 0.01`.
- **New control:** `max_fired_nodes` hard-cap added for traversal loops.
- **Context budget enforcement:** `max_context_chars` is enforced during traversal, not only at render time.
- **Default CLI / script behavior:** `query_brain.py` now defaults to `max_context_chars=20000` for logged session flow.
- Test count updated to **203** (from 200).

## v10.1.0 (2026-02-27)

### Real-time correction flow
- **Fired-node logging:** `query_brain.py --chat-id` persists fired nodes to `fired_log.jsonl` per conversation, with 7-day rolling prune. Corrections can now find what to penalize even hours after the original query.
- **Same-turn corrections:** new `learn_correction.py` reads fired log by chat_id, penalizes via `apply_outcome`, and optionally injects a CORRECTION node — all in one command.
- **Dedup with batch harvester:** `injected_corrections.jsonl` prevents double-injection when the 2-hour harvester later processes the same correction. `init_agent_brain.py` reads the dedup log on rebuild.

### CLI DX improvements
- **Query text output shows node IDs** — no more `--json` required for the learn workflow. Format: `node_id / ~~~ / content`.
- **`learn --json` returns summary** (`{"edges_updated": N, "max_weight_delta": X}`) instead of dumping the entire graph.
- **`health` text output is human-readable** — `Brain health: / Nodes / Edges / Reflex% Habitual% Dormant% / Orphans / Cross-file edges`.
- **`inject` auto-detects hash-v1 embedder** and defaults `--connect-min-sim` to 0.0 (was 0.3, causing zero connections for users without OpenAI).

### OpenAI integration
- `crabpath/openai_embeddings.py` — `OpenAIEmbedder` class wrapping `text-embedding-3-small`.
- `crabpath/openai_llm.py` — `openai_llm_fn` and `chat_completion` for GPT-5-mini routing/scoring.
- CLI flags: `--embedder openai` for init/query/inject, `--llm openai` for init/merge/connect.
- Zero new required dependencies — `openai` is an optional runtime import.

### Documentation overhaul
- **README rewritten:** value prop first, 5-minute quickstart with A→B learning story, "Correcting mistakes" and "Adding new knowledge" sections promoted to top.
- **TEACHING documented:** all three injection types (CORRECTION, TEACHING, DIRECTIVE) explained with examples. Previously only CORRECTION was documented — three production agents independently thought rebuild was required to add new knowledge.
- **Competition table:** CrabPath vs Plain RAG vs Reflexion vs MemGPT.
- **New sections:** State lifecycle, Cost control, "How CrabPath differs from related tools".
- **Session replay demoted** to "Optional: warm start" with skip note for new users.

### New examples
- `examples/cold_start/` — guided zero-session walkthrough with canned queries and expected output.
- `examples/correction_flow/` — generic fired-node logging pattern for any agent framework (hash embedder, no API key).
- `examples/sample_workspace/` expanded from 3 to 5 files (added `incidents.md`, `onboarding.md`) for cross-file routing demos.
- `examples/openclaw_adapter/agents_hook.md` updated with full inject + correction + chat-id logging template.

### Tests
- 200 tests (was 188), 8 simulations all passing.
- New tests: hash-embedder inject default, query text node IDs, health readable output, learn summary, correction flow integration (3 tests).

## v10.0.0
### What Changed
- Added CLI and API flows so CrabPath can inject and persist correction/teaching signals without rebuilding the entire state.
- Expanded operational guidance and verification workflow so feedback and correction behavior can be validated deterministically.

- Added live injection APIs (`inject_node`, `inject_correction`, `inject_batch`) with CLI support via `crabpath inject`, enabling runtime updates during operation.
- Added direct graph node injection paths for TEACHING, DIRECTIVE, and CORRECTION workflows, plus lightweight injection stats payloads from the CLI.

- Expanded reproducibility docs with live injection verification steps so users can confirm graph updates and health signals after corrective actions.

## v9.3.1
- Hardened command entrypoints and replay/logging behavior for edge cases in graph indexing and state workflows.
- Improved docs around runtime injection, exports, and deterministic test paths to make troubleshooting and operator handoff faster.

## v9.3.0
- Introduced live injection primitives (`inject_*`) and correction-node inhibitory edge behavior.
- Added the `crabpath inject` command path and supporting test coverage for repeatable feedback workflows.

## v9.1.0
- Added adversarial tests and latency benchmark harness updates to surface stability issues before release.
- Added interaction extraction and benchmark cleanup paths so simulation artifacts are predictable across runs.

## v9.0.0
- Delivered 20 user-feedback fixes focused on inhibitory suppression, file-type handling, `max_chars`, and `doctor/info` behavior.
- Tuned graph traversal defaults and diagnostics so noisy retrieval cases now recover more gracefully in production-like inputs.

## v8.0.0
- Unified state format and added dimension validation to prevent accidental embedding mismatches.
- Documented core design tenets to make production constraints explicit for integrators.

## v7.0.0
- Brought `HashEmbedder` into the core implementation as a built-in default path.
- This removed external required dependencies from baseline operation while preserving callback flexibility.

## v6.0-6.1
- Removed subprocess-based paths and deduplicated helper logic to simplify execution flow.
- This reduced operational complexity and improved reliability for smaller deployments.

## v5.0-5.3
- Removed provider-specific integrations and standardized pure callback behavior.
- This made core graph operations less opinionated and easier to adapt across embedding/LLM stacks.

## v4.0-4.5
- Added LLM-based features and batch callback execution paths.
- Improved how route extraction and scoring can combine deterministic traversal with optional model guidance.

## v3.0.0
- Rewrote the graph engine core with zero dependencies.
- Added a stable, dependency-light baseline for local, offline usage and reproducible graph state files.
