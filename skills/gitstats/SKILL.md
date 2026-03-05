---
name: pywayne-bin-gitstats
description: Analyze and visualize Git commit time distribution. Use when users need to analyze Git repository commit patterns, generate commit statistics, visualize commit activity by time, hour, or weekday. Triggered by requests to analyze commits, show commit distribution, visualize Git activity, or generate commit time statistics.
---

# Pywayne Bin Gitstats

Analyze Git repository commit time distribution and generate visualizations.

## Quick Start

```bash
# Analyze current repository (default: current directory, current branch)
gitstats

# Specify custom output path
gitstats --save output.png

# Analyze with time filter
gitstats --since "2024-01-01"
```

## Usage Examples

### Basic Analysis

```bash
# Analyze current repository
gitstats

# Analyze specific repository path
gitstats /path/to/repo

# Show plot in popup window (no file saved)
gitstats -p
```

### Time Range Filtering

```bash
# Commits since specific date
gitstats --since "2024-01-01"

# Commits within date range
gitstats --since "2024-01-01" --until "2024-12-31"

# Relative time expressions
gitstats --since "1 year ago"
gitstats --since "90 days ago"
gitstats --until "30 days ago"
```

### Branch Selection

```bash
# Analyze specific branch
gitstats --branch main
gitstats --branch develop
gitstats --branch origin/main

# Analyze all branches
gitstats --all
```

### Timezone Configuration

```bash
# Use UTC timezone
gitstats --tz UTC

# Use specific timezone
gitstats --tz "America/New_York"
gitstats --tz "Europe/London"

# Default is Asia/Shanghai
gitstats --tz "Asia/Shanghai"
```

### Custom Output

```bash
# Custom output filename
gitstats --save my_stats.png

# Output to subdirectory
gitstats --save results/commit_analysis.png

# Absolute path
gitstats --save /tmp/git_stats.png
```

### Combined Examples

```bash
# All branches, last year, custom output
gitstats --since "1 year ago" --all --save yearly_stats.png

# Main branch, last 90 days, UTC timezone
gitstats --branch main --since "90 days ago" --tz UTC

# Develop branch, date range, show plot
gitstats --branch develop --since "2024-01-01" --until "2024-06-30" -p
```

## Command Reference

| Argument | Description |
|----------|-------------|
| `repo` | Git repository path. Default: current directory |
| `--since` | Start time (e.g., "2024-01-01", "1 year ago", "90 days ago") |
| `--until` | End time (same formats as --since) |
| `--tz` | Timezone. Default: "Asia/Shanghai". Examples: "UTC", "America/New_York" |
| `--branch` | Specific branch to analyze. Examples: "main", "develop", "origin/main" |
| `--all` | Analyze all branches (overrides --branch) |
| `--save` | Output image path. Default: "git_time_distribution.png" |
| `-p`, `--show-plot` | Show plot in popup window without saving file |

## Output Charts

Generates a 3×2 subplot layout visualization:

1. **Commits per Day** - Line chart showing daily commit counts
2. **Commits by Hour** - Bar chart for hours 0-23
3. **Commits by Weekday** - Bar chart for Mon-Sun
4. **Heatmap: Weekday × Hour** - Color-coded activity matrix

Chart title includes: repository name, branch, and timezone.

## Branch Selection Priority

1. If `--all` is specified, all branches are analyzed
2. If `--branch` is specified, only that branch is analyzed
3. If neither is specified, current HEAD branch is used

## Requirements

- Git must be installed
- Python dependencies: pandas, matplotlib (installed with pywayne)

## Notes

- Time range can use Git's flexible date formats (absolute dates, relative expressions)
- Output file is overwritten if it exists
- Large repositories with `--all` may take longer to process
- Commit times are parsed in UTC, then converted to specified timezone
