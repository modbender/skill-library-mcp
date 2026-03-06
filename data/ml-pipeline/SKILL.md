---
name: ml-pipeline
description: >
  Complete machine learning pipeline for trading: feature engineering, AutoML, deep learning, and financial RL.
  Use for automated parameter sweeps, feature creation, model training, and anti-leakage validation.
version: "2.0.0"
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
metadata:
  consolidates:
    - ml-feature-engineering
    - deep-learning-optimizer-5
    - pytorch-lightning-2
    - scikit-learn-ml-framework
    - automl-pipeline-builder-2
    - ml-feature-engineering-helper
    - ml-fundamentals
    - machine-learning-feature-engineering-toolkit
---

# ML Pipeline

Unified skill for the complete ML pipeline within a quant trading research system.
Consolidates eight prior skills into a single authoritative reference covering
the full lifecycle: data validation, feature creation, selection,
transformation, anti-leakage checks, pipeline automation, deep learning optimization, and deployment.

---

## 1. When to Use

Activate this skill when the task involves any of the following:

- Creating, selecting, or transforming features for an ML-driven strategy.
- Auditing an existing feature pipeline for data leakage or overfitting risk.
- Automating an end-to-end ML pipeline (data prep through model export).
- Evaluating feature importance, scaling, encoding, or interaction effects.
- Integrating features with a feature store (Feast, Tecton, custom Parquet store).
- Explaining core ML concepts (bias-variance, cross-validation, regularisation)
  in the context of feature engineering decisions.

---

## 2. Inputs to Gather

Before starting work, collect or confirm:

| Input | Details |
|-------|---------|
| **Objective** | Target metric (Sharpe, accuracy, RMSE ...), constraints, time horizon. |
| **Data** | Symbols / instruments, timeframe, bar type, sampling frequency, data sources. |
| **Leakage risks** | Point-in-time concerns, survivorship bias, look-ahead in labels or features. |
| **Compute budget** | CPU/GPU limits, wall-clock budget for AutoML search. |
| **Latency** | Online vs. offline inference, acceptable prediction latency. |
| **Interpretability** | Regulatory or research need for explainable features / models. |
| **Deployment target** | Where the model will run (notebook, backtest harness, live engine). |

---

## 3. Feature Creation Patterns

### 3.1 Numerical Features

- **Interaction terms**: `price * volume`, `high / low`, `close - open`.
- **Rolling statistics**: mean, std, skew, kurtosis over configurable windows.
- **Polynomial / log transforms**: `log(volume + 1)`, `spread^2`.
- **Binning / discretisation**: equal-width, quantile-based, or domain-driven bins.

### 3.2 Categorical Features

- **One-hot encoding**: for low-cardinality categoricals (sector, exchange).
- **Target encoding**: mean-target per category with smoothing (careful of leakage -- use only in-fold means).
- **Ordinal encoding**: when categories have a natural order (credit rating).

### 3.3 Time-Series Specific

- **Lag features**: `return_{t-1}`, `return_{t-5}`, etc.
- **Calendar features**: day-of-week, month, quarter, options-expiry flag.
- **Rolling z-score**: `(x - rolling_mean) / rolling_std` for stationarity.
- **Fractional differentiation**: preserve memory while achieving stationarity (Lopez de Prado).

### 3.4 Feature Selection Techniques

- **Filter methods**: mutual information, variance threshold, correlation pruning.
- **Wrapper methods**: recursive feature elimination (RFE), forward/backward selection.
- **Embedded methods**: L1 regularisation, tree-based importance, SHAP values.
- **Permutation importance**: model-agnostic; run on out-of-fold predictions.

---

## 4. Anti-Leakage Checks

Data leakage is the single most common cause of inflated backtest results.
Apply these checks at every pipeline stage:

### 4.1 Label Leakage

- Labels must be computed from **future** returns relative to the feature
  timestamp. Verify that the label window does not overlap the feature window.
- Use purging and embargo when labels span multiple bars.

### 4.2 Feature Leakage

- No feature may use information from time `t+1` or later at prediction time `t`.
- Rolling statistics must use a **closed** left window: `df['feat'].rolling(20).mean().shift(1)`.
- Target-encoded categoricals must be computed on the **training fold only**.

### 4.3 Cross-Validation Leakage

- Use **purged k-fold** or **walk-forward** CV for time-series. Never use random
  k-fold on ordered data.
- Insert an **embargo gap** between train and test folds to prevent bleed-through
  from autocorrelation.

### 4.4 Survivorship & Selection Bias

