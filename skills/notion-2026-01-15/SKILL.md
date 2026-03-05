Here is the complete `SKILL.md` file updated for the January 15, 2026 API state.

```markdown
---
name: notion api 202601 15
description: Notion API updated to 2026 01 15 changes for creating, moving, and managing pages, data sources, and blocks.
homepage: https://developers.notion.com
metadata: {"clawdbot":{"emoji":"📝"}}
---

# notion

Use the Notion API to create/read/update/move pages, data sources (databases), and blocks.

## Setup

1. Create an integration at https://notion.so/my-integrations
2. Copy the API key (starts with `ntn_` or `secret_`)
3. Store it:
```bash
mkdir -p ~/.config/notion
echo "ntn_your_key_here" > ~/.config/notion/api_key

```

4. Share target pages/databases with your integration (click "..." → "Connect to" → your integration name)

## API Basics

All requests need:

```bash
NOTION_KEY=$(cat ~/.config/notion/api_key)
curl -X GET "[https://api.notion.com/v1/](https://api.notion.com/v1/)..." \
  -H "Authorization: Bearer $NOTION_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json"

```

> **Note:** The `Notion-Version` header is required. Use `2025-09-03`. The features released in Jan 2026 (Move Page, Templates) are additive and use this version header.

## Common Operations

**Search for pages and data sources:**

```bash
curl -X POST "[https://api.notion.com/v1/search](https://api.notion.com/v1/search)" \
  -H "Authorization: Bearer $NOTION_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{"query": "page title"}'

```

**Get page:**

```bash
curl "[https://api.notion.com/v1/pages/](https://api.notion.com/v1/pages/){page_id}" \
  -H "Authorization: Bearer $NOTION_KEY" \
  -H "Notion-Version: 2025-09-03"

```

**Move a page (Change Parent):**

```bash
curl -X POST "[https://api.notion.com/v1/pages/](https://api.notion.com/v1/pages/){page_id}/move" \
  -H "Authorization: Bearer $NOTION_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "parent": {"type": "page_id", "page_id": "new_parent_page_id"}
  }'

```

> *Note: To move to a database, use `{"type": "data_source_id", "data_source_id": "..."}`.*

**Create page (Standard):**

```bash
curl -X POST "[https://api.notion.com/v1/pages](https://api.notion.com/v1/pages)" \
  -H "Authorization: Bearer $NOTION_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "parent": {"database_id": "xxx"},
    "properties": {
      "Name": {"title": [{"text": {"content": "New Item"}}]},
      "Status": {"select": {"name": "Todo"}}
    }
  }'

```

**Create page from Template:**

```bash
curl -X POST "[https://api.notion.com/v1/pages](https://api.notion.com/v1/pages)" \
  -H "Authorization: Bearer $NOTION_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "parent": {"database_id": "xxx"},
    "template": {"type": "template_id", "template_id": "yyy"}
  }'

```

**List Data Source Templates:**

```bash
curl -X GET "[https://api.notion.com/v1/data_sources/](https://api.notion.com/v1/data_sources/){data_source_id}/templates" \
  -H "Authorization: Bearer $NOTION_KEY" \
  -H "Notion-Version: 2025-09-03"

```

**Update page properties:**

```bash
curl -X PATCH "[https://api.notion.com/v1/pages/](https://api.notion.com/v1/pages/){page_id}" \
  -H "Authorization: Bearer $NOTION_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "properties": {"Status": {"select": {"name": "Done"}}},
    "is_locked": true
  }'

```

**Apply Template to existing page (erasing content):**

```bash
curl -X PATCH "[https://api.notion.com/v1/pages/](https://api.notion.com/v1/pages/){page_id}" \
  -H "Authorization: Bearer $NOTION_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "template": {"type": "template_id", "template_id": "yyy"},
    "erase_content": true
  }'

```

**Query a data source (database):**

```bash
curl -X POST "[https://api.notion.com/v1/data_sources/](https://api.notion.com/v1/data_sources/){data_source_id}/query" \
  -H "Authorization: Bearer $NOTION_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "filter": {"property": "Status", "select": {"equals": "Active"}},
    "sorts": [{"property": "Date", "direction": "descending"}]
  }'

```

**Add blocks to page:**

```bash
curl -X PATCH "[https://api.notion.com/v1/blocks/](https://api.notion.com/v1/blocks/){page_id}/children" \
  -H "Authorization: Bearer $NOTION_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "children": [
      {"object": "block", "type": "paragraph", "paragraph": {"rich_text": [{"text": {"content": "Hello"}}]}}
    ]
  }'

```

## Property Types

Common property formats for database items:

* **Title:** `{"title": [{"text": {"content": "..."}}]}`
* **Rich text:** `{"rich_text": [{"text": {"content": "..."}}]}`
* **Select:** `{"select": {"name": "Option"}}`
* **Multi-select:** `{"multi_select": [{"name": "A"}, {"name": "B"}]}`
* **Date:** `{"date": {"start": "2024-01-15", "end": "2024-01-16"}}`
* **Checkbox:** `{"checkbox": true}`
* **Number:** `{"number": 42}`
* **URL:** `{"url": "https://..."}`
* **Email:** `{"email": "a@b.com"}`
* **Relation:** `{"relation": [{"id": "page_id"}]}`

## Recent Changes (Jan 2026)

* **Move Page API:** Use `/v1/pages/{id}/move` to reparent pages.
* **Templates:** New endpoints to list templates and parameters to apply them during page creation/update.
* **Locking:** `is_locked` boolean now supported in Update Page.
* **Tokens:** New tokens use `ntn_` prefix (formerly `secret_`).
* **Data Sources:** Continue using `data_source_id` for queries (introduced in 2025-09-03).

## Notes

* Page/database IDs are UUIDs (with or without dashes)
* The API cannot set database view filters — that's UI-only
* Rate limit: ~3 requests/second average
* Use `is_inline: true` when creating data sources to embed them in pages

```

```
