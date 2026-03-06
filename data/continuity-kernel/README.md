# continuity-kernel

**Fail-open continuity kernel for OpenClaw** — deterministic Soul Card + Mission Ticket injection, runtime contract canonicalization, and shadow-mode eval receipts.

## Features

- **Bounded llm_input continuity packet injection** (`runtime_hooks -> service -> injector`)
- **Runtime state fingerprinting** with restart-invariant deterministic digest
- **First-run bootstrap** with automatic SQLite migration (zero manual setup)
- **Durable default storage path** at `~/.local/state/continuity-kernel/continuity.db` (override with `CONTINUITY_KERNEL_DB_PATH`; `:memory:` is explicit opt-in only)
- **Fail-open runtime behavior** (baseline payload preserved on any continuity failure)
- **Deterministic runtime contract digests** for continuity packets and drift warnings
- **Dual-route selector prototype** behind explicit `dual_route_experimental` policy mode with fail-open fallback
- **Attention-preserving compaction prototype** behind `attention_preserving_experimental` policy mode with dropped-field A/B receipts
- **Trace-backed shadow eval harness** with suite support for:
  - `memoryarena-mini` (SC-01)
  - `memoryarena-mini-perturb` with deterministic perturb profiles (`deletion`, `noise_injection`, `reorder`)
  - `core-shadow` synthetic stress lane
- **Quality/verification metrics**:
  - resume_success_rate
  - reprompt_rate
  - off_goal_tool_call_rate
  - continuity_lift_delta
  - weak_check_score
  - strong_check_triggered
  - incorrect_accept_rate
  - incorrect_reject_rate
  - runtime_state_fingerprint_drift_rate
- **Rolling verification calibration receipts** over a 5-snapshot observed-trace window
- **Compaction A/B/C ablation receipts** (`A_size_only`, `B_dual_route_size_only`, `C_dual_route_attention_preserving`)
- **Machine-readable receipts**:
  - `~/.cache/continuity-kernel/checkpoints/*runtime_contract_proof*.json`
  - `~/.cache/continuity-kernel/p0-evals/<timestamp>/summary.json`
  - `~/.cache/continuity-kernel/p0-evals/<timestamp>/trace-bundle.jsonl`

## Quick Start

```bash
# From repo root
python3 -m unittest discover -s tests/continuity-kernel -p 'test_*.py'
python3 skills/continuity-kernel/generate_runtime_contract_proof.py

# SC-02 core-shadow gate (synthetic lane, no trace required)
python3 skills/continuity-kernel/run_shadow_eval.py --layer 'Soul Card' --chunk 'SC-02' --suite core-shadow --runs 100 --append artifacts/continuity-kernel/p0-evals.json

# SC-02 perturb gate (deterministic selector + size_only)
python3 skills/continuity-kernel/run_shadow_eval.py --layer 'Soul Card' --chunk 'SC-02' --suite memoryarena-mini-perturb --perturb-profile deletion --selector-mode deterministic --compaction-policy size_only --runs 100 --trace-jsonl tests/continuity-kernel/fixtures/shadow_eval_trace_memoryarena_mini_perturb.jsonl --append artifacts/continuity-kernel/p0-evals.json

# SC-02 perturb gate (dual-route + attention-preserving)
python3 skills/continuity-kernel/run_shadow_eval.py --layer 'Soul Card' --chunk 'SC-02' --suite memoryarena-mini-perturb --perturb-profile deletion --selector-mode dual_route_experimental --compaction-policy attention_preserving_experimental --runs 100 --trace-jsonl tests/continuity-kernel/fixtures/shadow_eval_trace_memoryarena_mini_perturb.jsonl --append artifacts/continuity-kernel/p0-evals.json
```

## Usage

```bash
# From skill directory
cd skills/continuity-kernel
python3 -m unittest discover -s ../../tests/continuity-kernel -p 'test_*.py'
python3 generate_runtime_contract_proof.py
python3 run_shadow_eval.py --layer 'Soul Card' --chunk 'SC-02' --suite core-shadow --runs 100 --append ../../artifacts/continuity-kernel/p0-evals.json
python3 run_shadow_eval.py --layer 'Soul Card' --chunk 'SC-02' --suite memoryarena-mini-perturb --perturb-profile deletion --selector-mode deterministic --compaction-policy size_only --runs 100 --trace-jsonl ../../tests/continuity-kernel/fixtures/shadow_eval_trace_memoryarena_mini_perturb.jsonl --append ../../artifacts/continuity-kernel/p0-evals.json
python3 run_shadow_eval.py --layer 'Soul Card' --chunk 'SC-02' --suite memoryarena-mini-perturb --perturb-profile deletion --selector-mode dual_route_experimental --compaction-policy attention_preserving_experimental --runs 100 --trace-jsonl ../../tests/continuity-kernel/fixtures/shadow_eval_trace_memoryarena_mini_perturb.jsonl --append ../../artifacts/continuity-kernel/p0-evals.json
```

## Requirements

- Python 3.8+
- Python stdlib only (no pip dependencies)
- SQLite (bundled with Python stdlib)

## Install

```bash
clawhub install continuity-kernel
```

Release-ready publish command:

```bash
clawhub publish skills/continuity-kernel
```

## License

MIT — see [LICENSE](LICENSE).
