# /backtest-optimize - Strategy Optimization Workflow

Run GPU-accelerated strategy optimization with proper MTF and validation.

## Autonomous Doctrine (Mandatory)

This workflow is always-on and goal-locked. It must continuously push toward tradeable alpha and must not stop on single-point failures.

- Persistent awareness and state management are mandatory.
- Instant reactivity to failure signatures is mandatory.
- Continuous self-healing action loops are mandatory.
- Continuous communication through state/log artifacts is mandatory.
- Goal-driven operation is mandatory until run gates are complete.

### Persistent Awareness And State Management

- Every control cycle must read and reconcile state from watchdog, progress, swarm control, process audit, session logger, utilization controller, and orchestrator consensus.
- State freshness is enforced. Missing or stale state must trigger immediate control-plane repair (`ensure_swarm_watchdogs` / tmux session recovery).
- Workload status must be tracked from both process-space (`pgrep`, PID liveness, GPU compute bindings) and artifact-space (progress JSON, result artifacts, log activity).
- Failure memory must be persistent and append-only via:
`docs/reference/FAILURE_POINTS_BACKTEST_OPTIMIZE.json`,
`docs/reference/KNOWLEDGE_BASE_BACKTEST.md`,
`<state_root>/workflow_events.log`.

### Instant Reactivity To Problem Signatures

- On worker crash, stuck worker, stale progress, OOM, or failed GPU path:
  detect in the same control cycle, execute remediation immediately, and re-verify outcome.
- If no active optimize workers exist and launcher is not active, relaunch immediately subject only to cooldown guardrails.
- If GPU is below target while work queue exists, trigger GPU fill lanes.
- If CPU is below target while work queue exists, trigger CPU fill lanes.
- If an action is executable locally by the swarm, execute immediately. Do not wait for manual direction.

### Continuous Self-Healing Dictation And Execution

- Remediation flow is deterministic and continuous:
  detect -> classify -> execute -> verify -> log -> continue.
- `session_state_manager` is the canonical continuity authority:
  - detects stale/missing state, no-worker timeouts, stalled progress, low-util-with-queue,
  - executes bounded auto-resolution actions (`ensure_swarm_watchdogs`, relaunch, sentry/util one-shot),
  - persists `next_steps` and expected outcomes continuously.
- `worker_sentry` owns stuck-worker detection and kill/relaunch behavior.
- `operation_hang_guard` owns cross-operation hang detection (session liveness + state freshness + stalled operation rules) with bounded auto-healing.
- `auto_scheduler` owns idle-pool relaunch behavior for main rounds.
- `util_controller` owns CPU/GPU utilization enforcement lanes.
- `main_orchestrator` owns next-step reasoning and action dispatch.
- `orchestration_consensus` owns cross-signal arbitration and deviation/performance/efficiency scoring.
- Recovery actions must be written to state and logs every cycle (`actions_last_cycle`, run events, session snapshots).
- Phase 0 throughput guardrails are mandatory:
  - prescreen lanes must use throughput-first GPU defaults (`raw_kernel` and adaptive/kernel batch sizing),
  - combo generation must remain vectorized (no per-combo Python RNG loops),
  - oversized Phase 0 workers that exceed runtime budget must be terminated and replaced automatically,
  - fill-lane prescreen volume must be bounded to ensure seed artifacts are produced in hours, not days.
 - Phase handoff guardrails are mandatory:
  - CPU phase1 lanes must run with `--gpu -1` (no accidental CUDA context),
  - phase1 warm-start must search GPU artifacts across lane roots (`--phase0-seed-dirs` or sibling fallback),
  - phase1 logs must show `Loaded Phase0 seed:` for each symbol/mode before long Optuna runs.

### Continuous Communication Contract

