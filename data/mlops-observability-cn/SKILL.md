---
name: mlops-observability-cn
version: 1.0.0
description: Full stack observability - reproducibility, lineage, monitoring, alerting
license: MIT
---

# MLOps Observability 👁️

Glass box system - reproducible, traceable, monitored.

## Features

### 1. MLflow Tracking 📊

Complete tracking setup:

```bash
cp references/mlflow-tracking.py ../your-project/src/tracking.py
```

Tracks:
- Config (params)
- Metrics (accuracy, loss)
- Models (sklearn/pytorch)
- Datasets (lineage)
- Git commit (reproducibility)

### 2. Drift Detection 📉

Using Evidently:

```python
from evidently import Report
from evidently.metrics import DataDriftTable

report = Report(metrics=[DataDriftTable()])
report.run(reference_data=train, current_data=prod)
```

### 3. Explainability (SHAP) 🔍

```python
import shap

explainer = shap.TreeExplainer(model)
shap_values = explainer.shap_values(X)
shap.summary_plot(shap_values, X)
```

## Quick Start

```bash
# Copy tracking code
cp references/mlflow-tracking.py ./src/

# Add to training script:
# from tracking import setup_tracking, log_training_run
```

## Reproducibility

```python
# Set all seeds
import random, numpy as np, torch
random.seed(42)
np.random.seed(42)
torch.manual_seed(42)

# Track git commit
import git
commit = git.Repo().head.commit.hexsha
mlflow.log_param("git_commit", commit)
```

## Monitoring Checklist

- [ ] Random seeds fixed
- [ ] MLflow tracking enabled
- [ ] System metrics logged
- [ ] Drift detection setup
- [ ] SHAP explanations saved
- [ ] Alerts configured

## Alerting

- **Local**: `plyer` notifications
- **Production**: PagerDuty (critical) / Slack (warnings)

## Author

Converted from [MLOps Coding Course](https://github.com/MLOps-Courses/mlops-coding-skills)

## Changelog

### v1.0.0 (2026-02-18)
- Initial OpenClaw conversion
- Added MLflow tracking code
