---
name: dependency-update-checker
description: CLI tool to check for outdated dependencies in package.json, requirements.txt, pyproject.toml, and other package files.
version: 1.0.0
author: skill-factory
metadata:
  openclaw:
    requires:
      bins:
        - python3
        - npm
        - pip
---

# Dependency Update Checker

## What This Does

A CLI tool that checks for outdated dependencies by running native package manager commands. Currently supports:
- **npm**: Checks `package.json` dependencies using `npm outdated`
- **pip**: Checks `requirements.txt` using `pip list --outdated`
- **poetry**: Checks `pyproject.toml` using `poetry show --outdated` (if poetry is installed)

The tool detects which package managers are relevant based on files in the current directory and runs the appropriate checks.

## When To Use

- You want a quick overview of outdated dependencies across multiple projects
- You need to check dependency status before updating or deploying
- You're managing multiple projects with different package managers
- You want a consistent interface for checking updates across ecosystems

## Usage

Check dependencies in current directory:
```bash
python3 scripts/main.py check
```

Check specific package manager:
```bash
python3 scripts/main.py check --manager npm
python3 scripts/main.py check --manager pip
python3 scripts/main.py check --manager poetry
```

Output format (JSON):
```bash
python3 scripts/main.py check --format json
```

## Examples

### Example 1: Check all dependencies

```bash
cd /path/to/project
python3 scripts/main.py check
```

Output:
```
Checking dependencies...
[✓] Found package.json
[✓] Running npm outdated...
┌─────────────────┬─────────┬─────────┬─────────┬──────────────┐
│ Package         │ Current │ Wanted  │ Latest │ Package Type │
├─────────────────┼─────────┼─────────┼─────────┼──────────────┤
│ express         │ 4.17.1  │ 4.18.0  │ 4.18.0  │ dependencies │
│ lodash          │ 4.17.20 │ 4.17.21 │ 4.17.21 │ dependencies │
└─────────────────┴─────────┴─────────┴─────────┴──────────────┘

[✓] Found requirements.txt
[✓] Running pip list --outdated...
┌─────────────────┬─────────┬─────────┐
│ Package         │ Current │ Latest  │
├─────────────────┼─────────┼─────────┤
│ requests        │ 2.28.1  │ 2.31.0  │
│ flask           │ 2.2.3   │ 2.3.0   │
└─────────────────┴─────────┴─────────┘
```

### Example 2: JSON output

```bash
python3 scripts/main.py check --format json
```

Output:
```json
{
  "npm": [
    {
      "package": "express",
      "current": "4.17.1",
      "wanted": "4.18.0",
      "latest": "4.18.0",
      "type": "dependencies"
    }
  ],
  "pip": [
    {
      "package": "requests",
      "current": "2.28.1",
      "latest": "2.31.0"
    }
  ]
}
```

## Requirements

- Python 3.x
- **npm**: Required for checking Node.js dependencies
- **pip**: Required for checking Python dependencies
- **poetry**: Optional, for checking Poetry projects

## Limitations

- This is a CLI tool, not an auto-integration plugin
- Requires package managers to be installed and available in PATH
- Some package managers may not support JSON output (fallback to text parsing)
- Only checks direct dependencies, not transitive dependencies
- Does not automatically update dependencies (check-only tool)
- May have issues with private registries or custom package sources
- Performance depends on network speed for checking remote registries