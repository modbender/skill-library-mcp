---
name: strategy-workflow
description: >
  Comprehensive strategy development workflow from ideation to validation.
  Use when creating trading strategies, running backtests, parameter optimization, or walk-forward validation.
version: "2.0.0"
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
---

# Strategy Workflow

Comprehensive strategy development workflow for quantitative trading, from hypothesis to validated production deployment.

## Overview

This skill provides a complete framework for developing, testing, and validating trading strategies. It supports:

- Hypothesis-driven strategy development
- Multi-GPU backtesting on Vast.ai
- Bayesian hyperparameter optimization with Optuna
- Walk-forward validation and out-of-sample testing
- Automated tearsheet generation

## Entry Points

### Control Plane (Swarm Orchestration)

Always-on watchdog loops that manage hardware utilization and self-healing:

```bash
bash scripts/start_swarm_watchdogs.sh
```

For local environments, set explicit paths:

```bash
VENV_PATH=/path/to/.venv/bin/activate \
RESULTS_ROOT=/path/to/backtests \
STATE_ROOT=/path/to/backtests/state \
LOGS_ROOT=/path/to/backtests/logs \
bash scripts/start_swarm_watchdogs.sh
```

### Work Plane (Parallel Execution)

Unified wrapper that starts control plane and launches parallel work:

```bash
scripts/backtest-optimize --parallel
```

Multi-GPU, multi-symbol execution:

```bash
cd WORKFLOW && ./launch_parallel.sh
```

### Single-Symbol Pipeline

For focused optimization on a single asset:

```bash
scripts/backtest-optimize --single --symbol SYMBOL --engine native --prescreen 50000 --paths 1000 --by-regime
```

## Strategy Development

### 1. Hypothesis Formulation

Define your strategy hypothesis in measurable terms:

- What market inefficiency are you exploiting?
- What is the expected holding period?
- What are the entry/exit conditions?
- What is the target risk-adjusted return?

### 2. Feature Selection

Identify relevant features for signal generation:

- Price-based (OHLCV, returns, volatility)
- Technical indicators (EMA, RSI, Bollinger Bands)
- Multi-timeframe features (MTF resampling)
- Volume analysis (PVSRA, VWAP)
- Market microstructure (order flow, spread)

### 3. Signal Generation

Convert features into actionable signals:

- Directional bias (trend following, mean reversion)
- Entry conditions (threshold crossings, pattern recognition)
- Exit conditions (take-profit, stop-loss, trailing stops)
- Position sizing rules

### 4. Position Sizing

Implement risk-aware position sizing:

- Fixed fractional
- Kelly criterion
- Volatility-adjusted
- Regime-dependent scaling

## Backtesting

### Pre-Flight Validation

**MANDATORY** before every optimization run:

```bash
python validation.py --check-all --data-path DATA_PATH --symbol SYMBOL
```

Validation checks:
- Data >= 90 days with no gaps/NaN
- Min trades >= 30 for statistical significance
- MTF resampling implemented correctly
- No look-ahead bias

### Multi-GPU Execution on Vast.ai

Deploy to cloud GPU instances for large-scale parameter sweeps:

```bash
# Copy workflow files
scp -P PORT workflow_files root@HOST:/root/WORKFLOW/

# Run optimization
ssh -p PORT root@HOST "cd /root/WORKFLOW && python optimize_strategy.py \
  --data-path /root/data --symbol SYMBOL --mode aggressive \
  --prescreen 5000 --paths 200 --engine gpu"
```

### Prescreening with Vectorized Backtests

Phase 0: GPU-accelerated parameter screening:

- Generate N random parameter combinations
- Batch evaluate on GPU
- Filter by minimum trades (30+)
- Return top K by Sharpe ratio

Performance baseline (RTX 5090, 730d lookback, 250k combos): ~4s per mode.

### Full Backtests with NautilusTrader

Phase 1: Event-driven backtesting for top candidates:

- High-fidelity simulation with realistic execution
- Slippage and commission modeling
- Multi-asset portfolio backtests

## Parameter Optimization

### Optuna for Hyperparameter Search

Phase 2: Bayesian optimization with warm-start from prescreening:

```python
import optuna

study = optuna.create_study(
    direction="maximize",
    sampler=optuna.samplers.TPESampler(seed=42),
    pruner=optuna.pruners.MedianPruner()
)

study.optimize(objective, n_trials=1000)
```