- Communication is machine-verifiable and continuous, not ad hoc:
  - session heartbeat JSONL (`session_state_<RUN_ID>.jsonl`)
  - latest snapshot (`session_latest.json`)
  - continuity manager state (`session_state_manager_state.json`)
  - continuity event stream (`session_state_manager_events.jsonl`)
  - stateful expected outcomes story (`docs/reference/WORKFLOW_EXPECTED_OUTCOMES_STATEFUL.md`)
  - control states (`swarm_control_state.json`, `auto_scheduler_state.json`, `util_controller_state.json`, `orchestration_consensus_state.json`, `main_orchestrator_state.json`, `worker_sentry_state.json`, `operation_hang_guard_state.json`)
  - event trail (`workflow_events.log`)
- Human escalation is only for true external decisions or hard platform constraints.
- All other corrective actions are autonomous and immediately executed.

### Goal-Driven Operation

- Primary objective: produce robust, validated, tradeable alpha artifacts.
- Secondary objectives:
  - maintain hardware occupancy targets,
  - preserve statistical validity (min trades, validation gates),
  - persist reproducible evidence and handoff context.
- The workflow is not considered done while actionable next steps still exist in state.

## One Command (Recommended)

Starts the control plane tmux loops and launches work jobs:

```bash
scripts/backtest-optimize --parallel
```

## Always-On Ops (Recommended)

Run watchdog + curator loops in parallel with backtests:

```bash
bash scripts/start_swarm_watchdogs.sh
```

For local Mac/Linux runs outside `/workspace`, set explicit roots + venv so one-shot agents
(`bt-watchdog`, `bt-curator`, `bt-session-log`, `bt-auto-scheduler`, `bt-operation-hang-guard`) do not silently die:

```bash
VENV_PATH=/Users/DanBot/Desktop/alpha_gen/.venv-vectorbtpro-sys/bin/activate \
RESULTS_ROOT=/Users/DanBot/Desktop/backtests_new \
STATE_ROOT=/Users/DanBot/Desktop/backtests_new/state \
LOGS_ROOT=/Users/DanBot/Desktop/backtests_new/logs \
bash scripts/start_swarm_watchdogs.sh
```

Idempotent auto-init (preferred for shell hooks/startup scripts):

```bash
bash scripts/ensure_swarm_watchdogs.sh
```

This keeps hardware occupancy high, records failures (OOM/fallback/env drift), continuously appends findings to the workflow knowledge base, and snapshots knowledge-plane readiness.
It also writes unified control state to:

- `/workspace/backtests_new/state/swarm_control_state.json`

Additional advisory loops (started by default):
- budget guard
- quant analyst (artifact summary)
- hypothesis runner (ledger snapshot)
- auto scheduler (keeps new rounds launching when workers go idle, and can auto-launch a GPU fill lane when GPU util drops below target)
- util controller (actively launches CPU/GPU fill lanes to enforce utilization SLO)
- orchestration consensus (deviation/performance/efficiency scoring each cycle)
- main orchestrator (state-aware reasoning/action dispatch with next-step queueing)
- worker sentry (detects stuck workers, kills/relaunches autonomously, and protects no-worker dead-zones)
- operation hang guard (detects hangs for every operation class, enforces state/session freshness, bounded process kill + swarm repair)
- session state manager (canonical continuity + auto-heal + queryable next-step authority)
- helper monitors (attach anytime): `bt-worker-gpu-mon`, `bt-worker-cpu-mon`, `bt-worker-progress`, `bt-worker-log-index`

Continuity state query:

```bash
python3 scripts/infra/session_state_manager.py \
  --query \
  --state-file /workspace/backtests_new/state/session_state_manager_state.json \
  --json
```

## Auto-Start Swarm When Launching Parallel Jobs

If you run `WORKFLOW/launch_parallel.sh` directly, it now auto-starts the tmux swarm (if `tmux` is available and `scripts/start_swarm_watchdogs.sh` exists). Disable with:

```bash
SWARM_ENABLED=false WORKFLOW/launch_parallel.sh
```

