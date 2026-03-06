# Tests – Feature Tracking

## Overview

**clawd_migrate** has Python unit tests for discover, backup, and migrate. They use a temporary directory with a fake moltbot/clawdbot layout and assert the expected files and layout.

## Status

- **Added:** 2025-02-01
- **Runner:** `unittest` (stdlib; no extra deps)

## What is tested

| Test | What it checks |
|------|----------------|
| `TestDiscover.test_discover_finds_memory_config_extra` | Discover returns memory (SOUL.md, USER.md, TOOLS.md), config, clawdbook, and extra (projects/) |
| `TestBackup.test_backup_creates_dir_and_copies_files` | Backup dir exists; SOUL.md, USER.md, credentials.json, projects/readme.txt, _manifest.txt present |
| `TestMigrate.test_migrate_creates_openclaw_layout` | Migration creates memory/, .config/openclaw/, .config/clawdbook/; copies memory and clawdbook; no errors; projects/ preserved |

## How to run

From repo root (the `clawd_migrate` directory):

```bash
# Via npm (sets PYTHONPATH to parent so package is found)
npm test

# Via Python (from parent of clawd_migrate so clawd_migrate is on path)
cd .. && PYTHONPATH=. python -m unittest discover -s clawd_migrate/tests -p "test_*.py" -v

# Or from repo root with PYTHONPATH to parent
PYTHONPATH=.. python -m unittest discover -s tests -p "test_*.py" -v
```

## Files

- `tests/__init__.py` – Marks tests package.
- `tests/test_migrate.py` – Discover, backup, migrate tests; adds parent of repo root to `sys.path` so `clawd_migrate` is importable.
- `scripts/run-tests.js` – Used by `npm test`; sets `PYTHONPATH` to parent dir and runs `python -m unittest discover`.

## Bug fix in migrate

In-place migration (output_root same as root) was copying "extra" files onto themselves, causing `shutil.copy2` to raise "same file". Migrate now skips copying when `src_path.resolve() == dest.resolve()`.
