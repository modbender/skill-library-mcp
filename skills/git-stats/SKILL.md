---
description: Analyze git repository statistics — contributor rankings, commit frequency, file churn, and activity patterns.
---

# Git Stats

Analyze git repository statistics and generate visual reports.

**Use when** reviewing project activity, contributor rankings, or identifying hotspots.

## Requirements

- Git repository
- No API keys needed

## Instructions

1. **Verify repo**: `git rev-parse --is-inside-work-tree` — exit early if not a git repo.

2. **Run analysis commands**:

   ```bash
   # Project overview
   echo "First commit: $(git log --reverse --format='%ai' | head -1)"
   echo "Latest commit: $(git log -1 --format='%ai')"
   echo "Total commits: $(git rev-list --count HEAD)"
   echo "Contributors: $(git shortlog -sn --all | wc -l)"
   echo "Branches: $(git branch -a | wc -l)"
   echo "Tags: $(git tag | wc -l)"

   # Top contributors
   git shortlog -sn --all | head -15

   # Commits per day
   git log --format='%ai' | cut -d' ' -f1 | sort | uniq -c | sort -rn | head -20

   # Commits by day of week
   git log --format='%ad' --date=format:'%A' | sort | uniq -c | sort -rn

   # Commits by hour
   git log --format='%ad' --date=format:'%H' | sort | uniq -c | sort -n

   # Most changed files (hotspots)
   git log --pretty=format: --name-only | sort | uniq -c | sort -rn | head -20

   # Lines added/removed per contributor
   git log --format='%aN' --numstat | awk '...'  # complex awk parsing
   ```

3. **Output format**:
   ```
   ## 📊 Git Repository Stats
   **Repo:** <name> | **Period:** <first> → <last> | **Age:** X months

   ### 👥 Top Contributors
   | # | Author | Commits | % |
   |---|--------|---------|---|
   | 1 | Alice  | 342     | 45% |
   | 2 | Bob    | 210     | 28% |

   ### 📅 Activity Patterns
   - Busiest day: Wednesday (avg 4.2 commits)
   - Busiest hour: 14:00-15:00
   - Longest streak: 23 consecutive days

   ### 🔥 Hotspot Files (most changed)
   | File | Changes | Last Modified |
   |------|---------|--------------|
   | src/main.ts | 89 | 2025-01-10 |

   ### 📈 Monthly Trend
   | Month | Commits |
   |-------|---------|
   | 2025-01 | ████████ 42 |
   | 2024-12 | ██████ 31 |
   ```

4. **Custom date range**: Support `--since` and `--until` flags for filtered analysis.

## Edge Cases

- **Empty repo**: Report "No commits found."
- **Single contributor**: Skip ranking, focus on activity patterns.
- **Very large repos** (>100k commits): Use `--since="1 year ago"` by default and note the filter.
- **Detached HEAD**: Use `--all` flag to include all branches.

## Troubleshooting

- **Duplicate authors** (same person, different emails): Suggest `.mailmap` file for deduplication.
- **Slow on large repos**: Add `--no-merges` and limit date range.