## Knowledge Handoff (Mandatory)

Before ending any major run, complete the handoff workflow in:

- `docs/reference/KNOWLEDGE_HANDOFF_WORKFLOW.md`
- Optional vendor graph ingest (VectorBT PRO): `docs/reference/VECTORBT_GRAPH_INGEST.md`
- Optional full private docs ingest (VectorBT PRO): `docs/reference/VECTORBT_PRIVATE_DOCS_INGEST.md`

Minimum required handoff outputs:

1. Dated run handoff file: `docs/reference/HANDOFF_SWARM_RUN_<YYYY-MM-DD>_<HHMMZ>.md`
2. Append concise findings to: `docs/reference/KNOWLEDGE_BASE_BACKTEST.md`
3. Record verification evidence from:
   - `pytest backtest_server/tests/test_knowledge_*.py -v`
   - `python3 -m scripts.knowledge.router --query \"...\" --domain-hint <domain>`
   - `python3 scripts/knowledge_plane_health.py --json`

## Quick Start

```bash
# 1. Validate before running
python ~/Desktop/alpha_gen/backtest_optimize/WORKFLOW/validation.py \
  --check-all --data-path /path/to/data --symbol SOL

# 2. Run optimization (if validation passes)
ssh -p PORT root@HOST "cd /root/WORKFLOW && python optimize_strategy.py \
  --data-path /root/data --symbol SOL --mode aggressive \
  --prescreen 1000 --paths 100"

# 3. Generate a QuantStats-style tearsheet from a trades CSV
scripts/generate-tearsheet SOL_MTF_EMA_001 --trades /path/to/trades.csv --capital 10000 --output ./tearsheets
```

## Workflow Phases

### Phase 0: Pre-Flight Validation
**MANDATORY before every optimization run**

```bash
python validation.py --check-all --data-path DATA_PATH --symbol SYMBOL
```

Checks:
- MTF resampling implemented (not just params)
- Min trades >= 30 (not 5 or 10)
- Data >= 90 days
- No gaps/NaN in data

### Phase 1: GPU Prescreening
- Generate N random param combos
- Batch evaluate on GPU
- Filter by min trades (30+)
- Return top K by Sharpe
- Prekernel gate: first kernel marker (`Batch 1/`) must appear within 120s per worker.
- Artifact gate: do not advance until `phase0_top500.json` exists for each expected symbol/mode.
- Performance baseline (RTX 5090, raw-kernel, 730d lookback, 250k combos):
  - combo generation: ~1s per mode,
  - total phase0 per mode: ~4s (including ranking/top-k serialization),
  - if runtime regresses to 30s+ per mode, treat as a regression and trigger workflow self-healing.

Distributed policy notes:
- Ray Tune trials must declare explicit `cpu/gpu` resources and cluster-fit `max_concurrent_trials`.
- Optuna distributed runs must use persistent shared storage (`JournalStorage`/`RDBStorage`; `GrpcStorageProxy` at large scale), not in-memory storage.

### Phase 2: Bayesian Optimization
- Optuna with warm-start from Phase 1
- Respect min trades constraint
- Save multiple "best" configs (Sharpe, returns, drawdown, etc.)

### Phase 3: Validation
- Walk-forward test
- Out-of-sample verification
- Monte Carlo stress test

## Critical Requirements

### MTF Must Be Working
The strategy uses Multi-TimeFrame EMAs:
- Fast EMA: 15/30/45/60 minute timeframes
- Slow EMA: 60/120/240/360 minute timeframes

**Verify MTF is implemented:**
```python
# This should be in gpu_batch_engine.py
from mtf_resampler import resample_ohlc, align_to_base_tf_gpu
mtf_data = precompute_mtf_data(close, open_, high, low, timeframes, 5)
```

### Min Trades >= 30
Statistical significance requires 30+ trades.

