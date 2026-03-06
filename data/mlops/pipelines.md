# CI/CD and DAG Pipelines

## Training Pipelines

**Separate training and inference dependencies:**
- Training needs dev tools, more RAM, different base image
- Inference needs minimal deps, optimized runtime
- ❌ Common mistake: single `requirements.txt` for both

**DAG structure (Airflow, Dagster, Kubeflow):**
```
data_validation → preprocess → train → evaluate → register
                                            ↓
                               validation_failed → alert
```

**Validation gates before registry:**
- Metrics above threshold (accuracy, F1, etc.)
- Model size within limits
- Inference latency test passes
- No data leakage detected

## CI/CD for Models

**GitHub Actions pattern:**
```yaml
on:
  push:
    paths: ['models/**', 'training/**']
jobs:
  train:
    - Validate data schema
    - Run training (with cache)
    - Compare metrics vs baseline
    - Register if improved
```

**Promotion flow:**
- Dev → Staging → Shadow → Canary → Production
- Each stage has its own validation
- Rollback plan before each promotion

## Common Traps

- ❌ Retraining daily without cost analysis (GPUs aren't free)
- ❌ No artifact caching → 4 hour builds that could be 20 min
- ❌ Coupling data ETL with model training DAG
- ❌ Assuming MLflow for everything (evaluate BentoML, Seldon for serving)
- ❌ Kubeflow YAML that works in docs but fails with real CRD versions
