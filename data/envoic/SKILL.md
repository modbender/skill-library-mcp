---
name: envoic
description: >-
  Scan, audit, and clean up Python virtual environments (.venv, conda),
  node_modules, and development artifacts consuming disk space. Use when
  the user mentions disk space, environment cleanup, stale venvs,
  node_modules bloat, project cleanup, broken environments, dangling
  symlinks, or asks about disk usage from development tools. Also use
  when encountering ENOSPC errors, slow installs from cache bloat, or
  when onboarding into a project and needing to verify environment health.
license: BSD-3-Clause
compatibility: >-
  Requires uvx (from uv) or pip for Python scanning.
  Requires npx (from Node.js 18+) or npm for JavaScript scanning.
  Works on Linux, macOS, and Windows.
metadata:
  author: mahimailabs
  version: "0.0.1"
  repository: https://github.com/mahimailabs/envoic
---

# envoic - Environment Scanner and Cleanup Skill

Use envoic to discover and safely clean Python virtual environments, `node_modules`, and development artifacts.

## Quick Start

```bash
uvx envoic scan .
uvx envoic manage . --dry-run
npx envoic scan . --deep
```

If `uvx` is unavailable, install Python package with `pip install envoic`.
If `npx` is unavailable, install JS package with `npm install -g envoic`.

## Primary Workflows

### 1) Onboarding Health Check

1. Run `uvx envoic info .venv` (or `npx envoic info node_modules`).
2. If environment is broken or stale, propose delete-and-recreate steps.

### 2) Disk Space Recovery

1. Run `uvx envoic scan <root> --deep` and/or `npx envoic scan <root> --deep`.
2. Identify largest stale candidates.
3. Run `manage --dry-run`, then actual cleanup only after confirmation.

### 3) Build/Test Artifact Cleanup

1. Scan project root.
2. Prefer deleting SAFE artifacts first.
3. Warn for CAREFUL artifacts.

## Safety Contract

1. Always scan before delete.
2. Prefer `--dry-run` before destructive operations.
3. Never delete lock files or project manifest files.
4. Require explicit user confirmation for non-dry-run cleanup.

See full policy in `references/safety.md`.

## Verified Trigger Phrases

- "Find and remove stale virtualenvs"
- "Clean old node_modules and caches"
- "I hit ENOSPC, free up disk from dev artifacts"
- "Audit environment sprawl in this workspace"
- "Check if this .venv is broken"
- "List largest build artifacts"
- "Dry-run cleanup plan for Python and JS"
- "Find dangling venv symlinks"
- "Clean test/build caches safely"
- "Generate JSON report for stale environments"

## References

- Full command catalog: `references/commands.md`
- Safety and risk tiers: `references/safety.md`
- Troubleshooting and fallbacks: `references/troubleshooting.md`

## Tool-Specific Surface Files

- Codex: `.agents/skills/envoic/SKILL.md` (symlink/copy of this skill)
- Cursor: `.cursorrules` (generated adapter)
- Copilot: `.github/copilot-instructions.md` (generated adapter)
- Claude: `.claude-plugin/plugins.yaml` (generated adapter)
