---
name: notion-workspace
description: Manage Notion workspace — search pages, read content, create pages in databases, append blocks, and list databases. Uses Notion REST API directly via urllib/requests.
license: MIT
metadata:
  author: Jack2
  version: 1.0.0
  tags: notion, productivity, notes, database
  env: NOTION_TOKEN
---

# notion-workspace Skill

Manage your Notion workspace from the CLI or as an importable Python module.

## Setup

Set your Notion integration token:
```bash
export NOTION_TOKEN=ntn_...
```

Or the default token embedded in the script will be used.

**Make sure your Notion integration has access to the pages/databases you want to use.**  
In Notion: open a page → Share → Invite your integration.

## Usage

### Search
```bash
python3 scripts/notion.py search "project notes"
python3 scripts/notion.py search "budget" --type database
```

### Read a Page
```bash
# Metadata only
python3 scripts/notion.py read PAGE_ID

# With block content
python3 scripts/notion.py read PAGE_ID --blocks
```

### Create a Page in a Database
```bash
python3 scripts/notion.py create DATABASE_ID --title "New Page Title"

# With extra properties
python3 scripts/notion.py create DATABASE_ID --title "Task" --props '{"Status": {"select": {"name": "In Progress"}}}'
```

### Append Text to a Page
```bash
python3 scripts/notion.py append PAGE_ID --text "New paragraph content"
```

### List Databases
```bash
python3 scripts/notion.py databases
```

## As a Python Module

```python
from scripts.notion import search, read_page_content, create_page, append_blocks, list_databases

# Search
results = search("meeting notes")
for item in results["results"]:
    print(item["id"], item["object"])

# Read page + blocks
data = read_page_content("PAGE_ID")
print(data["page"])
print(data["blocks"])

# Create page
page = create_page("DATABASE_ID", "My New Page")
print(page["url"])

# Append text
append_blocks("PAGE_ID", "This is a new paragraph.")

# List databases
dbs = list_databases()
```

## Files

| File | Purpose |
|------|---------|
| `scripts/notion.py` | CLI + importable module |
| `references/notion-api.md` | Notion API quick reference |

## Notes

- Uses `urllib` (stdlib only, no SDK needed)
- Notion API version: `2022-06-28`
- Rate limit: ~3 req/sec
- Page IDs can be with or without dashes (both work)
