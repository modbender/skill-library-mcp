# HCC Memory Architecture

## Hierarchical Cognitive Control for ML Evolution

### Layer 1: Episodic Memory
**Purpose**: Record every experiment in detail

**Structure**:
```json
{
  "phase": 9,
  "timestamp": "2026-02-17T11:11:00",
  "method": "Target Stats Features",
  "features": 52,
  "cv_score": 0.95546,
  "lb_score": 0.95365,
  "training_time_min": 8,
  "status": "success",
  "key_changes": ["Added target mean/count for all features"]
}
```

**When to update**: After every phase

---

### Layer 2: Pattern Memory
**Purpose**: Extract abstract patterns from experiments

**Success Patterns**:
```
PATTERN: target_stats
  condition: tabular data with categorical features
  action: for each feature, add target.mean() and target.count()
  expected_gain: +0.0001 to +0.0002 LB
  confidence: HIGH (proven in Phase 9)
  
PATTERN: simple_blend
  condition: multiple models available
  action: CatBoost 50% + XGBoost 25% + LightGBM 25%
  expected_gain: stable baseline
  confidence: HIGH
```

**Failure Patterns**:
```
PATTERN: too_many_features
  condition: feature_count > 60
  result: training timeout or SIGKILL
  solution: limit to < 50 features
  
PATTERN: over_engineering
  condition: adding complex interaction features
  result: CV up but LB down (overfitting)
  solution: keep features simple
```

---

### Layer 3: Knowledge Memory
**Purpose**: Domain knowledge and techniques

**Feature Engineering Library**:

| Technique | Description | Code |
|-----------|-------------|------|
| Target Mean | Mean of target per feature value | `df.groupby(col)['target'].mean()` |
| Target Count | Count per feature value | `df.groupby(col)['target'].count()` |
| Smooth Encoding | Regularized target encoding | `(count * mean + smoothing * global_mean) / (count + smoothing)` |
| Frequency | Value frequency | `df[col].value_counts(normalize=True)` |
| HR Reserve | 220 - Age - Max HR | `220 - df['Age'] - df['Max HR']` |
| Double Product | BP × HR / 100 | `df['BP'] * df['Max HR'] / 100` |

**Model Knowledge**:

```python
CATBOOST_OPTIMAL = {
    'iterations': 1000,
    'learning_rate': 0.05,
    'depth': 6,
    'l2_leaf_reg': 1,
    'random_seed': 42
}

XGBOOST_OPTIMAL = {
    'n_estimators': 1000,
    'learning_rate': 0.05,
    'max_depth': 6,
    'min_child_weight': 5,
    'random_state': 42
}

LIGHTGBM_OPTIMAL = {
    'n_estimators': 1000,
    'learning_rate': 0.05,
    'num_leaves': 31,
    'random_state': 42
}
```

---

### Layer 4: Strategic Memory
**Purpose**: High-level decision rules

**Evolution Strategy**:
```
EXPLORATION_PHASE (Phase 1-5):
  - Try diverse approaches
  - Test feature engineering ideas
  - Build baseline models
  
EXPLOITATION_PHASE (Phase 6-10):
  - Focus on what works
  - Fine-tune parameters
  - Optimize successful features
  
CONVERGENCE_PHASE (Phase 11+):
  - Minor adjustments only
  - Risk-averse changes
  - Target specific gaps
```

**Resource Management**:
```
if training_time > 15_min:
  reduce iterations by 20%
  or reduce features by 10%

if feature_count > 55:
  warn("Approaching resource limit")
  
if daily_submissions >= 9:
  warn("Submission quota almost reached")
  save_remaining_for_best_model()
```

**Goal Achievement**:
```
if current_lb >= target:
  if margin > 0.0001:
    declare_success()
    continue_for_higher_target()
  else:
    declare_success()
    stop_evolution()
```
