---
name: chis-chisf
description: Standardized skill install workflow using short aliases (chis/chisf) with force + force-install + workspace-aware lookup.
---

# CHIS / CHISF

A lightweight skill to standardize how we install/manage OpenClaw skills.

## Core idea

- `chis <slug> [workdir] [version]` = install a skill from ClawHub.
- `chisf <slug> [workdir] [version]` = force-install when the package is flagged/requires overwrite.
- `clawhub inspect <slug>` = inspect before install (recommended for validation).
- Always run installs with explicit workdir and skills dir to avoid path confusion.

Default workdir in examples: `/Users/zququ/.openclaw/workspace`.

## Default command mapping

### 1) Standard install

```bash
clawhub install <slug> --workdir /Users/zququ/.openclaw/workspace --dir skills --version <version>
```

- Omit `--version` for latest.
- If no version argument, installs latest available.

### 2) Force install

```bash
clawhub install <slug> --force --workdir /Users/zququ/.openclaw/workspace --dir skills --version <version>
```

Use this when:
- package is flagged as suspicious
- overwrite behavior is required

### 3) Inspect before install (recommended)

```bash
clawhub inspect <slug>
```

### 4) Verify

```bash
clawhub list --workdir /Users/zququ/.openclaw/workspace --dir skills
```

## CHIS aliases

Use these shortcuts in practice:

- **`chis <slug>`** → same as standard install in default workspace.
- **`chisf <slug>`** → same as force install in default workspace.
- If needed, set your session path context and explicitly pass an alternate path:
  - `chis --workdir /alt/path <slug>`
  - `chisf --workdir /alt/path <slug>`

## Failure handling

1. If `Rate limit exceeded`: retry after a few minutes.
2. If command fails due to path mismatch: ensure you are checking with same `--workdir` and `--dir skills` used during install.
3. If package not found: confirm correct slug via `clawhub search <keyword>`.

## Safe defaults for this environment

- Use:
  - `--workdir /Users/zququ/.openclaw/workspace`
  - `--dir skills`

- Already-known working example:

```bash
clawhub install proactive-agent --force --workdir /Users/zququ/.openclaw/workspace --dir skills
```

## Notes

- `CHISF` is a human-facing label I use for force-install style operations.
- Keep all install actions explicit and repeatable; never rely on default working dir.
- **Failure handling**
  - If install fails, run `clawhub inspect <slug> --workdir /Users/zququ/.openclaw/workspace --dir skills` for a quick pre-check.
  - If it still fails due to environment mismatch, re-run with explicit `--workdir /Users/zququ/.openclaw/workspace` and `--dir skills` (never rely on implicit defaults).
- For suspected API/service issues (e.g., rate limit exceeded), prefer 10–20 minute pause and retry.
- If rate limit persists, use the local fallback installer: `/Users/zququ/.local/bin/clawhub-install-safe --force <slug> <workdir>` (or without `--force` when not needed) before switching to another approach.
- Keep the same `--workdir` and `--dir skills`/registry context when re-running.