- Ensure the universe of instruments at time `t` reflects what was actually
  tradable at that time (delisted stocks, halted symbols removed later).
- Backfill from point-in-time databases where available.

### 4.5 Validation Checklist

Run before every backtest:

```text
[ ] Labels computed strictly from future returns (no overlap with features)
[ ] All rolling features shifted by at least 1 bar
[ ] Target encoding uses in-fold means only
[ ] Walk-forward or purged CV used (no random shuffle on time-series)
[ ] Embargo gap >= max(label_horizon, autocorrelation_lag)
[ ] Universe is point-in-time (no survivorship bias)
[ ] No global scaling fitted on full dataset (fit on train, transform test)
```

---

## 5. Pipeline Automation (AutoML)

### 5.1 Prerequisites

- Python environment with one or more AutoML libraries:
  Auto-sklearn, TPOT, H2O AutoML, PyCaret, Optuna, or custom Optuna pipelines.
- Training data in CSV / Parquet / database.
- Problem type identified: classification, regression, or time-series forecasting.

### 5.2 Pipeline Steps

| Step | Action |
|------|--------|
| **1. Define requirements** | Problem type, evaluation metric, time/resource budget, interpretability needs. |
| **2. Data infrastructure** | Load data, quality assessment, train/val/test split strategy, define feature transforms. |
| **3. Configure AutoML** | Select framework, define algorithm search space, set preprocessing steps, choose tuning strategy (Bayesian, random, Hyperband). |
| **4. Execute training** | Run automated feature engineering, model selection, hyperparameter optimisation, cross-validation. |
| **5. Analyse & export** | Compare models, extract best config, feature importance, visualisations, export for deployment. |

### 5.3 Pipeline Configuration Template

```python
pipeline_config = {
    "task_type": "classification",        # or "regression", "time_series"
    "time_budget_seconds": 3600,
    "algorithms": ["rf", "xgboost", "catboost", "lightgbm"],
    "preprocessing": ["scaling", "encoding", "imputation"],
    "tuning_strategy": "bayesian",        # or "random", "hyperband"
    "cv_folds": 5,
    "cv_type": "purged_kfold",            # or "walk_forward"
    "embargo_bars": 10,
    "early_stopping_rounds": 50,
    "metric": "sharpe_ratio",             # domain-specific metric
}
```

### 5.4 Output Artifacts

- `automl_config.py` -- pipeline configuration.
- `best_model.pkl` / `.joblib` / `.onnx` -- serialised model.
- `feature_pipeline.pkl` -- fitted preprocessing + feature transforms.
- `evaluation_report.json` -- metrics, confusion matrix / residuals, feature rankings.
- `deployment/` -- prediction API code, input validation, requirements.txt.

---

## 6. Core ML Fundamentals (Feature-Engineering Context)

### 6.1 Bias-Variance Trade-off

- More features increase model capacity (lower bias) but risk overfitting (higher variance).
- Use regularisation (L1/L2), feature selection, or dimensionality reduction to manage.

### 6.2 Evaluation Strategy

- **Walk-forward validation**: the gold standard for time-series strategies.
  Roll a fixed-width training window forward; test on the next out-of-sample period.
- **Monte Carlo permutation tests**: shuffle labels and re-evaluate to estimate
  the probability that observed performance is due to chance.
- **Combinatorial purged CV (CPCV)**: generate many train/test combinations with
  purging for more robust performance estimates.

### 6.3 Feature Scaling

- Fit scalers (StandardScaler, MinMaxScaler, RobustScaler) on the **training set only**.
- Apply the same fitted scaler to validation and test sets.
- RobustScaler is often preferred for financial data due to heavy tails.

### 6.4 Handling Missing Data

- Forward-fill then backward-fill for price data (be aware of leakage on backfill).
- Indicator column for missingness can itself be informative.
- Tree-based models can handle NaN natively; linear models cannot.

---

## 7. Workflow

For any feature engineering task, follow this sequence:

1. **Restate** the task in measurable terms (metric, constraints, deadline).
2. **Enumerate** required artifacts: datasets, feature definitions, configs, scripts, reports.
3. **Propose** a default approach and 1-2 alternatives with trade-offs.
4. **Implement** feature pipeline with anti-leakage checks built in.
5. **Validate** with walk-forward CV, Monte Carlo, and the leakage checklist above.
6. **Deliver** repo-ready code, documentation, and a run command.

---

## 8. Deep Learning Optimization

### 8.1 Optimizer Selection

