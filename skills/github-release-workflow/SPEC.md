# GitHub Release Workflow Specification

> A standardized workflow for professional GitHub releases.

## Overview

This specification defines a professional release workflow for Python projects, inspired by industry best practices.

## Prerequisites

- Git installed
- GitHub CLI (`gh`) authenticated
- Python 3.10+
- Git repository initialized

## Release Workflow

### 1. Pre-Release Checklist

```bash
# Ensure clean working tree
git status

# Update dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black lib/ tests/

# Type checking (optional)
mypy lib/
```

### 2. Update Version

Update version in:
- `pyproject.toml` → `version`
- `CHANGELOG.md` → Add new version header

```bash
# Example: bump to 2.1.0
# Edit pyproject.toml: version = "2.1.0"
```

### 3. Update Changelog

Add new section in `CHANGELOG.md`:

```markdown
## [2.1.0] - YYYY-MM-DD

### Added
- New feature 1
- New feature 2

### Changed
- Improvement 1

### Fixed
- Bug fix 1

### Removed
- Deprecated feature 1
```

### 4. Stage Changes

```bash
git add .
git status
```

### 5. Commit

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```bash
git commit -m "release: v2.1.0 - Added new features and improvements"
```

### 6. Create Tag

```bash
git tag -a v2.1.0 -m "Version 2.1.0: Release description"
```

### 7. Push

```bash
git push
git push origin v2.1.0
```

### 8. Create GitHub Release (Optional)

```bash
gh release create v2.1.0 \
  --title "Version 2.1.0" \
  --notes "Release notes from CHANGELOG.md"
```

## Branch Strategy

```
main (stable)
  ↑
develop (integration)
  ↑
feature/* (new features)
  ↑
hotfix/* (urgent fixes)
```

### Branch Types

| Branch | Purpose | Base | Merge To |
|--------|---------|------|----------|
| `main` | Stable releases | - | - |
| `develop` | Integration | main | main |
| `feature/*` | New features | develop | develop |
| `hotfix/*` | Urgent fixes | main | main, develop |
| `release/*` | Release prep | develop | main, develop |

## Versioning

Follow [Semantic Versioning](https://semver.org/):

```
MAJOR.MINOR.PATCH
  │    │    │
  │    │    └── Bug fixes
  │    └─────── New features (backward compatible)
  └─────────── Breaking changes
```

### Version Format

- **Release**: `v2.1.0` (annotated tag)
- **Pre-release**: `v2.1.0-alpha.1`, `v2.1.0-beta.1`
- **Build**: `v2.1.0+build.123`

## Commit Message Format

### Conventional Commits

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

### Types

| Type | Description |
|------|-------------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation |
| `style` | Formatting |
| `refactor` | Code restructuring |
| `test` | Tests |
| `chore` | Maintenance |
| `release` | Version release |

### Examples

```bash
git commit -m "feat(memory): add SQLite storage support"
git commit -m "fix(vitality): correct energy decay calculation"
git commit -m "docs: update README with examples"
git commit -m "release: v2.1.0"
```

## CI/CD Integration (Optional)

### GitHub Actions Example

```yaml
# .github/workflows/release.yml
name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.10'
      - run: pip install -e ".[dev]"
      - run: pytest
      - run: pip install build
      - run: python -m build
      - uses: softprops/action-gh-release@v1
        with:
          files: dist/*
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

## Quick Reference

```bash
# Full release flow
git checkout develop
git pull origin develop
# Make changes...
git add .
git commit -m "feat: new feature"
git checkout main
git merge develop
git tag -a v2.1.0 -m "Version 2.1.0"
git push origin main --follow-tags

# Hotfix flow
git checkout main
git checkout -b hotfix/fix-description
# Fix...
git commit -m "fix: description"
git checkout main
git merge hotfix/fix-description
git tag -a v2.1.1 -m "Version 2.1.1"
git push origin main --follow-tags
git branch -d hotfix/fix-description
```

## Related Standards

- [Conventional Commits](https://www.conventionalcommits.org/)
- [Semantic Versioning](https://semver.org/)
- [Keep a Changelog](https://keepachangelog.com/)
- [GitHub Flow](https://docs.github.com/en/get-started/quickstart/github-flow)

---

_Last updated: 2026-02-22_
