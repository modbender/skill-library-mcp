---
name: skill-doctor
displayName: Skill Doctor | OpenClaw Skill
description: Scans the skills folder for new, unused, or missing dependencies; fixes requirements.txt; and tests a skill in or out of sandbox.
version: 1.0.0
---

# Skill Doctor | OpenClaw Skill

Scans `workspace/skills` (or a given folder) to detect **missing** and **unused** Python dependencies, can **fix** `requirements.txt` (add missing, optionally remove unused), and can **test** a skill using the skill-tester in **sandbox** (default) or **no-sandbox** mode.

## Description

- **Scan:** For each skill, finds all Python files under the skill and its `scripts/` folder, extracts top-level imports, and compares them to `requirements.txt`. Reports:
  - **Missing:** Imported but not listed in requirements (suggests adding).
  - **Unused:** Listed in requirements but not imported (suggests removing).
- **Fix:** Adds missing packages to `requirements.txt` and/or removes unused ones (`--fix-unused`).
- **Test:** Runs the [skill-tester](workspace/skills/skill-tester) for the given skill. Use `--no-sandbox` to run tests with full environment (e.g. network); default runs in sandbox.

Stdlib modules and local modules (same skill’s `.py` files) are excluded from “missing”.

## Installation

```bash
clawhub install skill-doctor
```

Or clone into your skills directory:

```bash
git clone https://github.com/Org/skill-doctor.git workspace/skills/skill-doctor
```

## Usage

```bash
# Scan all skills (or default: scan)
python3 workspace/skills/skill-doctor/scripts/skill_doctor.py

# Scan one skill
python3 workspace/skills/skill-doctor/scripts/skill_doctor.py --skill SUBAGENT-DASHBOARD --scan

# Fix: add missing deps to requirements.txt
python3 workspace/skills/skill-doctor/scripts/skill_doctor.py --skill MY-SKILL --fix

# Fix: add missing and remove unused
python3 workspace/skills/skill-doctor/scripts/skill_doctor.py --skill MY-SKILL --fix --fix-unused

# Dry-run fix (report only)
python3 workspace/skills/skill-doctor/scripts/skill_doctor.py --skill MY-SKILL --fix --fix-unused --dry-run

# Test skill (sandbox)
python3 workspace/skills/skill-doctor/scripts/skill_doctor.py --skill gateway-guard --test

# Test skill (no sandbox: full env)
python3 workspace/skills/skill-doctor/scripts/skill_doctor.py --skill gateway-guard --test --no-sandbox

# JSON output
python3 workspace/skills/skill-doctor/scripts/skill_doctor.py --scan --json
python3 workspace/skills/skill-doctor/scripts/skill_doctor.py --skill X --test --json
```

## Commands

| Command / flags | Description |
|-----------------|-------------|
| `--scan` | Scan skills and report missing/unused dependencies (default if no `--fix`/`--test`) |
| `--skill SLUG` | Limit to one skill |
| `--fix` | Add missing packages to `requirements.txt` |
| `--fix-unused` | With `--fix`, also remove unused packages |
| `--dry-run` | With `--fix`: only report what would be done |
| `--test` | Run skill-tester for the skill |
| `--no-sandbox` | Run tests with full env (no sandbox) |
| `--timeout N` | Test timeout in seconds (default 60) |
| `--json` | Output JSON |
| `--skills-dir PATH` | Override skills root (default: `workspace/skills`) |

## What this skill does

1. **Discover skills** — Finds dirs with `SKILL.md` or `_meta.json` under the skills folder.
2. **Parse Python** — Uses `ast` to collect top-level `import` / `import from` names from all `.py` files in the skill and `scripts/`.
3. **Exclude stdlib and local** — Ignores standard library modules and local modules (same skill’s file names).
4. **Map to pip** — Maps import names to pip package names (e.g. `bs4` → `beautifulsoup4`, `yaml` → `PyYAML`).
5. **Compare** — Compares required (from `requirements.txt`) vs needed (from imports); reports missing and unused.
6. **Fix** — Writes `requirements.txt`: append missing packages; optionally remove unused lines.
7. **Test** — Invokes `skill-tester/scripts/skill_tester.py --skill SLUG --json`. Sandbox vs no-sandbox is controlled by `--no-sandbox` and the `OPENCLAW_DOCTOR_NO_SANDBOX` env var for the test run.

## Requirements

- Python 3.7+
- Optional: [skill-tester](workspace/skills/skill-tester) for `--test` (must be present under `workspace/skills/skill-tester`).

## Security & privacy

- **Reads:** Skill directories and their `.py` and `requirements.txt` files.
- **Writes:** Only `requirements.txt` when using `--fix` (and `--fix-unused`).
- **Test:** Runs skill-tester in a subprocess; `--no-sandbox` means tests run with the current environment (e.g. network allowed).
