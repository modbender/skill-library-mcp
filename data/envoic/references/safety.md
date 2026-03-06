# envoic Safety Guide

## Required Safety Rules

1. Always scan before deleting.
2. Prefer `--dry-run` first.
3. Never auto-delete unless user explicitly asks.
4. Warn before deleting CAREFUL artifacts (`.tox/`, `.nox/`, `*.egg-info`).
5. Never delete lock files (`package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`) or project manifests (`pyproject.toml`, `package.json`).
6. If deleting a broken venv, provide recreation steps.

## Risk Tiers

- SAFE: `__pycache__/`, `.pytest_cache/`, `.mypy_cache/`, `.ruff_cache/`, `.next/`, `.turbo/`, `coverage/`, `htmlcov/`, `.parcel-cache/`
- USUALLY SAFE: `dist/`, `build/` (only when generated artifacts are expected)
- CAREFUL: `.tox/`, `.nox/`, `*.egg-info`
