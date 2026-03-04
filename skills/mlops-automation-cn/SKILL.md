---
name: mlops-automation-cn
version: 1.0.0
description: Task automation, containerization, CI/CD, and experiment tracking
license: MIT
---

# MLOps Automation 🤖

Automate tasks, containers, CI/CD, and ML experiments.

## Features

### 1. Task Runner (just) ⚡

Copy justfile:

```bash
cp references/justfile ../your-project/
```

Tasks:
- `just check` - Run all checks
- `just test` - Run tests
- `just build` - Build package
- `just clean` - Remove artifacts
- `just train` - Run training

### 2. Docker 🐳

Multi-stage build:

```bash
cp references/Dockerfile ../your-project/
docker build -t my-model .
docker run my-model
```

Optimizations:
- Layer caching (uv sync before copy src/)
- Minimal runtime image
- Non-root user

### 3. CI/CD (GitHub Actions) 🔄

Automated pipeline:

```bash
cp references/ci-workflow.yml ../your-project/.github/workflows/ci.yml
```

Runs on push/PR:
- Lint (Ruff + MyPy)
- Test (pytest + coverage)
- Build (package + Docker)

## Quick Start

```bash
# Setup task runner
cp references/justfile ./

# Setup CI
mkdir -p .github/workflows
cp references/ci-workflow.yml .github/workflows/ci.yml

# Setup Docker
cp references/Dockerfile ./

# Test locally
just check
docker build -t test .
```

## MLflow Tracking

```python
import mlflow

mlflow.autolog()
with mlflow.start_run():
    mlflow.log_param("lr", 0.001)
    model.fit(X, y)
    mlflow.log_metric("accuracy", acc)
```

## Author

Converted from [MLOps Coding Course](https://github.com/MLOps-Courses/mlops-coding-skills)

## Changelog

### v1.0.0 (2026-02-18)
- Initial OpenClaw conversion
- Added justfile template
- Added Dockerfile
- Added CI workflow
