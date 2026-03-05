---
name: secret-detection
description: Git hook to detect secrets before commit.
version: 1.0.0
author: skill-factory
metadata:
  openclaw:
    requires:
      env: []
      bins: ["git", "python3"]
---

# Secret Detection

## What This Does

This skill provides a git pre‑commit hook that scans staged files for common secret patterns (API keys, passwords, tokens) and blocks the commit if any are found. It helps prevent accidental leakage of secrets to public repositories.

Inputs: Git staged files (automatically scanned by the hook) or manual file paths.  
Outputs: Detection report with line numbers; non‑zero exit code if secrets found.

## When To Use

Use this skill when:
- You work with repositories that may contain sensitive credentials
- You want to prevent accidental commits of secrets
- You need a lightweight, local secret scanner for git workflows
- You want to enforce security checks before pushing to remote

## Usage

### Installation
```bash
# Install the hook in your git repository
./scripts/main.py install
```

### Manual Scan
```bash
# Scan specific files
./scripts/main.py scan --file path/to/file

# Scan all staged files (like the hook does)
./scripts/main.py scan --staged
```

### Hook Behavior
- The hook runs automatically on `git commit`
- If secrets are detected, the commit is blocked
- The script prints the detected secrets with file names and line numbers
- Exit code 0 = no secrets found; exit code 1 = secrets found

## Examples

### Example 1: Installing the Hook
```bash
$ ./scripts/main.py install
✓ Pre-commit hook installed at .git/hooks/pre-commit
✓ Hook will scan for secrets on every commit
```

### Example 2: Secret Detection Blocking a Commit
```bash
$ git commit -m "Add config"
⚠️  Secret detected in config.yaml line 12: AWS_ACCESS_KEY_ID=AKIA...
⚠️  Secret detected in .env line 3: PASSWORD=secret123
✗ Commit blocked: 2 secrets found
```

### Example 3: Manual Scan
```bash
$ ./scripts/main.py scan --staged
Scanning 3 staged files...
✓ config.yaml: clean
✓ .env: clean  
✓ src/main.py: clean
✓ No secrets found
```

## Requirements

- Git (for hook installation)
- Python 3.6+ (for the scanner)
- No external API keys or services needed

## Limitations

- Only detects common secret patterns (AWS keys, GitHub tokens, passwords, etc.)
- May produce false positives (e.g., long random strings that aren't actually secrets)
- Does not scan binary files
- Requires manual installation per repository
- Does not replace comprehensive secret‑management solutions
- Prints first 20 characters of detected secrets to console for identification purposes