**Verify in code:**
```python
MIN_TRADES = 30
valid = [r for r in results if r.get('total_trades', 0) >= MIN_TRADES]
```

## Files

| File | Purpose |
|------|---------|
| `validation.py` | Pre-flight checks |
| `mtf_resampler.py` | MTF resampling functions |
| `gpu_batch_engine.py` | GPU batch backtest |
| `optimize_strategy.py` | Main optimization pipeline |
| `apply_fixes.py` | Auto-fix common issues |

## Common Issues

### Issue: Only 6 trades in 1 year
**Cause**: MTF not implemented
**Fix**: Ensure `mtf_resampler` is imported and used

### Issue: CPU fallback (40+ min)
**Cause**: Wrong argument order
**Fix**: `gpu_prescreen(close, open_, high, low, mode, n_combos=X)`

### Issue: Unrealistic Sharpe
**Cause**: Too few trades (overfitting)
**Fix**: Set `MIN_TRADES = 30`

## Deploy to Server

```bash
# Copy fixed files to vast.ai
scp -P PORT mtf_resampler.py validation.py root@HOST:/root/WORKFLOW/

# Apply fixes remotely
ssh -p PORT root@HOST "cd /root/WORKFLOW && python apply_fixes.py --engine-path gpu_batch_engine.py --apply"

# Verify
ssh -p PORT root@HOST "cd /root/WORKFLOW && python validation.py --check-all"
```

For current Vast template and persistent storage settings, use:

- `docs/VAST_TEMPLATE_AND_STORAGE_PLAYBOOK.md`

## Example Full Run

```bash
# 1. Validate
python validation.py --check-all --data-path /root/data --symbol SOL

# 2. Optimize (if validation passes)
python optimize_strategy.py \
  --data-path /root/data \
  --symbol SOL \
  --mode aggressive \
  --prescreen 5000 \
  --paths 200 \
  --engine gpu

# 3. Check results
cat Backtests/optimizations/SOL/aggressive/best_sharpe/metrics.json
```

## Results Location

```
Backtests/optimizations/{SYMBOL}/aggressive/
├── best_sharpe/
│   ├── config.json      # Best Sharpe config
│   └── metrics.json     # Performance metrics
├── best_returns/
├── lowest_drawdown/
├── best_winrate/
├── all_trials.json      # All Optuna trials
└── phase0_top500.json   # Phase 0 prescreening results
```

<!-- AUTO-WORKFLOW-NOTES:START -->
## Auto Workflow Notes (Maintained By Swarm)
- Updated UTC: `2026-02-12T09:42:52.947228+00:00`
- Run ID: `bt-20260211_233304Z`
- Stage: `unknown`
- Hardware snapshot: CPU `81.91`%, GPU `0.0`%
- Active actions: `skip_gpu_actions_no_gpu_detected, knowledge_plane_not_ready, process_efficacy_low`
- Process scores: adherence `80.0`, efficacy `35.97`
- Agent registry roles loaded: `30` from `/Users/DanBot/Desktop/alpha_gen/backtest_optimize/agents/AGENT_REGISTRY.md`
- agents.db tables: `27` at `/Users/DanBot/.agentdb/vectors.db` (skills=0, events=0)

### Active Incidents
- CPU utilization below target (75.1% < 80.0%).
- Process check missing: latest_handoff_recent.

### Immediate Remediations
- Increase Nautilus/Optuna worker concurrency until CPU target is met.
- Knowledge plane not ready; start MindsDB/Postgres or fix connectivity before handoff claims.
- CPU under target; increase Nautilus/Optuna worker count if job queue exists.
- No metrics artifacts found; check scheduler state and output paths.
- Generate a fresh HANDOFF_SWARM_RUN_<timestamp>.md with verification evidence.
- Session manager next step: maintain_polling_and_keep_workers_saturated
<!-- AUTO-WORKFLOW-NOTES:END -->















































































































































































































































































































































































































































































































































