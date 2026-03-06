---
name: mlops-prototyping-cn
version: 1.0.0
description: Structured Jupyter notebook prototyping with pipeline integrity
license: MIT
---

# MLOps Prototyping 🔬

Create standardized, reproducible Jupyter notebooks.

## Features

### 1. Notebook Structure Check ✅

Validate notebook follows best practices:

```bash
./scripts/check-notebook.sh notebook.ipynb
```

Checks for:
- H1 title
- Imports section
- Config/Constants
- Data loading
- Pipeline usage

### 2. Template 📝

Use this structure:

1. **Title & Purpose**
2. **Imports** (standard → third-party → local)
3. **Configs** (all constants at top)
4. **Datasets** (load, validate, split)
5. **Analysis** (EDA)
6. **Modeling** (use `sklearn.pipeline.Pipeline`)
7. **Evaluations** (metrics on test data)

## Quick Start

```bash
# Check your notebook
./scripts/check-notebook.sh my-notebook.ipynb

# Follow structure in notebook
# Use Pipeline for all transforms
# Set RANDOM_STATE everywhere
```

## Key Rules

✅ **DO:**
- Put all params in Config section
- Use `sklearn.pipeline.Pipeline`
- Split data BEFORE any transforms
- Set `random_state` everywhere

❌ **DON'T:**
- Magic numbers in code
- Manual transforms (use Pipeline)
- Fit on full dataset (data leakage)

## Author

Converted from [MLOps Coding Course](https://github.com/MLOps-Courses/mlops-coding-skills)

## Changelog

### v1.0.0 (2026-02-18)
- Initial OpenClaw conversion
- Added notebook checker
