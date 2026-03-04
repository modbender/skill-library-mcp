---
name: MLOps
slug: mlops
version: 1.0.0
description: "Deploy ML models to production with pipelines, monitoring, serving, and reproducibility best practices."
metadata: {"clawdbot":{"emoji":"🤖","requires":{"bins":[]},"os":["linux","darwin","win32"]}}
---

## Quick Reference

| Topic | File | Key Trap |
|-------|------|----------|
| CI/CD and DAGs | `pipelines.md` | Coupling training/inference deps |
| Model serving | `serving.md` | Cold start with large models |
| Drift and alerts | `monitoring.md` | Only technical metrics |
| Versioning | `reproducibility.md` | Not versioning preprocessing |
| GPU infrastructure | `gpu.md` | GPU request = full device |

## Critical Traps

**Training-Serving Skew:**
- Preprocessing in notebook ≠ preprocessing in service → silent bugs
- Pandas in notebook → memory leaks in production (use native types)
- Feature store values at training time ≠ serving time without proper joins

**GPU Memory:**
- `requests.nvidia.com/gpu: 1` reserves ENTIRE GPU, not partial memory
- MIG/MPS sharing has real limitations (not plug-and-play)
- OOM on GPU kills pod with no useful logs

**Model Versioning ≠ Code Versioning:**
- Model artifacts need separate versioning (MLflow, W&B, DVC)
- Training data version + preprocessing version + code version = reproducibility
- Rollback requires keeping old model versions deployable

**Drift Detection Timing:**
- Retraining trigger isn't just "drift > threshold" → cost/benefit matters
- Delayed ground truth makes concept drift detection lag weeks
- Upstream data pipeline changes cause drift without model issues

## Scope

This skill ONLY covers:
- CI/CD pipelines for models
- Model serving and scaling
- Monitoring and drift detection
- Reproducibility practices
- GPU infrastructure patterns

Does NOT cover: ML algorithms, feature engineering, hyperparameter tuning.
