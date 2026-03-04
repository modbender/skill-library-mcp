---
name: mlops-validation-cn
version: 1.0.0
description: Rigorous validation with typing, linting, testing, and security
license: MIT
---

# MLOps Validation ✅

Automated quality and security checks.

## Features

### 1. Pre-commit Hooks 🔧

Setup automated checks:

```bash
cp references/pre-commit-config.yaml ../your-project/.pre-commit-config.yaml
cd ../your-project
pre-commit install
```

Runs on every commit:
- Ruff (linting + formatting)
- MyPy (type checking)
- Bandit (security)

### 2. Test Fixtures 🧪

Shared pytest setup:

```bash
cp references/conftest.py ../your-project/tests/
```

Provides fixtures:
- `sample_df` - Test dataframe
- `temp_dir` - Temporary directory
- `sample_config` - Config dict
- `train_test_split` - Pre-split data

## Quick Start

```bash
# Copy pre-commit config
cp references/pre-commit-config.yaml ./.pre-commit-config.yaml

# Install hooks
pre-commit install

# Run manually
pre-commit run --all-files

# Setup test fixtures
cp references/conftest.py tests/

# Run tests
pytest tests/ -v --cov=src
```

## Commands

```bash
# Type check
mypy src/

# Lint
ruff check src/ tests/

# Format
ruff format src/ tests/

# Test
pytest tests/ --cov=src

# Security scan
bandit -r src/
```

## Author

Converted from [MLOps Coding Course](https://github.com/MLOps-Courses/mlops-coding-skills)

## Changelog

### v1.0.0 (2026-02-18)
- Initial OpenClaw conversion
- Added pre-commit config
- Added test fixtures