| Optimizer | Best For | Learning Rate |
|-----------|----------|---------------|
| Adam | Most cases, adaptive | 1e-3 to 1e-4 |
| AdamW | Transformers, weight decay | 1e-4 to 1e-5 |
| SGD + Momentum | Large batches, fine-tuning | 1e-2 to 1e-3 |
| RAdam | Stability without warmup | 1e-3 |

### 8.2 Learning Rate Scheduling

- **OneCycleLR**: Best for short training, fast convergence
- **CosineAnnealing**: Smooth decay, good generalization
- **ReduceOnPlateau**: Adaptive when validation loss plateaus
- **Warmup + Decay**: Standard for transformers

### 8.3 Regularization Techniques

- **Dropout**: 0.1-0.5 for fully connected layers
- **L2 (Weight Decay)**: 1e-4 to 1e-2
- **Batch Normalization**: Stabilizes training
- **Early Stopping**: Monitor validation loss, patience 5-10 epochs

### 8.4 PyTorch Lightning Integration

```python
import pytorch_lightning as pl

class TradingModel(pl.LightningModule):
    def configure_optimizers(self):
        optimizer = torch.optim.AdamW(self.parameters(), lr=1e-4)
        scheduler = torch.optim.lr_scheduler.OneCycleLR(
            optimizer, max_lr=1e-3, total_steps=self.trainer.estimated_stepping_batches
        )
        return [optimizer], [scheduler]
```

### 8.5 Financial Reinforcement Learning

- **State**: Market features, portfolio state, position
- **Action**: Buy/Sell/Hold, position sizing
- **Reward**: Risk-adjusted returns (Sharpe, Sortino)
- **Frameworks**: Stable-Baselines3, RLlib, FinRL

---

## 9. Error Handling

| Problem | Cause | Fix |
|---------|-------|-----|
| AutoML search finds no good model | Insufficient time budget or poor features | Increase budget, engineer better features, expand algorithm search space. |
| Out of memory during training | Dataset too large for available RAM | Downsample, use incremental learning, simplify feature engineering. |
| Model accuracy below threshold | Weak signal or overfitting | Collect more data, add domain-driven features, regularise, adjust metric. |
| Feature transforms produce NaN/Inf | Division by zero, log of negative | Add guards: `np.where(denom != 0, ...)`, `np.log1p(np.abs(x))`. |
| Optimiser fails to converge | Bad hyperparameter ranges | Tighten search bounds, increase iterations, exclude unstable algorithms. |

---

## 10. Bundled Scripts

All scripts live in `scripts/` within this skill directory.

| Script | Purpose |
|--------|---------|
| `data_validation.py` | Validate input data quality before pipeline execution. |
| `model_evaluation.py` | Evaluate trained model performance and generate reports. |
| `pipeline_deployment.py` | Deploy a trained pipeline to a target environment with rollback support. |
| `feature_engineering_pipeline.py` | End-to-end feature engineering: load, clean, transform, select, train. |
| `feature_importance_analyzer.py` | Analyse feature importance (permutation, SHAP, tree-based). |
| `data_visualizer.py` | Visualise feature distributions and relationships to target. |
| `feature_store_integration.py` | Integrate with feature stores (Feast, Tecton) for online/offline serving. |

---

## 11. Resources

### Frameworks

- **scikit-learn** -- preprocessing, feature selection, pipelines.
- **Auto-sklearn / TPOT / H2O AutoML / PyCaret** -- automated pipeline search.
- **Optuna** -- flexible hyperparameter optimisation.
- **SHAP** -- model-agnostic feature importance.
- **Feast / Tecton** -- feature store management.
- **PyTorch Lightning** -- https://lightning.ai/docs/pytorch/stable/
- **Stable-Baselines3** -- https://stable-baselines3.readthedocs.io/
- **FinRL** -- https://github.com/AI4Finance-Foundation/FinRL

### Key References

- Lopez de Prado, *Advances in Financial Machine Learning* (2018) -- purged CV, fractional differentiation, meta-labelling.
- Hastie, Tibshirani & Friedman, *The Elements of Statistical Learning* -- bias-variance, regularisation, model selection.
- scikit-learn user guide: feature extraction, preprocessing, model selection.

### Best Practices

- Always start with a simple baseline before running AutoML.
- Balance automation with domain knowledge -- blind search rarely beats informed priors.
- Monitor resource consumption; set hard timeouts.
- Validate on true out-of-sample holdout data, not just cross-validation.
- Document every pipeline decision for reproducibility.
