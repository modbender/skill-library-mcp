---
name: git-changelog
description: Generate changelogs from git commits. Supports markdown, plain text, and JSON output with date ranges and tag-based filtering.
---

# Git Changelog

## When to use

Generate a human-readable changelog from git commit history. Works with any git repository.

## Setup

No dependencies required. Uses only git and bash.

## How to

### Basic changelog (last 30 days or since last tag)

```bash
bash scripts/changelog.sh --repo /path/to/repo
```

### Since a specific date

```bash
bash scripts/changelog.sh --repo /path/to/repo --since "2026-01-01"
```

### Date range

```bash
bash scripts/changelog.sh --repo /path/to/repo --since "2026-01-01" --until "2026-02-01"
```

### JSON output (for programmatic use)

```bash
bash scripts/changelog.sh --repo /path/to/repo --format json
```

### Plain text output

```bash
bash scripts/changelog.sh --repo /path/to/repo --format plain
```

## Output Formats

| Format | Description |
|--------|-------------|
| `markdown` | Default. Headers, commit hashes, authors, dates |
| `plain` | Simple bullet list |
| `json` | Array of commit objects with hash, subject, author, date, type |

## Options

| Flag | Description | Default |
|------|-------------|---------|
| `--repo <path>` | Repository path | Current directory |
| `--since <date>` | Start date | Last tag or 30 days ago |
| `--until <date>` | End date | Now |
| `--format <fmt>` | Output format | markdown |
| `--group` | Group by conventional commit type | Off (needs bash 4+) |

## Notes

- Automatically detects the last git tag and uses it as the start point
- Excludes merge commits for cleaner output
- Conventional commit types (feat/fix/docs/etc) are extracted for JSON output
- `--group` mode requires bash 4+ (macOS ships with 3.2; install via `brew install bash`)
