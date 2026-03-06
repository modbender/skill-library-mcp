---
name: Skill Deps Doctor
description: "Cross-platform skill dependency doctor — preflight check for missing binaries, version mismatches, system libraries, CJK fonts, Playwright/Chromium runtime, and project-level deps. Use before running skills to prevent late runtime dependency failures."
metadata: {"clawdbot": {"emoji": "🧰", "requires": {"bins": ["python3", "skill-deps-doctor"]}, "install": [{"id": "skill-deps-doctor", "kind": "pip", "package": "skill-deps-doctor", "bins": ["skill-deps-doctor"], "label": "Install skill-deps-doctor (package: skill-deps-doctor) from PyPI"}]}}
---

# 🧰 Skill Deps Doctor

> **Complementary to `openclaw doctor`** — `doctor` checks gateway/config/services;
> this skill checks **skill runtime dependencies** (bins, versions, libs, fonts).

Use this skill to **detect missing or broken dependencies before a skill fails at runtime**.

## What it checks

- 🔎 **Binary presence** — scans `skills/*/SKILL.md` declared `requires.bins` against `$PATH`
- 📌 **Version constraints** — `node>=18`, `python3>=3.10` syntax with actual version probing
- 🧩 **Shared libraries** — Playwright/Chromium native deps via `ldconfig` (Linux)
- 🔤 **CJK fonts** — prevents PDF tofu (□) via `fc-list`
- 🔗 **Transitive native deps** — e.g. `playwright` → 13 `.so` libraries
- 📦 **Project presets** via `--check-dir`:
  - Node (`package.json`), Python (`pyproject.toml` / `requirements.txt`), Docker (`Dockerfile`)
  - Cross-references npm/pip packages against system-dep hints
- 🎚️ **Playwright probes** — Node + Python detection + Chromium headless launch smoke test
- 📦 **Dependency profiles** — `--profile slidev`, `--profile whisper`, `--profile pdf-export`
- 🔌 **Plugin system** — third-party checkers via Python entry points

## Install

```bash
pip install skill-deps-doctor
```

Legacy command `skill-deps-doctor` remains supported for compatibility.

## Usage

### Basic check

```bash
skill-deps-doctor --skills-dir /path/to/workspace/skills
```

### Scan a project directory (with probes)

```bash
skill-deps-doctor --skills-dir ./skills --check-dir ./project --probe
```

### Monorepo recursive scan

```bash
skill-deps-doctor --skills-dir ./skills --check-dir ./monorepo --recursive
```

### Dependency profiles

```bash
skill-deps-doctor --skills-dir ./skills --profile slidev --profile pdf-export
skill-deps-doctor --skills-dir ./skills --list-profiles
```

### Generate fix script

```bash
skill-deps-doctor --skills-dir ./skills --fix > fix.sh
```

### Dependency graph

```bash
skill-deps-doctor --skills-dir ./skills --graph tree
skill-deps-doctor --skills-dir ./skills --graph dot | dot -Tsvg -o deps.svg
```

### Cross-platform fix matrix

```bash
skill-deps-doctor --skills-dir ./skills --platform-matrix
```

### JSON output (CI)

```bash
skill-deps-doctor --skills-dir ./skills --json
```

### Environment snapshot + baseline regression gating

```bash
# Save baseline
skill-deps-doctor --skills-dir ./skills --snapshot baseline.json

# Gate on new issues
skill-deps-doctor --skills-dir ./skills --baseline baseline.json --fail-on-new
# Exit: 0 = pass, 2 = errors, 3 = new findings vs baseline
```

### Validate hints schema & plugin contracts

```bash
skill-deps-doctor --skills-dir ./skills --validate-hints
skill-deps-doctor --skills-dir ./skills --validate-plugins
```

### Custom hints override

```bash
skill-deps-doctor --skills-dir ./skills --hints-file my-hints.yaml
```

### Verbosity

```bash
skill-deps-doctor --skills-dir ./skills -v        # Show all (including info)
skill-deps-doctor --skills-dir ./skills -q        # Errors only
skill-deps-doctor --skills-dir ./skills --no-plugins  # Skip third-party plugins
```

### Fallback wrapper (repo/dev layout)

```bash
python {baseDir}/scripts/skill-deps-doctor.py --skills-dir ./skills
```

## Notes

- **Linux**: shared-lib checks via `ldconfig`; font checks via `fc-list`; auto-adapts `apt` hints to host package manager (dnf / yum / apk / pacman).
- **macOS / Windows**: binary + version + font checks work; Playwright checks rely on probes (`--probe`).
- **CI integration**: use `--json` for machine-readable output, `--snapshot` + `--baseline --fail-on-new` for regression gating.
