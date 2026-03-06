# Secret Detection Skill

A git pre‑commit hook that scans staged files for common secret patterns (API keys, passwords, tokens) and blocks commits if secrets are found.

## Quick Start

1. **Install the hook** (in your git repository):
   ```bash
   ./scripts/main.py install
   ```

2. **Test the scanner**:
   ```bash
   ./scripts/main.py scan --staged
   ```

3. **The hook will run automatically** on every `git commit`.

## What It Detects

- AWS Access Key IDs (`AKIA...`)
- AWS Secret Access Keys
- Passwords, secrets, tokens in variable assignments
- GitHub Personal Access Tokens (`ghp_...`)
- GitHub Fine‑Grained Tokens (`github_pat_...`)
- OpenAI API Keys (`sk-...`)
- Bearer tokens

## Manual Usage

### Scan Specific Files
```bash
./scripts/main.py scan --file config.yaml --file .env
```

### Scan All Staged Files
```bash
./scripts/main.py scan --staged
```

## How It Works

1. The `install` command creates a `.git/hooks/pre‑commit` script that calls this scanner.
2. On `git commit`, the hook scans all staged files using regex patterns.
3. If any secret pattern is matched, the commit is blocked and the secrets are displayed.
4. Clean commits proceed normally.

## Limitations

- Only common secret patterns are detected (custom patterns can be added by editing `SECRET_PATTERNS` in `scripts/main.py`).
- May produce false positives (e.g., long random strings that aren't secrets).
- Does not scan binary files.
- Requires manual installation per repository.

## For Developers

The skill is written in Python 3 and uses no external dependencies beyond the standard library.

To extend the detection patterns, edit the `SECRET_PATTERNS` list in `scripts/main.py`.