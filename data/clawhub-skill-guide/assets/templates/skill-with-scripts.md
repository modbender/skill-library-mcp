---
name: SKILL_NAME
description: >
  DESCRIPTION of what this skill does. Include specific trigger keywords
  and scenarios. Use when: scenario1, scenario2, scenario3.
metadata:
  openclaw:
    requires:
      env:
        - ENV_VAR_NAME
      bins: []
    primaryEnv: ENV_VAR_NAME
    env:
      - name: ENV_VAR_NAME
        description: "What this environment variable is for"
        required: true
      - name: OPTIONAL_CONFIG_VAR
        description: "Optional configuration value (default: some-default)"
        required: false
---

# Skill Title

Brief overview of what this skill provides.

## Prerequisites

| Requirement | Details |
|-------------|---------|
| `ENV_VAR_NAME` | Required. Obtain from Example service dashboard. |
| `OPTIONAL_CONFIG_VAR` | Optional. Defaults to `some-default` if not set. |

## Security Notes

The included scripts (`scripts/setup.sh`, `scripts/run.py`) only create files
within the skill workspace. They make no network calls and write no files
outside the skill directory. **Inspect them before running** — both are plain
code with no obfuscation.

## Bundled Scripts

| Script | Purpose | Lines |
|--------|---------|-------|
| `scripts/setup.sh` | Creates workspace directory structure | ~25 |
| `scripts/run.py` | Core processing logic | ~80 |

## Quick Start

1. Set required environment variable: `export ENV_VAR_NAME="your-value"`
2. Run setup: `bash scripts/setup.sh`
3. Execute: `python3 scripts/run.py`

## How It Works

Core instructions and workflows.

## File Reference

| File | Purpose |
|------|---------|
| `SKILL.md` | Core instructions (this file) |
| `scripts/setup.sh` | Workspace initialization |
| `scripts/run.py` | Core processing logic |
