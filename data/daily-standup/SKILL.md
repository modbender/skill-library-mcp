---
name: daily-standup
description: Generate daily standup reports from Git activity, TODOs, and project status.
---


# Daily Standup

Auto-generate standup reports from Git activity and project context.

## Instructions

1. **Gather Git activity**:
   ```bash
   # Yesterday's commits
   git log --since="yesterday 00:00" --until="today 00:00" --oneline --all --author="$(git config user.name)"

   # Today's commits
   git log --since="today 00:00" --oneline --all --author="$(git config user.name)"

   # Stats (24h)
   git log --since="24 hours ago" --shortstat --author="$(git config user.name)"

   # Files changed
   git log --since="24 hours ago" --name-only --pretty=format:"" | sort -u | grep .
   ```

2. **Check project context**: TODO files, open branches, stale PRs

3. **Generate report**:
   ```
   ## 📋 Standup — 2025-02-08

   ### ✅ Done (Yesterday)
   - feat: Add user auth endpoint (abc1234)
   - fix: Resolve login timeout (#42)

   ### 🔨 In Progress
   - Working on payment integration (branch: feature/payments)
   - 3 files changed today

   ### 🚧 Blockers
   - Waiting on API key from vendor

   ### 📊 Stats (24h)
   - Commits: 5 | Files: 12 | +340/-89 lines
   ```

4. **Multi-repo standup**:
   ```bash
   for dir in ~/projects/*/; do
     [ -d "$dir/.git" ] || continue
     commits=$(git -C "$dir" log --since="24 hours ago" --oneline --author="$(git config user.name)" 2>/dev/null)
     [ -n "$commits" ] && echo "### $(basename $dir)" && echo "$commits"
   done
   ```

## Edge Cases

- **No commits**: Report "No activity" — don't error; ask about work done offline
- **Multiple authors**: Filter by `git config user.name`; flag if not set
- **Detached HEAD / bare repos**: Skip gracefully
- **Weekend standups**: Extend to "since Friday 00:00" on Mondays

## Requirements

- Git repository (any project)
- No API keys or dependencies