### Grid Search vs Bayesian Optimization

| Method | Use Case |
|--------|----------|
| Grid Search | Small parameter space, exhaustive coverage needed |
| Random Search | Large space, quick exploration |
| Bayesian (TPE) | Efficient optimization, exploitation/exploration balance |
| CMA-ES | Continuous parameters, smooth objective |

### Pruning Strategies

- **MedianPruner**: Prune if worse than median of completed trials
- **PercentilePruner**: Prune bottom X% of trials
- **HyperbandPruner**: Multi-fidelity optimization
- **SuccessiveHalvingPruner**: Aggressive early stopping

### Distributed Optimization

For large-scale runs, use persistent storage:

```python
# JournalStorage for multi-process
storage = optuna.storages.JournalStorage(
    optuna.storages.JournalFileStorage("journal.log")
)

# RDBStorage for distributed clusters
storage = optuna.storages.RDBStorage("postgresql://...")
```

## Walk-Forward Validation

### Rolling Window Validation

Slide the training/test window through time:

```
[Train 1][Test 1]
    [Train 2][Test 2]
        [Train 3][Test 3]
```

Parameters:
- `train_window`: Training period length
- `test_window`: Out-of-sample test length
- `step_size`: Window advancement increment

### Anchored Walk-Forward

Expand training window while sliding test window:

```
[Train 1      ][Test 1]
[Train 1 + 2      ][Test 2]
[Train 1 + 2 + 3      ][Test 3]
```

Use when historical regime diversity improves model robustness.

### Epoch Selection Criteria

Intelligent selection of training periods:

- **Regime-aware**: Match training regimes to expected deployment conditions
- **Volatility-adjusted**: Include both high and low volatility periods
- **Event-inclusive**: Ensure major market events are represented
- **Recency-weighted**: Emphasize recent data while maintaining diversity

### Out-of-Sample Testing

Final validation phase:
- Hold out 20-30% of data for final OOS test
- No parameter tuning on OOS data
- Monte Carlo stress testing
- Regime-conditional performance analysis

## SLOs and Guardrails

### Utilization Targets

- CPU utilization target: >= 70%
- GPU utilization target: >= 70%
- No silent GPU fallback for GPU sweeps

### Hardware Watchdog Hooks

Enforced by:
- `hooks/hardware_capacity_watchdog.py`
- `scripts/process_auditor.py`

### Capacity Monitoring

Control plane loops monitor:
- Worker health and liveness
- Progress artifact freshness
- Resource utilization
- Job queue depth

Self-healing actions:
- Automatic worker restart on crash
- Fill lanes for underutilized resources
- Cooldown guardrails to prevent thrashing

## Tearsheet Generation

Generate QuantStats-style performance reports:

```bash
scripts/generate-tearsheet STRATEGY_NAME \
  --trades /path/to/trades.csv \
  --capital 10000 \
  --output ./tearsheets
```

See `tearsheet-generator` skill for detailed visualization options.

## Multi-Provider Orchestration

### PAL MCP Integration

Attach PAL as an MCP server for research/consensus across multiple model providers:

- Config template: `config/mcp/pal.mcp.json.example`
- Docs: `docs/reference/PAL_MCP_INTEGRATION.md`
- Providers: OpenRouter, OpenAI, Anthropic, xAI, local models

## Resources

### Documentation

- [VectorBT Documentation](https://vectorbt.dev/)
- [NautilusTrader Docs](https://nautilustrader.io/)
- [Optuna Documentation](https://optuna.readthedocs.io/)
- [QuantStats](https://github.com/ranaroussi/quantstats)

### Project References

- `config/workflow_defaults.yaml` - Default configuration
- `config/model_policy.yaml` - Model policy (advisory)
- `docs/guides/SWARM_OPTIMIZATION_RUNBOOK.md` - Detailed runbook
- `hooks/pipeline-hooks.md` - Hook contracts
- `docs/reference/VECTORBT_GRAPH_INGEST.md` - VectorBT PRO integration

### Results Structure

```
Backtests/optimizations/{SYMBOL}/{MODE}/
  best_sharpe/
    config.json      # Best Sharpe configuration
    metrics.json     # Performance metrics
  best_returns/
  lowest_drawdown/
  best_winrate/
  all_trials.json    # All Optuna trials
  phase0_top500.json # Prescreening results
```
