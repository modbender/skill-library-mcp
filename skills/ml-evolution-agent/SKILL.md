---
name: ml-evolution-agent
description: "Auto-evolving ML competition agent. Learns from each experiment, accumulates HCC multi-layer memory, and continuously improves LB scores. Inspired by MLE-Bench #1 ML-Master methodology."
metadata:
  openclaw:
    emoji: "🤖"
    version: "1.0.0"
    author: "OpenClaw Agent"
    requires:
      bins: ["kaggle", "python3"]
    tags: ["machine-learning", "kaggle", "auto-ml", "evolution", "memory"]
---

# ML Evolution Agent 🤖

**Auto-evolving ML competition agent** that learns from every experiment.

## What This Skill Does

1. **Auto-evolves ML models** for Kaggle-style competitions
2. **HCC Multi-layer Memory** - Episodic, Pattern, Knowledge, Strategic layers
3. **Continuous improvement** - Each phase learns from previous failures/successes
4. **Resource-aware** - Respects system limits (time, memory, API quotas)

## When to Use

- User mentions Kaggle competition
- Tabular data classification/regression tasks
- Need to beat a target LB score
- User wants automated ML experimentation

## Quick Start

```python
# Initialize
from ml_evolution import MLEvolutionAgent

agent = MLEvolutionAgent(
    competition="playground-series-s6e2",
    target_lb=0.95400,
    data_dir="./data"
)

# Run evolution
agent.evolve(max_phases=10)
```

## HCC Memory Architecture

```
Layer 1: Episodic Memory
├── Experiment logs (phase, CV, LB, features, params)
├── Success/failure records
└── Resource usage tracking

Layer 2: Pattern Memory
├── What works (success patterns)
├── What fails (failure patterns)
└── When to use each approach

Layer 3: Knowledge Memory
├── Feature engineering techniques
├── Model configurations
├── Hyperparameter knowledge
└── Domain-specific features

Layer 4: Strategic Memory
├── Auto-evolution rules
├── Resource management rules
├── Exploration-exploitation balance
└── Competition-specific strategies
```

## Proven Techniques (from real competitions)

### Feature Engineering
| Technique | Effect | Best For |
|-----------|--------|----------|
| Target Statistics | +0.00018 LB | All tabular data |
| Frequency Encoding | +0.00005 LB | High-cardinality features |
| Smooth Target Encoding | +0.00003 LB | Prevent overfitting |
| Medical Indicators | +0.00006 CV | Health data |

### Model Configurations
| Model | Best Params | Weight |
|-------|-------------|--------|
| CatBoost | iter=1000-1200, lr=0.04-0.05, depth=6-7 | 50% |
| XGBoost | n_est=1000-1200, lr=0.04, max_depth=6 | 25-30% |
| LightGBM | n_est=1000-1200, lr=0.04, leaves=40 | 20-25% |

### Resource Limits
- Features: < 60 (avoids timeout)
- Iterations: < 1200 (avoids SIGKILL)
- Training time: < 20 min (system limit)
- Submissions: 10/day (Kaggle quota)

## Evolution Rules

```python
# Auto-evolution decision tree
if phase_improved:
    keep_features()
    try_similar_approach()
elif phase_degraded > 0.0001:
    rollback()
    try_new_direction()
else:
    fine_tune_params()

# Overfitting detection
if cv_lb_gap > 0.002:
    increase_regularization()
    reduce_features()
    simplify_model()
```

## Files Structure

```
ml-evolution-agent/
├── SKILL.md              # This file
├── HCC_MEMORY.md         # Memory architecture details
├── FEATURE_ENGINEERING.md # Feature techniques library
├── MODEL_CONFIGS.md      # Optimal model configurations
├── EVOLUTION_RULES.md    # Auto-evolution decision rules
└── templates/
    ├── train_baseline.py # Baseline training script
    ├── train_evolved.py  # Evolution training script
    └── memory.json       # Example memory state
```

## Example Results

**Playground S6E2 (Feb 2026)**
- Started: LB 0.95347
- Best: LB 0.95365 (+0.00018)
- Phases: 14
- Success rate: 36%
- Target beaten: Yes (0.95361 → 0.95365)

## Key Learnings

1. **Simple > Complex** - Target stats beat complex feature engineering
2. **Resource limits matter** - Too many features = timeout
3. **CatBoost is king** - Consistently best for tabular data
4. **Daily quota awareness** - Kaggle limits submissions

## Installation

```bash
clawhub install ml-evolution-agent
```

---

*Built from real competition experience. Evolved through 14 phases of experimentation.*
