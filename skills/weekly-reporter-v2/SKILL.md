---
name: weekly-reporter-v2
description: Auto-generate professional weekly work reports with multiple templates
command-dispatch: tool
command-tool: weekly_reporter
command-arg-mode: raw
metadata: {"openclaw": {"emoji": "📋", "requires": {"bins": ["python3"]}}}
---

# 📋 Weekly Reporter - Auto Work Report Generator

Automatically generate weekly work reports with customizable templates. Perfect for professionals who want to save time on weekly summaries.

## Features

- **Multiple Templates**: Simple, Detailed, Tech formats
- **Data Summary**: Task completion, hours spent, progress tracking
- **Issue Tracking**: Document problems and suggestions
- **Week Selection**: This week or last week reports

## Commands

| Command | Description |
|---------|-------------|
| `this-week` | Generate this week's report |
| `last-week` | Generate last week's report |
| `--template <type>` | Choose template: simple/detailed/tech |

## Template Types

### Simple Template
- Quick overview with key metrics
- Best for quick daily updates

### Detailed Template  
- Full table format with all tasks
- Best for formal reporting

### Tech Template
- Developer-focused with code metrics
- Best for engineering teams

## Usage

```
/weekly-reporter this-week
/weekly-reporter this-week --template detailed
/weekly-reporter last-week --template tech
```

## Output Example

```markdown
# Weekly Report (2026.03.03)

## Summary
- Total Tasks: 15
- Completed: 12 (80%)
- In Progress: 2
- Hours: 32

## Completed Tasks
- ✅ Task 1 - 4h
- ✅ Task 2 - 2h
...

## Next Week Plan
- Complete chat feature
- User feedback processing
```

## Technical Details

- **Language**: Python 3
- **No dependencies** required beyond standard library

