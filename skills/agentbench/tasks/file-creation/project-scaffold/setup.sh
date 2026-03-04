#!/usr/bin/env bash
set -euo pipefail

cd "$1"

git init
git config user.email "bench@agentbench.local"
git config user.name "AgentBench"

cat > requirements.md << 'REQUIREMENTS'
# FileSync — Python CLI Tool Requirements

## Overview

FileSync is a command-line utility for tracking, comparing, and synchronizing
file system state across directories. It produces JSON manifests of directory
contents and can diff and apply changes between snapshots.

**Constraints**: Python 3.9+, standard library only (argparse, pathlib, hashlib,
json, logging, os, shutil). No third-party packages.

**Entry point**: `python -m filesync`

---

## Subcommands

### 1. `scan`

Recursively scan a directory and produce a JSON manifest.

```
python -m filesync scan <directory> [-o OUTPUT]
```

- Walk the directory tree using `pathlib.Path.rglob`.
- For each file, record:
  - `path` (relative to the scanned directory)
  - `size` (bytes)
  - `hash` (hex digest using the configured algorithm, default SHA-256)
  - `mtime` (ISO 8601 timestamp)
- Output the manifest as a JSON object with keys:
  - `root`: absolute path of the scanned directory
  - `created_at`: ISO 8601 timestamp of when the scan was run
  - `algorithm`: hash algorithm used
  - `files`: list of file entry objects (sorted by path)
- If `-o` is given, write to that file; otherwise print to stdout.
- Respect ignore patterns from `.filesyncrc` (see Configuration below).

### 2. `diff`

Compare two manifests and produce a diff report.

```
python -m filesync diff <manifest-a> <manifest-b> [-o OUTPUT]
```

- Load both JSON manifests.
- Classify every file into one of:
  - `added` — present in B but not A
  - `removed` — present in A but not B
  - `modified` — present in both but hash differs
  - `unchanged` — present in both with identical hash
- Output a JSON diff report with keys:
  - `base`: root from manifest A
  - `target`: root from manifest B
  - `created_at`: timestamp
  - `summary`: object with counts `{ added, removed, modified, unchanged }`
  - `changes`: list of `{ path, status, size_before, size_after }` (omit unchanged files unless `--include-unchanged` flag is given)
- If `-o` is given, write to that file; otherwise print to stdout.

### 3. `apply`

Apply a diff report to a target directory.

```
python -m filesync apply <diff-report> <target-dir> [--delete] [--dry-run]
```

- Read the JSON diff report.
- For each `added` or `modified` entry, copy the file from the source
  directory (the `target` path in the diff report) to `<target-dir>`.
- `--delete`: also remove files listed as `removed` from `<target-dir>`.
- `--dry-run`: print what would be done without making changes. Each planned
  action should be logged at INFO level in the format:
  `[DRY RUN] Would copy <path>` or `[DRY RUN] Would delete <path>`.
- Exit with code 0 on success, 1 on any file operation error.

---

## Configuration — `.filesyncrc`

FileSync reads an optional `.filesyncrc` YAML-format configuration file from
the current working directory (fall back to `~/.filesyncrc`). Fields:

```yaml
output_format: json          # "json" (default) or "text"
hash_algorithm: sha256       # Any algorithm supported by hashlib (md5, sha1, sha256, sha512)
ignore_patterns:             # List of glob patterns to skip during scan
  - "*.pyc"
  - "__pycache__"
  - ".git"
  - ".filesyncrc"
```

The config module must:
- Provide a `load_config()` function returning a dataclass or dict with defaults.
- Merge file-based config with any CLI flag overrides (CLI wins).
- Gracefully handle missing config files (use defaults).

---

## Logging

Use Python's built-in `logging` module.

- Default level: WARNING.
- `--verbose` flag: set level to INFO.
- `--debug` flag: set level to DEBUG.
- Format: `%(asctime)s [%(levelname)s] %(name)s: %(message)s`
- The logger name should be `"filesync"`.

---

## Package Structure (required)

```
filesync/
    __init__.py          # Package version (__version__ = "0.1.0")
    __main__.py          # Entry point: parse args → dispatch subcommand
    cli.py               # argparse setup, subcommand routing
    scanner.py           # scan logic
    differ.py            # diff logic
    applier.py           # apply logic
    config.py            # .filesyncrc loading and defaults
    utils.py             # Shared helpers (hashing, timestamp formatting)
setup.py or pyproject.toml   # Package metadata and entry point
tests/
    test_scan.py
    test_diff.py
    test_apply.py
```

---

## Additional Notes

- All public functions must have docstrings.
- `__init__.py` must define `__version__ = "0.1.0"`.
- `python -m filesync --help` must display the three subcommands (scan, diff, apply).
- `python -m filesync scan --help` (and likewise for diff/apply) must show the
  subcommand-specific flags.
- Stub implementations are acceptable, but all imports must resolve and
  `--help` output must work end-to-end.
REQUIREMENTS

git add requirements.md
git commit -m "Initial commit: add FileSync requirements"
