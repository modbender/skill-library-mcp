# Repo Analyzer

Zero-dependency GitHub trust scorer that runs 29 analysis modules across 14 scoring categories to produce a single grade (A–F) for any public repository.

## Install

```bash
clawhub install repo-analyzer
```

## Setup

Requires a GitHub token for full accuracy (without one, you're limited to 60 requests/hour and scores are degraded):

```bash
export GITHUB_TOKEN="ghp_..."
```

Alternatively, if `gh` CLI is authenticated (`gh auth status`), the tool picks up that token automatically.

## Usage

```bash
node scripts/analyze.js <owner/repo>
node scripts/analyze.js https://github.com/owner/repo
node scripts/analyze.js <x.com-url>          # auto-extracts GitHub links from tweets
node scripts/analyze.js --file repos.txt     # batch mode, one repo per line
```

### Output Formats

| Flag | Description |
|------|-------------|
| *(default)* | Rich terminal report with bar charts and verdict |
| `--json` | Full structured JSON for pipelines |
| `--oneline` | Compact: `RepoName: 85/100 [A] — 2 flags` |
| `--badge` | Shields.io markdown badge |

Add `--verbose` for progress output.

## Scoring Categories (14 categories, 168 pts → normalized to 100)

| Category | Max Pts |
|----------|---------|
| Code Quality | 25 |
| Commit Health | 20 |
| Contributors | 15 |
| AI Authenticity | 15 |
| Agent Safety | 15 |
| Social | 10 |
| Activity | 10 |
| Dependency Audit | 10 |
| README Quality | 10 |
| Maintainability | 10 |
| Project Health | 10 |
| Fork Quality | 8 |
| Crypto Safety | 5 |
| Originality | 5 |

## Grade Scale

| Grade | Range | Verdict |
|-------|-------|---------|
| A | 85+ | LEGIT |
| B | 70–84 | SOLID |
| C | 55–69 | MIXED |
| D | 40–54 | SKETCHY |
| F | <40 | AVOID |

## Batch Mode

Create a text file with one `owner/repo` per line (`#` for comments), then:

```bash
node scripts/analyze.js --file repos.txt --json
```

## Full Documentation

See [SKILL.md](SKILL.md) for complete details on scoring logic, flags, and agent integration.
