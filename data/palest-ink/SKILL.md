---
name: palest-ink
description: "Record and query user activities (git operations, web browsing,
  commands, etc.) with automatic storage, daily report generation, and flexible
  search capabilities. Use when: (1) recording daily activities for later
  reference, (2) generating daily/weekly activity reports, (3) searching
  historical records by type, keywords, or tags, (4) tracking what work was done
  on specific topics (plugins, features, etc.), (5) understanding productivity
  patterns or reviewing past work."
---


# Palest Ink

## Overview

Palest Ink automatically records and indexes user activities, making it easy to review daily work, search for specific operations, and generate activity reports. Think of it as an intelligent activity journal that helps you track what you've done, when you did it, and what was accomplished.

## Quick Start

Palest Ink stores all data in `~/.palest-ink/` with the following structure:

```
~/.palest-ink/
├── records.json          # All activity records
├── daily_reports/        # Generated daily reports
└── config.json           # Configuration (tags, categories, etc.)
```

### First Time Setup

1. Initialize storage directory (automatic on first record)
2. Record activities using the CLI
3. Generate reports or query records as needed

## Core Capabilities

### 1. Recording Activities

Record different types of activities:

**Git Operations**
```bash
# Record a git commit
palest-ink record git --message "Fix authentication bug" --repo my-app --commit abc123 --tags bugfix,auth

# Record a merge or PR work
palest-ink record git --message "Merge feature/user-profile" --repo my-app --pr 156 --tags feature,merge
```

**Web Browsing**
```bash
# Record visiting a webpage
palest-ink record web --url "https://example.com/docs/api" --title "API Documentation" --tags docs,reference
```

**Command/Task**
```bash
# Record a command or task
palest-ink record task --command "npm install package-name" --desc "Install dependencies" --tags setup
```

**Custom Notes**
```bash
# Free-form note
palest-ink record note --content "Discussed project timeline with team" --tags meeting
```

### 2. Querying Records

Search through your activity history:

**By Type**
```bash
# Find all git operations
palest-ink query --type git

# Find all web pages visited
palest-ink query --type web
```

**By Keywords**
```bash
# Search for records containing "plugin"
palest-ink query --keywords "plugin"

# Search multiple keywords
palest-ink query --keywords "plugin,authentication"
```

**By Date Range**
```bash
# Today's activities
palest-ink query --today

# Last 7 days
palest-ink query --days 7

# Specific date range
palest-ink query --from 2026-03-01 --to 2026-03-03
```

**By Tags**
```bash
# Records tagged "bugfix"
palest-ink query --tags bugfix

# Multiple tags (OR logic)
palest-ink query --tags "bugfix,feature"

# Require multiple tags (AND logic)
palest-ink query --tags "bugfix" --tags "plugin"
```

**Combined Search**
```bash
# Git commits mentioning "plugin" in last 7 days
palest-ink query --type git --keywords "plugin" --days 7

# Web pages about documentation from yesterday
palest-ink query --type web --tags docs --days 1
```

### 3. Generating Reports

Generate daily or periodic reports:

**Daily Report**
```bash
# Generate report for today
palest-ink report --day today

# Generate report for specific date
palest-ink report --day 2026-03-03

# Save report to file
palest-ink report --day today --output ~/Desktop/report.md
```

**Weekly Summary**
```bash
# Last 7 days summary
palest-ink report --week

# Custom range summary
palest-ink report --from 2026-03-01 --to 2026-03-07 --output weekly.md
```

**Report Sections**
Reports include:
- Git operations (commits, merges, PRs)
- Web pages visited
- Commands/tasks executed
- Notes captured
- Tag-based groupings
- Time distribution by category

## Usage Examples

**Example 1: Track plugin development**
```bash
# Record git work
palest-ink record git --message "Add plugin system" --repo my-app --tags plugin,feature
palest-ink record git --message "Fix plugin loading bug" --repo my-app --tags plugin,bugfix

# Query all plugin-related work
palest-ink query --keywords plugin --type git
```

**Example 2: Find documentation you referenced**
```bash
# Record web visits
palest-ink record web --url "https://docs.example.com" --title "API Docs" --tags docs
palest-ink record web --url "https://github.com/example/repo" --title "Repo" --tags reference

# Later, find all documentation visits
palest-ink query --type web --tags docs
```

**Example 3: Generate daily work summary**
```bash
# Throughout the day, record activities
palest-ink record git --message "Refactor auth module" --repo my-app --tags refactoring
palest-ink record task --command "pytest tests/" --desc "Run tests" --tags testing

# End of day, generate report
palest-ink report --day today --output ~/daily_report.md
```

## Advanced Features

### Tag Management

Define frequently-used tags in `~/.palest-ink/config.json`:

```json
{
  "tags": {
    "categories": ["bugfix", "feature", "refactoring", "docs", "testing"],
    "projects": ["my-app", "other-project"],
    "custom": []
  }
}
```

### Automatic Capture

For frequent operations, consider shell aliases or git hooks:

**Git post-commit hook example**
```bash
#!/bin/bash
# .git/hooks/post-commit
COMMIT_MSG=$(git log -1 --pretty=%B)
palest-ink record git --message "$COMMIT_MSG" --repo $(basename $(git rev-parse --show-toplevel)) --commit $(git rev-parse HEAD)
```

**Browser bookmarklet (manual)**
```javascript
// Bookmarklet to record current page
javascript:(function(){window.open('palest-ink://record/web?url='+encodeURIComponent(location.href)+'&title='+encodeURIComponent(document.title))})();
```

## Best Practices

1. **Record immediately** - Capture activities as they happen, not retroactively
2. **Use descriptive tags** - Tags make searching much more effective
3. **Include context** - Add repo names, commit hashes, or full URLs
4. **Regular reports** - Generate weekly reports to track progress
5. **Review and prune** - Periodically clean up old or irrelevant records

## Troubleshooting

**Storage location not found?**
- First record automatically creates `~/.palest-ink/`
- Manually create: `mkdir -p ~/.palest-ink/daily_reports`

**Query returns no results?**
- Check date range with `--days` or specific dates
- Try broader keywords
- Use `--list-tags` to see all available tags

**Report generation fails?**
- Ensure `records.json` exists and is valid JSON
- Check output directory permissions
- Try with `--day today` for simplicity

## Resources

### scripts/

- **`palest-ink`** - Main CLI entry point (shell script)
  - Handles record, query, report subcommands
  - Manages JSON storage
  - Formats output

- **`record.py`** - Recording backend (Python)
  - Validates record formats
  - Updates `records.json`
  - Handles timestamps and IDs

- **`query.py`** - Search backend (Python)
  - Implements search logic
  - Supports filters (type, tags, date, keywords)
  - Returns structured results

- **`report.py`** - Report generator (Python)
  - Generates markdown reports
  - Groups by category and time
  - Calculates statistics
