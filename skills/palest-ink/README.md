# Palest Ink - Activity Recording Skill

Record and track your daily activities (git operations, web browsing, commands, notes) with automatic storage, daily reports, and powerful search capabilities.

## Quick Start

1. The skill automatically creates `~/.palest-ink/` on first use
2. Add the scripts to your PATH (optional):

```bash
export PATH="$PATH:~/.openclaw/workspace/skills/public/palest-ink/scripts"
```

## Basic Usage

### Record Activities

```bash
# Git operations
palest-ink record git --message "Fix bug" --repo my-app --tags bugfix

# Web pages
palest-ink record web --url "https://example.com" --title "Docs" --tags docs

# Tasks/Commands
palest-ink record task --command "npm test" --desc "Run tests" --tags testing

# Notes
palest-ink record note --content "Meeting notes" --tags meeting
```

### Query Records

```bash
# Find git commits about plugins
palest-ink query --type git --keywords plugin

# Find web pages about documentation
palest-ink query --type web --tags docs

# Today's activities
palest-ink query --today

# Last 7 days
palest-ink query --days 7
```

### Generate Reports

```bash
# Today's report
palest-ink report --day today

# Weekly summary
palest-ink report --week

# Save to file
palest-ink report --day today --output ~/daily_report.md
```

## Data Location

All data is stored locally in `~/.palest-ink/`:
- `records.json` - All activity records
- `daily_reports/` - Generated reports
- `config.json` - Configuration (create from config.example.json)

## Features

- **Multiple activity types**: git, web, task, note
- **Flexible tagging**: Organize with custom tags
- **Powerful search**: By type, tags, keywords, date range
- **Daily/weekly reports**: Markdown-formatted summaries
- **Local storage**: All data stays on your machine
- **No external dependencies**: Uses only Python 3 and Bash

## Examples

### Track plugin development work
```bash
# Record commits
palest-ink record git --message "Add plugin system" --repo my-app --tags plugin,feature
palest-ink record git --message "Fix plugin loading" --repo my-app --tags plugin,bugfix

# Query all plugin work
palest-ink query --type git --keywords plugin
```

### Find documentation you visited
```bash
# Record visits
palest-ink record web --url "https://docs.example.com" --title "API Docs" --tags docs

# Later, find all docs
palest-ink query --type web --tags docs
```

### Generate end-of-day report
```bash
# Throughout the day, record activities
# ... various palest-ink record commands ...

# Generate and save report
palest-ink report --day today --output ~/daily_report.md
```
