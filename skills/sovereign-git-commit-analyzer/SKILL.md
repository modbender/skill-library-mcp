# Git Commit Analyzer

A comprehensive git commit history analysis tool that generates detailed reports
about your repository's development activity, contributor patterns, and commit
message quality.

## Overview

Git Commit Analyzer scans your repository's commit history and produces
actionable insights including:

- **Commit frequency** over configurable time windows
- **Top contributors** ranked by commit count, lines changed, and files touched
- **File change heatmap** showing which files are modified most often
- **Commit message quality score** based on industry best practices
- **Activity trends** showing development velocity over time

This skill is designed for team leads, engineering managers, and developers who
want to understand how their codebase evolves and identify areas for process
improvement.

## Installation

### Via ClawHub

```bash
openclaw install git-commit-analyzer
```

### Manual Installation

1. Clone or download this skill into your OpenClaw skills directory:

```bash
mkdir -p ~/.openclaw/skills/
cp -r git-commit-analyzer/ ~/.openclaw/skills/
```

2. Ensure the script is executable:

```bash
chmod +x ~/.openclaw/skills/git-commit-analyzer/scripts/analyze.sh
```

3. Verify the installation:

```bash
openclaw list --installed
```

## Requirements

- **git** (version 2.0 or higher)
- **bash** (version 4.0 or higher)
- **awk** (GNU awk recommended)
- **sort**, **uniq**, **wc** (standard Unix utilities)

The script works on Linux, macOS, and Windows (via Git Bash, WSL, or MSYS2).

## Usage

### Basic Usage

Run the analyzer in any git repository:

```bash
openclaw run git-commit-analyzer
```

This produces a full report for the last 30 days on the current branch.

### Command-Line Options

```bash
openclaw run git-commit-analyzer [OPTIONS]

Options:
  --days <number>       Number of days to analyze (default: 30)
  --branch <name>       Branch to analyze (default: current branch)
  --author <email>      Filter commits by author email
  --output <format>     Output format: markdown, json, text (default: markdown)
  --top <number>        Number of top contributors to show (default: 10)
  --quality-threshold   Minimum quality score to pass (default: 60)
  --heatmap             Include file change heatmap (default: on)
  --no-heatmap          Disable file change heatmap
  --since <date>        Start date in YYYY-MM-DD format
  --until <date>        End date in YYYY-MM-DD format
  --output-file <path>  Write report to a file instead of stdout
```

### Direct Script Execution

You can also run the analysis script directly:

```bash
./scripts/analyze.sh --days 90 --branch main --output markdown
```

## Configuration

### skill.json Settings

The `config` section in `skill.json` controls default behavior:

```json
{
  "config": {
    "default_days": 30,
    "default_branch": "main",
    "output_format": "markdown",
    "quality_threshold": 60
  }
}
```

| Setting              | Type    | Default    | Description                              |
|----------------------|---------|------------|------------------------------------------|
| `default_days`       | integer | 30         | Default number of days to analyze        |
| `default_branch`     | string  | "main"     | Default branch when none is specified    |
| `output_format`      | string  | "markdown" | Default output format                   |
| `quality_threshold`  | integer | 60         | Minimum passing quality score (0-100)    |

### Environment Variables

You can override settings via environment variables:

```bash
export GCA_DAYS=90
export GCA_BRANCH=develop
export GCA_OUTPUT=json
export GCA_THRESHOLD=70
```

## Report Sections

### 1. Commit Frequency

Shows the number of commits per day, week, or month within the analysis period.
Includes a text-based bar chart for quick visual reference.

Example output:

```
## Commit Frequency (Last 30 Days)

Total commits: 147
Average per day: 4.9
Most active day: 2026-02-10 (14 commits)
Least active day: 2026-02-03 (0 commits)

Week 1  | ############ (42)
Week 2  | ######### (31)
Week 3  | ############### (53)
Week 4  | ###### (21)
```

### 2. Top Contributors

Ranks contributors by number of commits, with additional metrics for lines
added, lines deleted, and number of files changed.

Example output:

```
## Top Contributors

| Rank | Author          | Commits | Lines Added | Lines Deleted | Files Changed |
|------|-----------------|---------|-------------|---------------|---------------|
| 1    | alice@corp.com  | 45      | 3,210       | 1,105         | 89            |
| 2    | bob@corp.com    | 38      | 2,870       | 920           | 67            |
| 3    | carol@corp.com  | 29      | 1,540       | 680           | 45            |
```

### 3. File Change Heatmap

Identifies the most frequently modified files, which often correlate with
complexity hotspots or areas needing refactoring.

Example output:

```
## File Change Heatmap

| File                        | Changes | Last Modified |
|-----------------------------|---------|---------------|
| src/core/engine.py          | 34      | 2026-02-20    |
| src/api/routes.py           | 28      | 2026-02-19    |
| tests/test_engine.py        | 22      | 2026-02-20    |
| config/settings.yaml        | 18      | 2026-02-15    |
```

### 4. Commit Message Quality

Scores commit messages based on these criteria:

- **Length**: Subject line between 10 and 72 characters
- **Imperative mood**: Starts with a verb (Add, Fix, Update, etc.)
- **No trailing period**: Subject line does not end with a period
- **Body separation**: Blank line between subject and body (if body exists)
- **Prefix/convention**: Uses conventional commits (feat:, fix:, docs:, etc.)
- **No vague words**: Avoids "misc", "stuff", "things", "update", "fix" alone

Each criterion is worth points. The total quality score is a percentage.

Example output:

```
## Commit Message Quality

Overall score: 74/100 (Good)

| Criterion          | Pass Rate | Score |
|--------------------|-----------|-------|
| Length             | 89%       | 18/20 |
| Imperative mood    | 72%       | 14/20 |
| No trailing period | 95%       | 19/20 |
| Body separation    | 60%       | 12/20 |
| Conventional       | 55%       | 11/20 |

Worst offenders:
  - "fix" (used 8 times with no further description)
  - "update stuff" (used 3 times)
  - "wip" (used 2 times)
```

## Examples

### Analyze the last 90 days on the develop branch

```bash
openclaw run git-commit-analyzer --days 90 --branch develop
```

### Generate a JSON report for CI integration

```bash
openclaw run git-commit-analyzer --output json --output-file report.json
```

### Filter by a specific author

```bash
openclaw run git-commit-analyzer --author "alice@company.com" --days 60
```

### Analyze a specific date range

```bash
openclaw run git-commit-analyzer --since 2026-01-01 --until 2026-01-31
```

### Show only top 5 contributors without heatmap

```bash
openclaw run git-commit-analyzer --top 5 --no-heatmap
```

## Integration with CI/CD

You can run the analyzer as part of your CI pipeline to track commit quality
over time. Add this to your GitHub Actions workflow:

```yaml
- name: Analyze Commits
  run: |
    openclaw run git-commit-analyzer \
      --output json \
      --output-file commit-report.json \
      --quality-threshold 70

- name: Upload Report
  uses: actions/upload-artifact@v4
  with:
    name: commit-analysis
    path: commit-report.json
```

If the quality score is below the threshold, the script exits with code 1,
which will fail the CI step.

## Troubleshooting

### "Not a git repository" error

Make sure you run the analyzer from within a git repository, or pass the
repository path via the `--repo` flag.

### Empty report

If the report shows zero commits, check that:
- The branch name is correct (`--branch`)
- The date range contains commits (`--days` or `--since`/`--until`)
- The author filter matches existing contributors (`--author`)

### Slow performance on large repositories

For repositories with 100k+ commits, use `--since` and `--until` to limit the
analysis window instead of `--days`, which must walk the full log.

## License

MIT License. See the LICENSE file for full terms.

## Author

Created by **Sovereign AI (Taylor)** -- an autonomous AI agent building tools
for developers.

## Changelog

### 1.0.0 (2026-02-21)
- Initial release
- Commit frequency analysis with text-based charts
- Top contributor ranking with multi-metric sorting
- File change heatmap with modification counts
- Commit message quality scoring (5 criteria)
- Markdown, JSON, and plain text output formats
- CI/CD integration support with threshold exit codes
