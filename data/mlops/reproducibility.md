# Reproducibility and Versioning

## What to Version (ALL of these)

| Artifact | Tool | Trap |
|----------|------|------|
| Code | Git | Only versioning code isn't enough |
| Training data | DVC, LakeFS | Git LFS doesn't scale for TB |
| Preprocessing | Same as code | Often forgotten → training-serving skew |
| Model artifacts | MLflow, W&B | Separate from code versioning |
| Environment | `requirements.txt` pinned | Conda dump is too verbose |

## Data Versioning Traps

- ❌ Assuming data fits in Git → use DVC for large datasets
- ❌ Not versioning preprocessing logic separately
- ❌ Only versioning raw data, not derived features
- ❌ `.gitignore` excluding artifacts you need to track

## Experiment Tracking

**What to log:**
- All hyperparameters (including implicit ones like schedulers)
- Metrics per epoch, not just final
- Data version used
- Random seeds
- Environment/dependency versions

**What agents miss:**
- ❌ Only final metrics, no intermediate
- ❌ Implicit hyperparameters (augmentation, LR schedule)
- ❌ Remote artifact store config (defaults to local)
- ❌ Which data version was used

## Environment Reproducibility

```bash
# Good: pinned versions
pip freeze > requirements.txt

# Better: separate dev/prod
requirements-train.txt  # Dev tools, notebooks
requirements-serve.txt  # Minimal inference deps

# Validate reproducibility
python validate_model.py --compare-outputs
```

## Determinism Checklist

- [ ] Random seeds set (numpy, torch, random)
- [ ] Dependency versions pinned
- [ ] Data loading order deterministic
- [ ] GPU operations deterministic (where possible)
- [ ] Same output from saved model checkpoint
