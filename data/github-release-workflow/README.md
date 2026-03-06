# GitHub Release Workflow

<p align="center">
  <img src="https://img.shields.io/badge/version-1.0.0-blue" alt="Version">
  <img src="https://img.shields.io/badge/python-3.10+-green" alt="Python">
  <img src="https://img.shields.io/badge/license-MIT-orange" alt="License">
</p>

> A standardized workflow for professional GitHub releases.

## Overview

This project provides a complete specification and CLI tool for professional GitHub releases, following industry best practices:

- **Conventional Commits** — Clear commit message format
- **Semantic Versioning** — Standard version numbers
- **Keep a Changelog** — Structured changelog
- **GitHub Releases** — Tagged releases with notes

## Installation

```bash
git clone https://github.com/weapon3k/github-release-workflow.git
cd github-release-workflow
pip install -e .
```

## Quick Start

```bash
# Initialize git (first time)
gh-release init

# Create a release
gh-release release v1.0.0

# Check status
gh-release status

# View log
gh-release log -n 10
```

## Workflow

### 1. Prepare

```bash
# Ensure clean working tree
git status
pytest
black .
```

### 2. Update

- Update version in `pyproject.toml`
- Add entry to `CHANGELOG.md`

### 3. Release

```bash
git add .
git commit -m "release: v1.0.0"
git tag -a v1.0.0 -m "Version 1.0.0"
git push
git push origin v1.0.0
```

## Commit Format

```
<type>(<scope>): <description>

Types: feat, fix, docs, style, refactor, test, chore, release
```

## Version Format

```
MAJOR.MINOR.PATCH
```

- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes

## Files

- `SPEC.md` — Full specification
- `SKILL.md` — OpenClaw skill definition
- `release.py` — CLI tool

## See Also

- [Conventional Commits](https://www.conventionalcommits.org/)
- [Semantic Versioning](https://semver.org/)
- [Keep a Changelog](https://keepachangelog.com/)

---

**License**: MIT
