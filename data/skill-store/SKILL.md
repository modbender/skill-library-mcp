---
name: skill-store
description: "Smart skill installation advisor for ClawHub. Searches for skills matching your needs, evaluates candidates on security (via skill-shield), code quality, and documentation, then produces a comparison report with a recommendation. Use when: looking for a skill to do something specific, comparing similar skills, or wanting a safety-checked recommendation before installing. Zero external dependencies."
---

# Skill Store — Smart Installation Advisor

Find the right skill without the guesswork. Searches ClawHub, evaluates candidates on security + quality, and recommends the best one.

## Usage

```bash
python3 scripts/evaluate.py "your search query" [options]
```

### Examples

```bash
# Find a weather skill
python3 scripts/evaluate.py "weather forecast"

# Evaluate top 3 only, save reports
python3 scripts/evaluate.py "image generation" --top 3 --output-dir ./reports

# Use a specific skills workspace for clawhub
python3 scripts/evaluate.py "security audit" --workdir /path/to/workspace
```

### Options

| Option | Default | Description |
|--------|---------|-------------|
| `--top N` | 5 | Number of candidates to evaluate |
| `--output-dir DIR` | (stdout) | Save report.md and report.json to DIR |
| `--workdir DIR` | /tmp/skill-store-eval-* | Working directory for clawhub install |
| `--scanner PATH` | auto-detect | Path to skill-shield's scan.py |
| `--keep-all` | false | Don't uninstall non-recommended candidates |

### Output

Prints a Markdown comparison report to stdout. With `--output-dir`, also writes:
- `report.md` — human-readable comparison
- `report.json` — structured evaluation data

## How It Works

1. Searches ClawHub for skills matching your query
2. Installs top N candidates into a temporary directory
3. Runs skill-shield security scan on each candidate
4. Evaluates code quality (lines of code, documentation, tests, structure)
5. Scores and ranks candidates (security 40%, quality 30%, relevance 30%)
6. Generates comparison report with recommendation
7. Uninstalls non-recommended candidates (unless `--keep-all`)

## Scoring

| Dimension | Weight | What's measured |
|-----------|--------|-----------------|
| Security | 40% | skill-shield rating, findings count, permission audit |
| Quality | 30% | Code lines, SKILL.md completeness, README, tests |
| Relevance | 30% | clawhub search score (normalized) |

## Requirements

- `clawhub` CLI installed and authenticated
- `skill-shield` scan.py accessible (auto-detected from sibling directory or via `--scanner`)
- Python 3.8+

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Recommendation made successfully |
| 1 | No candidates found or all evaluations failed |
