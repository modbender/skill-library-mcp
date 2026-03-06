---
name: milkee
description: "Complete MILKEE accounting integration for Swiss businesses. Manage projects, customers, time tracking, tasks, and products. Use when: (1) tracking billable time with start/stop timers, (2) creating/managing projects and customers, (3) recording work entries with descriptions, (4) viewing daily time summaries. Features smart fuzzy project matching."
metadata:
  openclaw:
    requires:
      env:
        - MILKEE_API_TOKEN
        - MILKEE_COMPANY_ID
---

# MILKEE Skill

Complete integration for MILKEE Swiss accounting software. Manage projects, customers, time tracking, tasks, and products.

## Features

- ⏱️ **Time Tracking** – Start/stop timers with fuzzy project matching
- 👥 **Customers** – Full CRUD operations
- 📋 **Projects** – Create, update, manage budgets
- ✅ **Tasks** – Track project tasks
- 📦 **Products** – Manage billable items

## Quick Start

### Time Tracking (Main Feature)

```bash
# Start timer (smart fuzzy match)
python3 scripts/milkee.py start_timer "Website" "Building authentication"

# Stop timer (auto-logs to MILKEE)
python3 scripts/milkee.py stop_timer

# Show today's times
python3 scripts/milkee.py list_times_today
```

### Projects

```bash
python3 scripts/milkee.py list_projects
python3 scripts/milkee.py create_project "My Project" --customer-id 123 --budget 5000
python3 scripts/milkee.py update_project 456 --name "Updated" --budget 6000
```

### Customers

```bash
python3 scripts/milkee.py list_customers

# Create with all fields
python3 scripts/milkee.py create_customer "Example AG" \
  --street "Musterstrasse 1" \
  --zip "8000" \
  --city "Zürich" \
  --phone "+41 44 123 45 67" \
  --email "info@example.ch" \
  --website "https://example.ch"

# Update specific fields
python3 scripts/milkee.py update_customer 123 --name "New Name" --phone "+41 44 999 88 77"
```

### Tasks & Products

```bash
python3 scripts/milkee.py list_tasks
python3 scripts/milkee.py create_task "Implement feature" --project-id 456

python3 scripts/milkee.py list_products
python3 scripts/milkee.py create_product "Consulting Hour" --price 150
```

## Configuration

Set environment variables:

```bash
export MILKEE_API_TOKEN="USER_ID|API_KEY"
export MILKEE_COMPANY_ID="YOUR_COMPANY_ID"
```

Or configure via your gateway config under `skills.entries.milkee.env`.

### Get Your Credentials

1. Log in to MILKEE → **Settings** → **API**
2. Copy your User ID and API Key
3. Format: `USER_ID|API_KEY`
4. Company ID is shown in Settings

## Special Features

### Fuzzy Project Matching

When you say "Website", the skill:
1. Fetches all projects from MILKEE
2. Fuzzy-matches using Levenshtein distance
3. Auto-selects the closest match
4. Starts timer on that project

### Timer Persistence

- Timer state saved to `~/.milkee_timer`
- Survives between sessions
- Auto-calculates elapsed time on stop

### Daily Summary

`list_times_today` shows:
- All time entries for today
- Duration per entry
- Total hours worked

## Technical Details

- **Language**: Python 3.8+
- **Dependencies**: None (stdlib only)
- **Timer File**: `~/.milkee_timer` (JSON)
- **API Docs**: https://apidocs.milkee.ch/api

---

**Author**: xenofex7 | **Version**: 2.0.0
